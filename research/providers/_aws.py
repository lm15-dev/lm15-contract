"""Shared bits for the AWS doors' captures: the region and the fixture rule.

Credentials come from lm15's own aws-chain (the machine's profile, env,
SSO…) — never from a .env in a repo; every case is re-signed with the
fixed test pair for the fixture (research/providers/_capture.py aws_fixture).
"""
from __future__ import annotations

import os

REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
