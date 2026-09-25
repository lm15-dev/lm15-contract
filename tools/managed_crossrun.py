#!/usr/bin/env python3
"""Mixed-language runs on one managed store file (AUTH-26 level 2, sequential).

Each scenario is a list of legs; each leg is one `managed_run` (PROTOCOL.md)
against the SAME store file, so a login one SDK saves is read, renewed,
replaced or signed out by another. Every scenario runs once with every leg in
the reference SDK, and once per rotation of the SDKs under test across its
legs; the normalized outcomes (steps, trace, store) must be identical.

    python3 tools/managed_crossrun.py python typescript rust go

Then the lock (AUTH-4, AUTH-20.4), concurrently: two SDKs, as two
processes, find the same xAI token due at the same moment. The first to take
the lock renews against a server that answers slowly; the other must wait on
the lock, re-read, and use the fresh token — exactly one refresh request
between them, whichever language wins. Every ordered pair is run.
"""

from __future__ import annotations

import json
import threading
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))

import check  # noqa: E402
import managed  # noqa: E402

S = "PRIVATE-MANAGED-TOKEN"
T0 = 1790000000000


def ok(body, status=200):
    return {"status": status, "json": body}


XAI_LOGIN = [
    ok({"device_code": f"{S}-device", "user_code": "WXYZ-1234", "verification_uri": "https://accounts.x.ai/device", "interval": 5, "expires_in": 600}),
    ok({"access_token": f"{S}-access-1", "refresh_token": f"{S}-refresh-1", "expires_in": 3600}),
]

SCENARIOS = [
    {
        "id": "login-read-renew-logout",
        "legs": [
            {"clock_ms": T0, "http": XAI_LOGIN, "steps": [{"do": "login", "provider": "xai", "method": "device"}]},
            {"clock_ms": T0 + 60_000, "steps": [{"do": "status", "provider": "xai"}, {"do": "request_auth", "provider": "xai"}, {"do": "connections"}]},
            {"clock_ms": T0 + 3_400_000, "http": [ok({"access_token": f"{S}-access-2", "refresh_token": f"{S}-refresh-2", "expires_in": 3600})],
             "steps": [{"do": "request_auth", "provider": "xai"}, {"do": "status", "provider": "xai"}]},
            {"clock_ms": T0 + 3_500_000, "steps": [{"do": "request_auth", "provider": "xai"}, {"do": "logout", "target": "xai"}]},
            {"clock_ms": T0 + 3_600_000, "env": {"XAI_API_KEY": f"{S}-ambient"},
             "steps": [{"do": "status", "provider": "xai"}, {"do": "request_auth", "provider": "xai"}, {"do": "explain", "provider": "xai"}]},
        ],
    },
    {
        "id": "keys-replace-and-stale-logout",
        "legs": [
            {"clock_ms": T0, "steps": [{"do": "set_api_key", "provider": "openai", "key": f"{S}-key-1"},
                                       {"do": "configure", "provider": "gemini", "method": "env", "answers": {"name": "GEMINI_API_KEY"}}]},
            {"clock_ms": T0 + 1000, "steps": [{"do": "connections"}, {"do": "set_api_key", "provider": "openai", "key": f"{S}-key-2", "replace": "cn_"}]},
            {"clock_ms": T0 + 2000, "env": {"GEMINI_API_KEY": f"{S}-gemini"},
             "steps": [{"do": "request_auth", "provider": "gemini"}, {"do": "request_auth", "provider": "openai"}, {"do": "logout", "target": "gemini"}]},
            {"clock_ms": T0 + 3000, "steps": [{"do": "connections"}, {"do": "status", "provider": "gemini"}]},
        ],
    },
    {
        "id": "interrupted-renewal-is-seen-everywhere",
        "legs": [
            {"clock_ms": T0, "http": XAI_LOGIN, "steps": [{"do": "login", "provider": "xai", "method": "device"}]},
            {"clock_ms": T0 + 3_400_000, "http": [{"network": "timeout"}], "steps": [{"do": "request_auth", "provider": "xai"}]},
            {"clock_ms": T0 + 3_500_000, "steps": [{"do": "status", "provider": "xai"}, {"do": "request_auth", "provider": "xai"}]},
            {"clock_ms": T0 + 3_600_000, "http": XAI_LOGIN,
             "steps": [{"do": "connections"}, {"do": "login", "provider": "xai", "method": "device", "replace": "cn_"}]},
        ],
    },
]


def current_id(store_path: Path, provider: str) -> str | None:
    try:
        doc = json.loads(store_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return ((doc.get("_lm15") or {}).get("slots") or {}).get(provider, {}).get("connection_id")


def run(scenario: dict, shims: list, tmp: Path) -> list[dict]:
    home = Path(tempfile.mkdtemp(prefix="home-", dir=tmp))
    store = home / ".config" / "lm15" / "credentials.json"
    store.parent.mkdir(parents=True)
    outcomes = []
    for leg, shim in zip(scenario["legs"], shims):
        steps = []
        for step in leg["steps"]:
            step = dict(step)
            if step.get("replace") == "cn_":  # the id saved by an earlier leg, whoever wrote it
                step["replace"] = current_id(store, step["provider"])
            steps.append(step)
        env = {**leg.get("env", {}), "HOME": str(home), "LM15_CREDENTIALS_PATH": str(store)}
        reply = shim.call("managed_run", store_path=str(store), home=str(home), env=env, clock_ms=leg["clock_ms"],
                          sentinel=S, http=leg.get("http", []), ui=leg.get("ui", []), steps=steps)
        if not reply.get("ok"):
            raise RuntimeError(f"{shim.name}: {reply.get('error')}")
        problem = managed.secrecy_violation(reply["result"], S)
        if problem:
            raise RuntimeError(f"{shim.name}: {problem}")
        outcomes.append(reply["result"])
    # One normalization over the whole scenario: ids keep their identity across legs.
    merged = managed.normalize({"steps": [o["steps"] for o in outcomes], "events": [o["events"] for o in outcomes],
                                "store": [o["store"] for o in outcomes]})
    return merged


def race(first, second, tmp: Path) -> str | None:
    """Both renew one due token at once; returns a reason when the lock failed."""
    home = Path(tempfile.mkdtemp(prefix="home-", dir=tmp))
    store = home / ".config" / "lm15" / "credentials.json"
    store.parent.mkdir(parents=True)
    store.write_text(json.dumps({"xai": {"type": "oauth", "access": f"{S}-old", "refresh": f"{S}-refresh-0",
                                         "expires": T0 + 100_000, "issued_at": T0 - 3_500_000, "lifetime_s": 3600.0}}), encoding="utf-8")
    replies: dict[str, dict] = {}

    def leg(shim, key: str, delay: int) -> None:
        refresh = {"status": 200, "json": {"access_token": f"{S}-new-{key}", "refresh_token": f"{S}-refresh-{key}", "expires_in": 3600},
                   "delay_ms": delay}
        replies[key] = shim.call("managed_run", store_path=str(store), home=str(home),
                                 env={"HOME": str(home), "LM15_CREDENTIALS_PATH": str(store)}, clock_ms=T0, sentinel=S,
                                 http=[refresh], ui=[], steps=[{"do": "request_auth", "provider": "xai"}])

    threads = [threading.Thread(target=leg, args=(first, "a", 1500)), threading.Thread(target=leg, args=(second, "b", 1500))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    sent = 0
    tokens = set()
    for key, reply in replies.items():
        if not reply.get("ok"):
            return f"{key}: {reply.get('error')}"
        result = reply["result"]
        sent += sum(1 for e in result["events"] if "http" in e)
        step = result["steps"][0]
        if not step.get("ok"):
            return f"{key}: request_auth failed: {step.get('error')}"
        tokens.add(step["value"]["credential"]["value"])
    if sent != 1:
        return f"{sent} refresh requests were sent; the lock let both renew" if sent > 1 else "nobody renewed"
    if len(tokens) != 1 or f"{S}-old" in tokens:
        return f"the two processes used different or stale tokens: {sorted(t.rsplit('-', 1)[-1] for t in tokens)}"
    return None


def main(argv: list[str]) -> int:
    names = argv or ["python", "typescript"]
    reference = check.load_shim("python")
    shims = {name: check.load_shim(name) for name in names if name != "python"}
    shims["python"] = reference
    failures = 0
    try:
        with tempfile.TemporaryDirectory(prefix="lm15-crossrun-") as tmp_name:
            tmp = Path(tmp_name)
            for scenario in SCENARIOS:
                legs = len(scenario["legs"])
                expected = run(scenario, [reference] * legs, tmp)
                order = [shims[n] for n in names]
                rotations = {tuple(order[(i + k) % len(order)] for i in range(legs)) for k in range(len(order))}
                for combo in sorted(rotations, key=lambda c: [s.name for s in c]):
                    label = " → ".join(s.name for s in combo)
                    actual = run(scenario, list(combo), tmp)
                    diff = check.first_difference(expected, actual)
                    if diff is None:
                        print(f"  pass  {scenario['id']}: {label}")
                    else:
                        failures += 1
                        print(f"  FAIL  {scenario['id']}: {label}: {diff.path}: {json.dumps(diff.expected)[:200]} != {json.dumps(diff.actual)[:200]}")
            for first_name in names:
                for second_name in names:
                    # Two processes: a second instance when both legs are the same language.
                    second = shims[second_name] if second_name != first_name else check.load_shim(second_name)
                    reason = race(shims[first_name], second, tmp)
                    if second is not shims[second_name]:
                        second.close()
                    if reason is None:
                        print(f"  pass  concurrent renewal: {first_name} ∥ {second_name}")
                    else:
                        failures += 1
                        print(f"  FAIL  concurrent renewal: {first_name} ∥ {second_name}: {reason}")
    finally:
        for shim in {id(s): s for s in shims.values()}.values():
            shim.close()
    print(f"managed crossrun: {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
