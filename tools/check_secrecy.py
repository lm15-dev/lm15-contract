#!/usr/bin/env python3
"""Enforce the secrecy invariant (spec/auth.md AUTH-5) across the corpus.

Two independent checks:

1. Sentinel discipline. The planted sentinel ``SECRET-SENTINEL-DO-NOT-PRINT``
   may appear in fixture *inputs* (``env``, ``borrowed_file``, ``body``,
   ``key``/credential value positions) but never inside any ``expect`` /
   ``expected`` block — an expectation containing the sentinel would pin a
   secret-leaking rendering as correct.

2. Live-secret scan. No file in the corpus may contain material matching
   known credential shapes (Anthropic/OpenAI/Google/GitHub key prefixes,
   Slack tokens, AWS access key ids). Captured bodies are verbatim by rule,
   so a hit here means a capture leaked a real credential and must be
   re-captured with the credential revoked.

Exit non-zero on any violation.

Usage: check_secrecy.py [--root DIR]   (default: the repo containing this script)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SENTINEL = "SECRET-SENTINEL-DO-NOT-PRINT"
EXPECTATION_KEYS = {"expect", "expected", "expect_lm15"}

# Deliberately specific prefixes: broad entropy heuristics drown reviewers
# in false positives, which teaches them to ignore the gate.
LIVE_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("anthropic api key", re.compile(r"sk-ant-(?:api|oat|ort)[0-9a-zA-Z]*-[A-Za-z0-9_-]{16,}")),
    ("openai api key", re.compile(r"sk-(?:proj|svcacct)-[A-Za-z0-9_-]{20,}")),
    ("google api key", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("github token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    # AWS's own documentation ids end in EXAMPLE (AKIAIOSFODNN7EXAMPLE,
    # AKIAI44QH8DHBEXAMPLE); they appear verbatim in frozen research sources
    # (research/cloud-hosts/sources/, 2026-09-03) and are not material.
    ("aws access key id", re.compile(r"\b(?!(?:AKIAIOSFODNN7EXAMPLE|AKIAI44QH8DHBEXAMPLE)\b)(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    # platform.deepseek.com keys: "sk-" + exactly 32 lowercase hex (observed
    # shape 2026-09-03); the exact length keeps it from matching prose.
    ("deepseek api key", re.compile(r"\bsk-[0-9a-f]{32}\b")),
    # z.ai keys: 32 hex, a dot, 16 alphanumerics (observed shape 2026-09-03).
    ("z.ai api key", re.compile(r"\b[0-9a-f]{32}\.[A-Za-z0-9]{16}\b")),
    # platform.kimi.ai keys: "sk-" + exactly 48 mixed-case alphanumerics
    # (observed shape 2026-09-03); the exact length keeps it from prose.
    ("moonshot api key", re.compile(r"\bsk-[A-Za-z0-9]{48}\b")),
    # dev.meta.ai keys: authentication.md documents "LLM|<numeric team id>|
    # <secret>" (example LLM|607358788850350|nx9.....LJY); a key issued
    # 2026-09-03 is LLM_<15 digits>_<27 alphanumerics>.  Both separators;
    # the 16-char floor keeps the docs' 11-char example from matching.
    ("meta model api key", re.compile(r"\bLLM[|_]\d{6,}[|_][A-Za-z0-9._-]{16,}")),
    # Cloud hosts (changes/2026-09-03-cloud-hosts.md, AUTH-5): any PEM
    # private key block; the AWS test-suite pair (AKIDEXAMPLE) is not
    # AKIA-shaped and is expected in fixtures.
    ("pem private key", re.compile(r"-----BEGIN (?:RSA |EC |ENCRYPTED |)PRIVATE KEY-----")),
    # AWS secret access key: 40 chars of base64 alphabet right after the
    # `aws_secret_access_key` / AWS_SECRET_ACCESS_KEY setting, excluding the
    # two documented example secrets (…EXAMPLEKEY).
    ("aws secret access key", re.compile(r"(?i)aws_secret_access_key\W{1,4}(?![A-Za-z0-9/+]{30}EXAMPLEKEY\b)[A-Za-z0-9/+]{40}\b")),
    # Google OAuth access tokens.
    ("google access token", re.compile(r"\bya29\.[0-9A-Za-z_-]{30,}")),
    # Amazon Bedrock short-term API keys (first capture 2026-09-04): the
    # base64 of a SigV4 presigned CallWithBearerToken URL. Only the frozen
    # test-vector file is exempt, not arbitrary tokens with a test-id prefix
    # (which could still contain a real session token).
    ("bedrock api key", re.compile(r"bedrock-api-key-[A-Za-z0-9+/]{120,}={0,2}")),
    # Azure OpenAI / Foundry key shapes are added at first live capture
    # (as deepseek and z.ai were), never from memory: a guessed 84-char
    # pattern matched base64 image payloads on 2026-09-03 and was removed.
    # Signed JWTs (three base64url segments, header starting {"alg").  A
    # JWT is a bearer-equivalent for its lifetime (AUTH-5).  Fixture JWTs
    # signed with the corpus test key live only under auth/token-vectors.json.
    ("signed jwt", re.compile(r"\beyJ[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{20,}\b")),
)

# The one place a private key may live: the corpus test key (AUTH-11), and
# the one place a signed JWT may live: token vectors signed with that key.
PATH_ALLOWLIST: dict[str, frozenset[str]] = {
    "auth/test-keys/rsa-2048-test-only.pem": frozenset({"pem private key"}),
    "auth/token-vectors.json": frozenset({"signed jwt"}),
    "research/providers/_aws_bearer.py": frozenset({"bedrock api key"}),
    # Google's own documentation examples, frozen verbatim (research sources
    # are never edited): a sample ya29 token and a sample RS256 JWT.
    "research/cloud-hosts/sources/aws-sts-assume-role.md": frozenset({"aws access key id"}),
    "research/cloud-hosts/sources/gcp-metadata-token.md": frozenset({"google access token"}),
    "research/cloud-hosts/sources/gcp-service-account-oauth.md": frozenset({"signed jwt"}),
}

# Pin reviewed content as well as its path: replacing a test key or adding
# a live JWT at an exempt path must fail. Refresh these only after review
# of the changed test material, never to silence a new secret finding.
ALLOWLIST_SHA256 = {
    "auth/test-keys/rsa-2048-test-only.pem": "6e3e52ed07726dfd0d08091e1560ceffbb45cc92a01caea9980bd77fac6f942f",
    "auth/token-vectors.json": "a826e661c0489ece0f5e3560f0ba52708da00ca94cb0f100514e50ad59d81950",
    "research/providers/_aws_bearer.py": "da773e1a03e6a2d74da75bbfc0ce46177682c6d7a1f1c1324373200d6c7499d1",
    "research/cloud-hosts/sources/aws-sts-assume-role.md": "de00601cf1c5c813f6ca4fad2f6067f6ed10c81923ffc644b82cdfdcdb85f607",
    "research/cloud-hosts/sources/gcp-metadata-token.md": "3982907f85cd097a6c8a611015617737458f5fa08807fdde3a58158ed1e49a80",
    "research/cloud-hosts/sources/gcp-service-account-oauth.md": "65500ac616ef4e1089fc8aba161e8bb748d93f47563852d347b7a8323884fa76",
}

SCANNED_SUFFIXES = {".json", ".jsonl", ".txt", ".md", ".sse", ".pem", ".py", ".sh",
                    ".req", ".creq", ".sts", ".authz"}
SKIPPED_PARTS = {".git", "__pycache__", "node_modules"}


def sentinel_in_expectations(node: object, in_expectation: bool, where: str, problems: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            sentinel_in_expectations(
                value, in_expectation or key in EXPECTATION_KEYS, f"{where}.{key}", problems
            )
    elif isinstance(node, list):
        for index, value in enumerate(node):
            sentinel_in_expectations(value, in_expectation, f"{where}[{index}]", problems)
    elif isinstance(node, str) and in_expectation and SENTINEL in node:
        problems.append(f"{where}: sentinel inside an expectation block")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    root: Path = args.root

    problems: list[str] = []
    scanned = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        if any(part in SKIPPED_PARTS for part in path.parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        relative = str(path.relative_to(root))
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8", errors="replace")
        except OSError as exc:
            problems.append(f"{relative}: unreadable ({exc})")
            continue
        scanned += 1

        allowed = (PATH_ALLOWLIST.get(relative, frozenset())
                   if hashlib.sha256(raw).hexdigest() == ALLOWLIST_SHA256.get(relative)
                   else frozenset())
        for label, pattern in LIVE_SECRET_PATTERNS:
            if label in allowed:
                continue
            match = pattern.search(text)
            if match:
                # Never echo the secret itself; name the shape and location.
                line = text.count("\n", 0, match.start()) + 1
                problems.append(f"{relative}:{line}: material matching {label}")

        if path.suffix == ".json" and SENTINEL in text:
            try:
                data = json.loads(text)
            except ValueError:
                continue  # unreadable JSON is check_provenance's problem
            sentinel_in_expectations(data, False, relative, problems)

    if scanned == 0:
        print(f"check_secrecy: nothing to scan under {root}", file=sys.stderr)
        return 2

    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"check_secrecy: {len(problems)} violation(s) across {scanned} file(s)")
        return 1

    print(f"check_secrecy: OK ({scanned} file(s) scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
