"""Mint an Amazon Bedrock short-term API key ("bearer token") from AWS
credentials — the algorithm of AWS's own `aws-bedrock-token-generator`
(research/cloud-hosts/sources/bedrock-api-keys.md:10-40; generator source
1.1.0: a SigV4 *query* presign of `POST https://bedrock.amazonaws.com/
?Action=CallWithBearerToken`, service `bedrock`, 12 h, then
`"bedrock-api-key-" + base64(url-without-scheme + "&Version=1")`).

Research tool only.  lm15 itself does not need to mint: with AWS
credentials it signs each request directly (SigV4).  The key exists for
callers that only speak bearer; here it lets the capture exercise the
bearer rung of the aws-chain without anyone pasting a key.

Pinned against the official generator with the AWS test pair at a fixed
clock (both vectors in `_VECTORS`; `python3 _aws_bearer.py --selftest`).
Never prints a minted key.

    python3 research/providers/_aws_bearer.py --write ~/.config/lm15/aws-bearer.env
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sys
import tempfile
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

HOST = "bedrock.amazonaws.com"
SERVICE = "bedrock"
PREFIX = "bedrock-api-key-"
EXPIRES = 43200  # 12 h, the generator's constant


def mint(access_key_id: str, secret_access_key: str, session_token: str | None, region: str, now: datetime) -> str:
    now = now.astimezone(timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date = now.strftime("%Y%m%d")
    scope = f"{date}/{region}/{SERVICE}/aws4_request"
    params = [
        ("Action", "CallWithBearerToken"),
        ("X-Amz-Algorithm", "AWS4-HMAC-SHA256"),
        ("X-Amz-Credential", f"{access_key_id}/{scope}"),
        ("X-Amz-Date", amz_date),
        ("X-Amz-Expires", str(EXPIRES)),
        ("X-Amz-SignedHeaders", "host"),
    ]
    if session_token:
        params.append(("X-Amz-Security-Token", session_token))
    enc = lambda s: urllib.parse.quote(s, safe="-_.~")  # noqa: E731
    query = "&".join(f"{enc(k)}={enc(v)}" for k, v in params)  # botocore's URL order
    canonical_query = "&".join(f"{enc(k)}={enc(v)}" for k, v in sorted(params))
    canonical = "\n".join(["POST", "/", canonical_query, f"host:{HOST}\n", "host", hashlib.sha256(b"").hexdigest()])
    string_to_sign = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical.encode()).hexdigest()])
    key = ("AWS4" + secret_access_key).encode()
    for piece in (date, region, SERVICE, "aws4_request"):
        key = hmac.new(key, piece.encode(), hashlib.sha256).digest()
    signature = hmac.new(key, string_to_sign.encode(), hashlib.sha256).hexdigest()
    presigned = f"{HOST}/?{query}&X-Amz-Signature={signature}&Version=1"
    return PREFIX + base64.b64encode(presigned.encode()).decode()


# Official aws-bedrock-token-generator 1.1.0 output, AWS test pair, clock 2026-09-04T12:00:00Z, us-east-1.
_VECTORS = [
    (("AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY", None),
     "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSURFWEFNUExFJTJGMjAyNjA5MDQlMkZ1cy1lYXN0LTElMkZiZWRyb2NrJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA5MDRUMTIwMDAwWiZYLUFtei1FeHBpcmVzPTQzMjAwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZYLUFtei1TaWduYXR1cmU9MDU0ODg3NDcyZTVhMzg1MTllNDU0MWM4MGFiOTdhZDZmM2ZjMTAzZmRjNDg2OGYwZjI2ZWFhNWQwMWViZDY3NSZWZXJzaW9uPTE="),
    (("AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY", "SESSIONTOKEN"),
     "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSURFWEFNUExFJTJGMjAyNjA5MDQlMkZ1cy1lYXN0LTElMkZiZWRyb2NrJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA5MDRUMTIwMDAwWiZYLUFtei1FeHBpcmVzPTQzMjAwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZYLUFtei1TZWN1cml0eS1Ub2tlbj1TRVNTSU9OVE9LRU4mWC1BbXotU2lnbmF0dXJlPWY1MGVjMDA4YTkwOGUyNzU4YTc2NzhkMjUyNDliMmZlZWRhMWEzMDM4YTAwYzEwYjhiYWVkNzQ0Zjk1YWExNTcmVmVyc2lvbj0x"),
]


def selftest() -> None:
    fixed = datetime(2026, 9, 4, 12, 0, 0, tzinfo=timezone.utc)
    for (ak, sk, st), want in _VECTORS:
        got = mint(ak, sk, st, "us-east-1", fixed)
        assert got == want, f"mismatch for session_token={st!r}"
    print("ok: 2/2 vectors match aws-bedrock-token-generator 1.1.0")


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        selftest()
        return 0
    if "--write" not in argv:
        print(__doc__)
        return 2
    out = Path(argv[argv.index("--write") + 1]).expanduser()
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".." / "lm15-python"))
    from lm15.cloud.chains import ChainContext, resolve
    from lm15.credentials import AwsCredentials
    from lm15.registry import lookup

    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
    env = {k: v for k, v in os.environ.items() if k != "AWS_BEARER_TOKEN_BEDROCK"}  # mint from keys, not from a key
    cred = resolve(lookup("bedrock-chat").access, ChainContext.online(env=env, settings={"region": region}))
    if not isinstance(cred, AwsCredentials):
        sys.exit(f"the aws-chain yielded {cred.kind}, not AWS credentials; nothing to mint from")
    token = mint(cred.access_key_id, cred.secret_access_key, cred.session_token, region, datetime.now(timezone.utc))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.parent.chmod(0o700)
    # A replacement is mode 600 even when the old path was world-readable,
    # and never follows an existing symlink to another credential file.
    fd, temporary = tempfile.mkstemp(prefix=".bedrock-token-", dir=out.parent)
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(f"AWS_BEARER_TOKEN_BEDROCK={token}\nAWS_BEARER_TOKEN_REGION={region}\n")
        os.replace(temporary, out)
    finally:
        Path(temporary).unlink(missing_ok=True)
    print(f"wrote {out} (mode 600; key id {cred.access_key_id[:4]}…, region {region}, valid 12 h from now)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
