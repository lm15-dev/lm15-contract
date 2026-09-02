"""Live end-to-end proof of the files lifecycle with the shipped lm15 code."""
import os, sys, traceback

from lm15.providers import AnthropicLM, GeminiLM, OpenAILM
from lm15.types import DocumentPart, FileUploadRequest, Message, Request
from lm15.errors import ProviderError

PDF = "/tmp/lm15-magic.pdf"

def prove(name, lm, model):
    print(f"\n=== {name} ===")
    # 1. upload (path-backed: proves the lazy path read)
    info = lm.file_upload(FileUploadRequest(filename="lm15-magic.pdf", path=PDF, media_type="application/pdf"))
    print("uploaded:", info.id)
    print("  filename:", info.filename, "| media_type:", info.media_type, "| size:", info.size_bytes)
    print("  created:", info.created_at, "| expires:", info.expires_at)
    print("  readiness:", info.readiness, "| downloadable:", info.downloadable)
    # 2. wait_ready
    info = lm.file_wait_ready(info.id, poll_every=2.0, timeout=120)
    print("wait_ready ->", info.readiness)
    # 3. the loop that matters: file_id into a chat request
    resp = lm.complete(Request(model=model, messages=(
        Message(role="user", parts=(
            DocumentPart(media_type="application/pdf", file_id=info.id),
        )),
        Message(role="user", parts=()) if False else Message.user("What is the magic word in the attached document? Answer with exactly one word."),
    )))
    print("chat answer:", resp.text.strip())
    # 4. get
    again = lm.file_get(info.id)
    print("file_get:", again.id == info.id, "| readiness:", again.readiness)
    # 5. list — the queue remembers
    page = lm.file_list(limit=10)
    print("file_list:", len(page.items), "items | ours present:", any(f.id == info.id for f in page.items), "| cursor:", bool(page.next_cursor))
    # 6. download — expect a typed provider refusal for user uploads
    try:
        lm.file_download(info.id)
        print("download: UNEXPECTEDLY SUCCEEDED")
    except ProviderError as exc:
        print(f"download refused (typed): {type(exc).__name__}: {str(exc)[:80]}")
    # 7. delete, then prove it is gone
    lm.file_delete(info.id)
    print("deleted")
    try:
        lm.file_get(info.id)
        print("get-after-delete: UNEXPECTEDLY SUCCEEDED")
    except ProviderError as exc:
        print(f"get-after-delete (typed): {type(exc).__name__}")

results = {}
for name, lm, model in [
    ("anthropic", AnthropicLM(api_key=os.environ["ANTHROPIC_API_KEY"]), "claude-haiku-4-5-20251001"),
    ("openai", OpenAILM(api_key=os.environ["OPENAI_API_KEY"]), "gpt-5-nano"),
    ("gemini", GeminiLM(api_key=os.environ["GEMINI_API_KEY"]), "gemini-2.5-flash"),
]:
    try:
        prove(name, lm, model)
        results[name] = "OK"
    except Exception as exc:
        traceback.print_exc()
        results[name] = f"FAIL: {exc}"
print("\n=== summary ===")
for k, v in results.items():
    print(f"{k}: {v}")
sys.exit(0 if all(v == "OK" for v in results.values()) else 1)
