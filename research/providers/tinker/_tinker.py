"""Tinker capture plumbing shared by the survey and capture scripts.

``TinkerCapture`` is ``_capture.Capture`` with one more redaction: Tinker's
error bodies name the account (`organization: "<email> - default org"
tml:organization:<uuid>`) and its catalog names the owner
(`tml:organization_user:<uuid>`). Neither is a credential, but neither
belongs in a public corpus, so both are replaced before anything is written.
A checkpoint path's run id is kept: it is useless without the key, and the
cases must pin the exact model string the server answered to.

Model roles (live 2026-11-09, `get_server_capabilities` and `/models`):

- ``CHECKPOINTS``: untrained LoRA sampler checkpoints made for these captures
  on the maintainer's account (2026-11-09, `user_metadata.purpose` "lm15
  contract captures", no expiry; ~0.37 GB together, about $0.04 a month).
  An untrained LoRA answers as its base model; what matters here is that the
  server resolves the checkpoint's base and applies that family's rules.
  (The first survey used a FunctAI checkpoint that was deleted mid-run:
  `probe-reasoning-anthropic-checkpoint-*` 404 "Weights not found".)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import Capture  # noqa: E402

HOST = "tinker.thinkingmachines.dev"
ENV = "TINKER_API_KEY"
_RUN = "tinker://e68146d2-1a2e-56e8-b42f-1f5957705501"
CHECKPOINTS = {
    "Qwen/Qwen3.5-4B": f"{_RUN}:train:0/sampler_weights/lm15-untrained",       # LoRA rank 8
    "openai/gpt-oss-20b": f"{_RUN}:train:1/sampler_weights/lm15-untrained",    # rank 1
    "thinkingmachines/Inkling-Small": f"{_RUN}:train:2/sampler_weights/lm15-untrained",  # rank 1
}
CHECKPOINT = CHECKPOINTS["Qwen/Qwen3.5-4B"]
# The FunctAI checkpoint of the first survey run (deleted during it).
GONE = "tinker://3447f8c5-f502-54e9-a030-6259fee3f875:train:0/sampler_weights/best-step-000000"

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_URN = re.compile(r"tml:(organization_user|organization|project|user):[0-9a-f-]{36}")


class TinkerCapture(Capture):
    def redact(self, text: str) -> str:
        text = super().redact(text)
        text = _EMAIL.sub("<redacted-email>", text)
        return _URN.sub(lambda m: f"tml:{m.group(1)}:<redacted>", text)


def capture(provider: str = "tinker", *, change_slug: str = "tinker-live", default_model: str = "Qwen/Qwen3.5-4B") -> TinkerCapture:
    return TinkerCapture(provider, env_var=ENV, default_model=default_model, host=HOST, change_slug=change_slug)
