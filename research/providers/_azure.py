"""Shared bits for the three Azure doors' captures: the lab env file, the
Entra bearer probes, and the Azure-side settings a case pins.

The lab is provisioned by research/cloud-hosts/azure/provision.sh into
~/.config/lm15/azure-lab.env; capture entry points explicitly load that
external state for live runs only. Existing environment values win.
Imports, --help and --dry-run do not load lab state.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

LAB_ENV = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "lm15" / "azure-lab.env"


def load_lab_env() -> None:
    if not LAB_ENV.exists():
        return
    for line in LAB_ENV.read_text().splitlines():
        if line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def entra_token(scope: str, *, dry_run: bool = False) -> str | None:
    """A bearer token for ``scope`` from `az` (the signed-in user), None when
    `az` is missing or not logged in.  Used only by probes."""
    if dry_run:
        return "dry-run-entra-token"
    for argv in (["az"], ["nix", "run", "nixpkgs#azure-cli", "--"]):
        try:
            out = subprocess.run(argv + ["account", "get-access-token", "--output", "tsv", "--query", "accessToken", "--scope", scope],
                                 capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    return None


SCOPES = ("https://ai.azure.com/.default", "https://cognitiveservices.azure.com/.default")


def service_principal_token(policy, kind: str, *, dry_run: bool = False):
    """A BearerToken for the lab's service principal through lm15's own
    ``azure-chain`` (no `az`): ``kind`` is ``"secret"`` or ``"certificate"``.
    The env handed to the chain carries ONLY the principal's variables, so
    the api-key and CLI rungs cannot win.  None when the lab env lacks them."""
    from lm15.cloud.chains import ChainContext, resolve
    from lm15.credentials import BearerToken

    if dry_run:
        return BearerToken("dry-run-principal-token")
    keep = {"AZURE_TENANT_ID", "AZURE_CLIENT_ID"}
    keep.add("AZURE_CLIENT_SECRET" if kind == "secret" else "AZURE_CLIENT_CERTIFICATE_PATH")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    if len(env) < 3:
        return None
    env["PATH"] = ""  # no az / azd on the path: the chain must stop at the environment rung
    return resolve(policy, ChainContext.online(env=env))
