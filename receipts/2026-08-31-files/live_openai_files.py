import os
from lm15.providers import OpenAILM
from lm15.types import FileUploadRequest
from lm15.errors import ProviderError

lm = OpenAILM(api_key=os.environ["OPENAI_API_KEY"])
info = lm.file_upload(FileUploadRequest(filename="lm15-magic.pdf", path="/tmp/lm15-magic.pdf", media_type="application/pdf"))
print("uploaded:", info.id, "| readiness:", info.readiness, "| size:", info.size_bytes)
info = lm.file_wait_ready(info.id)
print("wait_ready ->", info.readiness)
print("file_get:", lm.file_get(info.id).filename)
page = lm.file_list(limit=100)
print("file_list:", len(page.items), "items | ours present:", any(f.id == info.id for f in page.items))
try:
    lm.file_download(info.id)
    print("download: UNEXPECTEDLY SUCCEEDED")
except ProviderError as exc:
    print(f"download refused (typed): {type(exc).__name__}: {str(exc)[:70]}")
lm.file_delete(info.id)
print("deleted")
try:
    lm.file_get(info.id)
except ProviderError as exc:
    print(f"get-after-delete (typed): {type(exc).__name__}")
