#!/usr/bin/env python3
"""Record which managed-login and inference endpoints a web page may call directly.

Writes the ``cors_probe`` section of ``auth/managed/browser.json`` and leaves its
``receipts`` untouched. For every endpoint a browser flow would touch, it sends
what a page would send, carrying ``Origin: https://lm15.dev``:

- a CORS preflight (``OPTIONS`` with ``Access-Control-Request-Method`` and
  ``-Headers``) when a browser would send one: a JSON body or any header outside
  the CORS safelist;
- then the request itself, with a deliberately **invalid, harmless** payload
  (unknown client, bad refresh token, malformed JSON, no credential), and reads
  ``Access-Control-Allow-Origin`` on the reply.

What this is and is not (spec/auth-managed.md AUTH-22): it emulates the CORS
exchange from a server, so it shows what the provider's headers allow. It is
**not** a browser receipt. A real page can still fail where this passes (a
forbidden header such as User-Agent, bot protection that treats browsers
differently, a cookie requirement) and a page receipt is recorded separately,
in ``receipts``, by the person who ran it.

No credential is read or sent. No request can create an account resource: every
payload is rejected by the provider before it would (checked 2026-09-24; one
OpenAI device endpoint accepted an unknown client id, so it gets malformed JSON).

Usage: python3 tools/probe_auth_cors.py [--origin URL] [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "auth/managed/profiles.json"
OUT = ROOT / "auth/managed/browser.json"

FORM = "application/x-www-form-urlencoded"
JSON = "application/json"
# Fetch spec CORS-safelisted request headers (values within limits) and content types.
SAFELISTED = {"accept", "accept-language", "content-language", "content-type"}
SIMPLE_TYPES = {FORM, "multipart/form-data", "text/plain"}

# (id, provider, method-in-profiles or None, request key or None, stage, http method, url,
#  content type or None, harmless body or None, extra request headers)
PROBES = [
    ("xai.device_authorization", "xai", "device", "device_authorization", "authorization", "POST",
     "https://auth.x.ai/oauth2/device/code", FORM, "client_id=", {}),
    ("xai.device_token", "xai", "device", "device_token", "authorization", "POST",
     "https://auth.x.ai/oauth2/token", FORM,
     "grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code&client_id=b1a00492-073a-47ea-816f-4c329264a828&device_code=invalid", {}),
    ("xai.renewal", "xai", "device", "renewal", "renewal", "POST",
     "https://auth.x.ai/oauth2/token", FORM,
     "grant_type=refresh_token&client_id=b1a00492-073a-47ea-816f-4c329264a828&refresh_token=invalid", {}),
    ("xai.models", "xai", None, None, "catalog", "GET", "https://api.x.ai/v1/models", None, None,
     {"Authorization": "Bearer invalid"}),
    ("xai.inference", "xai", None, None, "inference", "POST", "https://api.x.ai/v1/chat/completions", JSON, "{}",
     {"Authorization": "Bearer invalid"}),

    ("claude-code.token", "claude-code", "browser", "token", "authorization", "POST",
     "https://platform.claude.com/v1/oauth/token", JSON,
     '{"grant_type":"refresh_token","client_id":"9d1c250a-e61b-44d9-88ed-5944d1962f5e","refresh_token":"invalid"}', {}),
    ("claude-code.inference", "claude-code", None, None, "inference", "POST", "https://api.anthropic.com/v1/messages", JSON, "{}",
     {"Authorization": "Bearer invalid", "anthropic-version": "2023-06-01",
      "anthropic-beta": "claude-code-20250219,oauth-2025-04-20", "x-app": "cli",
      "anthropic-dangerous-direct-browser-access": "true"}),
    ("claude-code.models", "claude-code", None, None, "catalog", "GET", "https://api.anthropic.com/v1/models", None, None,
     {"Authorization": "Bearer invalid", "anthropic-version": "2023-06-01",
      "anthropic-beta": "oauth-2025-04-20", "anthropic-dangerous-direct-browser-access": "true"}),

    ("openai-codex.token", "openai-codex", "browser", "token", "authorization", "POST",
     "https://auth.openai.com/oauth/token", FORM,
     "grant_type=refresh_token&client_id=app_EMoamEEZ73f0CkXaXp7hrann&refresh_token=invalid", {}),
    ("openai-codex.device_authorization", "openai-codex", "device", "device_authorization", "authorization", "POST",
     "https://auth.openai.com/api/accounts/deviceauth/usercode", JSON, "{", {}),
    ("openai-codex.device_token", "openai-codex", "device", "device_token", "authorization", "POST",
     "https://auth.openai.com/api/accounts/deviceauth/token", JSON, "{", {}),
    ("openai-codex.inference", "openai-codex", None, None, "inference", "POST",
     "https://chatgpt.com/backend-api/codex/responses", JSON, "{}",
     {"Authorization": "Bearer invalid", "chatgpt-account-id": "invalid", "OpenAI-Beta": "responses=experimental", "originator": "lm15"}),
    ("openai-codex.models", "openai-codex", None, None, "catalog", "GET",
     "https://chatgpt.com/backend-api/codex/models?client_version=0.147.0", None, None,
     {"Authorization": "Bearer invalid", "chatgpt-account-id": "invalid", "originator": "lm15"}),

    ("github-copilot.device_authorization", "github-copilot", "device", None, "authorization", "POST",
     "https://github.com/login/device/code", FORM, "client_id=invalid&scope=read%3Auser", {}),
    ("github-copilot.device_token", "github-copilot", "device", None, "authorization", "POST",
     "https://github.com/login/oauth/access_token", FORM,
     "client_id=Iv1.b507a08c87ecfe98&device_code=invalid&grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code", {}),
    ("github-copilot.copilot_token", "github-copilot", "device", None, "renewal", "GET",
     "https://api.github.com/copilot_internal/v2/token", None, None,
     {"Authorization": "Bearer invalid", "Editor-Version": "vscode/1.107.0",
      "Editor-Plugin-Version": "copilot-chat/0.35.0", "Copilot-Integration-Id": "vscode-chat"}),
    ("github-copilot.copilot_token_minimal", "github-copilot", "device", None, "renewal", "GET",
     "https://api.github.com/copilot_internal/v2/token", None, None,
     {"Authorization": "Bearer invalid", "Copilot-Integration-Id": "vscode-chat"}),
    ("github-copilot.inference", "github-copilot", None, None, "inference", "POST",
     "https://api.individual.githubcopilot.com/chat/completions", JSON, "{}",
     {"Authorization": "Bearer invalid", "Editor-Version": "vscode/1.107.0",
      "Editor-Plugin-Version": "copilot-chat/0.35.0", "Copilot-Integration-Id": "vscode-chat"}),
    ("github-copilot.models", "github-copilot", None, None, "catalog", "GET",
     "https://api.individual.githubcopilot.com/models", None, None,
     {"Authorization": "Bearer invalid", "Editor-Version": "vscode/1.107.0",
      "Editor-Plugin-Version": "copilot-chat/0.35.0", "Copilot-Integration-Id": "vscode-chat"}),

    ("openrouter.token", "openrouter", "browser", "token", "authorization", "POST",
     "https://openrouter.ai/api/v1/auth/keys", JSON,
     '{"code":"invalid","code_verifier":"invalid","code_challenge_method":"S256"}', {}),
    ("openrouter.models", "openrouter", None, None, "catalog", "GET", "https://openrouter.ai/api/v1/models/user", None, None,
     {"Authorization": "Bearer invalid"}),
    ("openrouter.inference", "openrouter", None, None, "inference", "POST",
     "https://openrouter.ai/api/v1/chat/completions", JSON, "{}", {"Authorization": "Bearer invalid"}),

    ("kimi-code.device_authorization", "kimi-code", "device", None, "authorization", "POST",
     "https://auth.kimi.com/api/oauth/device_authorization", FORM, "client_id=invalid", {}),
    ("kimi-code.device_token", "kimi-code", "device", None, "authorization", "POST",
     "https://auth.kimi.com/api/oauth/token", FORM,
     "client_id=17e5f671-d194-4dfb-9706-5516cb48c098&device_code=invalid&grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code", {}),
    ("kimi-code.renewal", "kimi-code", "device", None, "renewal", "POST",
     "https://auth.kimi.com/api/oauth/token", FORM,
     "client_id=17e5f671-d194-4dfb-9706-5516cb48c098&grant_type=refresh_token&refresh_token=invalid", {}),
    ("kimi-code.inference", "kimi-code", None, None, "inference", "POST",
     "https://api.kimi.com/coding/v1/messages", JSON, "{}",
     {"Authorization": "Bearer invalid", "anthropic-version": "2023-06-01"}),

    ("meta.device_authorization", "meta", "device", "device_authorization", "authorization", "POST",
     "https://auth.meta.com/oidc/device/authorization/", FORM, "client_id=invalid", {}),
    ("meta.device_token", "meta", "device", "device_token", "authorization", "POST",
     "https://auth.meta.com/oidc/device/token/", FORM,
     "grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code&device_code=invalid&client_id=1031625952748946", {}),
    ("meta.key_mint", "meta", "device", "key_mint", "authorization", "POST",
     "https://api.meta.ai/muse-code/key", JSON, "{}", {"Authorization": "Bearer invalid", "x-api-version": "1.0.0"}),
    ("meta.inference", "meta", None, None, "inference", "POST", "https://api.meta.ai/v1/responses", JSON, "{}",
     {"Authorization": "Bearer invalid"}),
]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # a browser fetch in CORS mode would not follow cross-origin either
        return None


OPENER = urllib.request.build_opener(_NoRedirect())


def _send(method: str, url: str, headers: dict[str, str], body: bytes | None):
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with OPENER.open(request, timeout=20) as response:
            return response.status, {k.lower(): v for k, v in response.headers.items()}
    except urllib.error.HTTPError as exc:
        headers_out = {k.lower(): v for k, v in (exc.headers or {}).items()}
        exc.close()
        return exc.code, headers_out
    except (urllib.error.URLError, OSError) as exc:
        return None, {"error": type(exc).__name__}


def _origin_ok(allow: str | None, origin: str) -> bool:
    return allow is not None and allow.strip() in ("*", origin)


def _headers_ok(allowed: str | None, requested: list[str]) -> bool:
    if not requested:
        return True
    if allowed is None:
        return False
    names = {h.strip().lower() for h in allowed.split(",")}
    return "*" in names or all(h in names for h in requested)


def probe(entry, origin: str) -> dict:
    pid, provider, method_id, request_key, stage, http_method, url, ctype, body, extra = entry
    custom = sorted(h.lower() for h in extra if h.lower() not in SAFELISTED)
    preflighted = bool(custom) or (ctype is not None and ctype not in SIMPLE_TYPES) or http_method not in ("GET", "HEAD", "POST")
    requested = sorted(set(custom + (["content-type"] if ctype and ctype not in SIMPLE_TYPES else [])))
    ident = {"User-Agent": "lm15-contract-cors-probe/1", "Origin": origin, "Accept": "application/json"}
    result: dict = {"id": pid, "provider": provider, "stage": stage, "method": http_method, "url": url,
                    "request": "preflighted" if preflighted else "simple"}
    if requested:
        result["requested_headers"] = requested
    if preflighted:
        status, headers = _send("OPTIONS", url, {**ident, "Access-Control-Request-Method": http_method,
                                                 **({"Access-Control-Request-Headers": ",".join(requested)} if requested else {})}, None)
        allow_origin = headers.get("access-control-allow-origin")
        ok = status is not None and 200 <= status < 300 and _origin_ok(allow_origin, origin) \
            and _headers_ok(headers.get("access-control-allow-headers"), requested)
        result["preflight"] = {"status": status, "allow_origin": allow_origin,
                               "allow_headers": headers.get("access-control-allow-headers"), "passes": ok}
    send_headers = {**ident, **extra, **({"Content-Type": ctype} if ctype else {})}
    status, headers = _send(http_method, url, send_headers, body.encode() if body is not None else None)
    allow_origin = headers.get("access-control-allow-origin")
    result["actual"] = {"status": status, "allow_origin": allow_origin,
                        "content_type": (headers.get("content-type") or "").split(";")[0] or None,
                        "security_challenge": headers.get("cf-mitigated", "").lower() == "challenge"}
    readable = _origin_ok(allow_origin, origin)
    if preflighted and not result["preflight"]["passes"]:
        verdict = "relay"
    elif readable:
        verdict = "direct"
    elif status is None or result["actual"]["security_challenge"] or (status == 429):
        verdict = "unclear"
    else:
        verdict = "relay"
    result["verdict"] = verdict
    return result


def check_against_profiles(profiles: dict) -> None:
    """A probe that names a profile request must probe that exact URL."""
    for pid, provider, method_id, request_key, *_rest in PROBES:
        if request_key is None:
            continue
        url = _rest[2]
        request = profiles["providers"][provider]["methods"][method_id]["requests"][request_key]
        if request.get("url") != url:
            raise SystemExit(f"{pid}: probe URL {url} differs from profiles.json {request.get('url')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--origin", default="https://lm15.dev")
    parser.add_argument("--dry-run", action="store_true", help="probe and print; do not write browser.json")
    args = parser.parse_args()
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
    check_against_profiles(profiles)
    results = [probe(entry, args.origin) for entry in PROBES]
    existing = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    document = {
        "version": 1,
        "provenance": {"source": "live-capture", "date": _dt.date.today().isoformat(),
                       "evidence": "cors_probe: tools/probe_auth_cors.py run against the live endpoints (server-side CORS emulation); "
                                   "receipts: each entry names its own evidence; changes/2026-09-24-managed-auth-profiles-and-browser-track.md §5"},
        "about": existing.get("about") or (
            "Browser evidence for managed login (spec/auth-managed.md AUTH-22: a native pass is not a browser pass). "
            "cors_probe is regenerated by tools/probe_auth_cors.py: a server-side emulation of the CORS exchange a page "
            "at the given origin would make, with harmless invalid payloads. Its verdict says what the provider's "
            "headers allow (direct = a page may read the reply; relay = the browser would refuse it; unclear = rate "
            "limit, challenge or network error). It is not a receipt. receipts holds what a person observed in a real "
            "browser page, redacted, one entry per provider, method and stage. live_verdicts overrides a probe verdict where a real "
            "page proved otherwise (live behavior outranks headers)."),
        "cors_probe": {
            "date": _dt.date.today().isoformat(),
            "origin": args.origin,
            "tool": "tools/probe_auth_cors.py",
            "platform_limits": [
                "A page cannot set User-Agent (Chromium drops it; the Fetch spec no longer forbids it but browsers differ). "
                "A profile whose provider requires a specific User-Agent needs a relay to send it.",
                "fetch() from a page never follows a cross-origin redirect in CORS mode without CORS on every hop.",
                "Cookies are not sent (credentials: 'omit'); no flow in profiles.json needs them.",
            ],
            "results": results,
        },
        "live_verdicts": existing.get("live_verdicts", {}),
        "tunnel_notes": existing.get("tunnel_notes", {}),
        "receipts": existing.get("receipts", []),
    }
    text = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    if args.dry_run:
        sys.stdout.write(text)
    else:
        OUT.write_text(text, encoding="utf-8")
    width = max(len(r["id"]) for r in results)
    for r in results:
        pre = r.get("preflight", {})
        print(f"{r['id']:<{width}}  {r['verdict']:<7} {r['request']:<11} "
              f"pre={pre.get('status', '-')!s:<4} act={r['actual']['status']!s:<4} acao={r['actual']['allow_origin']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
