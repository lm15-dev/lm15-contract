#!/usr/bin/env python3
"""Freeze the primary sources for the cloud-hosts design pass.

Every page is saved verbatim (HTML reduced to text; Markdown kept as-is)
next to a manifest with URL, date, HTTP status, byte count and sha256.
A page that does not answer 200 with a body is recorded as a failure
and never written; a cached copy is never overwritten by an error page.

Run from anywhere:  python3 research/cloud-hosts/sources/fetch.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (X11; Linux x86_64) lm15-contract-research/1.0"

# name -> url.  Grouped by cloud; the name is the file stem.
SOURCES: dict[str, str] = {
    # ---- AWS: credential chain -------------------------------------------
    "aws-sdkref-credential-chain": "https://docs.aws.amazon.com/sdkref/latest/guide/standardized-credentials.html",
    "aws-sdkref-login-credentials": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-login-credentials.html",
    "aws-boto3-credentials": "https://docs.aws.amazon.com/boto3/latest/guide/credentials.html",
    "aws-cli-credential-chain": "https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html",
    "aws-go-sdk-credentials": "https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/configure-gosdk.html",
    "aws-sdkref-settings-precedence": "https://docs.aws.amazon.com/sdkref/latest/guide/settings-reference.html",
    "aws-sdkref-env-vars": "https://docs.aws.amazon.com/sdkref/latest/guide/environment-variables.html",
    "aws-sdkref-config-files": "https://docs.aws.amazon.com/sdkref/latest/guide/file-format.html",
    "aws-sdkref-creds-config-files": "https://docs.aws.amazon.com/sdkref/latest/guide/creds-config-files.html",
    "aws-sdkref-static-credentials": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-static-credentials.html",
    "aws-sdkref-process-credentials": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-process-credentials.html",
    "aws-sdkref-sso-credentials": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-sso-credentials.html",
    "aws-sdkref-assume-role": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-assume-role-credentials.html",
    "aws-sdkref-container-credentials": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-container-credentials.html",
    "aws-sdkref-imds-credentials": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-imds-credentials.html",
    "aws-sdkref-region": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-region.html",
    "aws-sdkref-endpoints": "https://docs.aws.amazon.com/sdkref/latest/guide/feature-ss-endpoints.html",
    "aws-imdsv2": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html",
    "aws-sts-assume-role": "https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html",
    "aws-sts-assume-role-web-identity": "https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html",
    "aws-sso-oidc-create-token": "https://docs.aws.amazon.com/singlesignon/latest/OIDCAPIReference/API_CreateToken.html",
    "aws-sso-get-role-credentials": "https://docs.aws.amazon.com/singlesignon/latest/PortalAPIReference/API_GetRoleCredentials.html",
    # ---- AWS: signing and framing ---------------------------------------
    "aws-sigv4-create-signed-request": "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv-create-signed-request.html",
    "aws-sigv4-elements": "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv.html",
    "aws-sigv4-troubleshoot": "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv-troubleshooting.html",
    "aws-eventstream-smithy": "https://smithy.io/2.0/aws/amazon-eventstream.html",
    # ---- AWS: Bedrock ---------------------------------------------------
    "bedrock-endpoints": "https://docs.aws.amazon.com/general/latest/gr/bedrock.html",
    "bedrock-invoke-model": "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html",
    "bedrock-invoke-model-stream": "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html",
    "bedrock-converse": "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html",
    "bedrock-converse-stream": "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html",
    "bedrock-list-foundation-models": "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ListFoundationModels.html",
    "bedrock-anthropic-messages": "https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html",
    "bedrock-api-keys": "https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html",
    "bedrock-openai-chat-completions": "https://docs.aws.amazon.com/bedrock/latest/userguide/inference-chat-completions-mantle.html",
    "bedrock-inference-profiles": "https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html",
    "bedrock-model-access": "https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html",
    "bedrock-errors": "https://docs.aws.amazon.com/bedrock/latest/APIReference/CommonErrors.html",
    "bedrock-runtime-errors": "https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html#API_runtime_InvokeModel_Errors",
    "bedrock-converse-supported": "https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-supported-models-features.html",
    "anthropic-on-bedrock": "https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock.md",
    "anthropic-on-bedrock-legacy": "https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy.md",
    "anthropic-platform-on-aws": "https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws.md",
    # ---- Azure: identity --------------------------------------------------
    "azure-identity-readme": "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/README.md",
    "azure-identity-default-credential": "https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/credential-chains",
    "azure-identity-environment-credential": "https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.environmentcredential",
    "entra-client-credentials": "https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow",
    "entra-certificate-credentials": "https://learn.microsoft.com/en-us/entra/identity-platform/certificate-credentials",
    "entra-national-clouds": "https://learn.microsoft.com/en-us/entra/identity-platform/authentication-national-cloud",
    "azure-msi-vm-token": "https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/how-to-use-vm-token",
    "azure-app-service-msi": "https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity",
    "azure-aks-workload-identity": "https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview",
    "entra-workload-identity-federation": "https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation",
    "azure-cli-get-access-token": "https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-latest",
    # ---- Azure: OpenAI / Foundry ------------------------------------------
    "azure-openai-reference": "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/reference",
    "azure-openai-api-lifecycle": "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle",
    "azure-openai-managed-identity": "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/managed-identity",
    "azure-openai-responses": "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses",
    "azure-openai-rbac": "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/role-based-access-control",
    "azure-foundry-models-inference": "https://learn.microsoft.com/en-us/azure/ai-foundry/model-inference/reference/reference-model-inference-api",
    "azure-foundry-openai-v1": "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/latest",
    "azure-foundry-models-sold-directly": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure",
    "anthropic-on-foundry": "https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry.md",
    "anthropic-platforms-overview": "https://platform.claude.com/docs/en/api/overview.md",
    "azure-openai-errors": "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/quotas-limits",
    # ---- GCP: auth --------------------------------------------------------
    "gcp-adc": "https://cloud.google.com/docs/authentication/application-default-credentials",
    "gcp-adc-provide": "https://cloud.google.com/docs/authentication/provide-credentials-adc",
    "gcp-service-account-oauth": "https://developers.google.com/identity/protocols/oauth2/service-account",
    "gcp-metadata-token": "https://cloud.google.com/compute/docs/access/authenticate-workloads",
    "gcp-metadata-querying": "https://cloud.google.com/compute/docs/metadata/querying-metadata",
    "gcp-sts-token": "https://cloud.google.com/iam/docs/reference/sts/rest/v1/TopLevel/token",
    "gcp-wif-other-clouds": "https://cloud.google.com/iam/docs/workload-identity-federation-with-other-clouds",
    "gcp-impersonation-generate-token": "https://cloud.google.com/iam/docs/reference/credentials/rest/v1/projects.serviceAccounts/generateAccessToken",
    "gcp-gcloud-print-access-token": "https://cloud.google.com/sdk/gcloud/reference/auth/print-access-token",
    "gcp-gcloud-adc-login": "https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login",
    "gcp-token-refresh": "https://developers.google.com/identity/protocols/oauth2/web-server",
    "gcp-google-auth-user-guide": "https://googleapis.dev/python/google-auth/latest/user-guide.html",
    "gcp-gcloud-create-cred-config": "https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools/create-cred-config",
    "gcp-google-auth-default-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/auth/_default.py",
    "gcp-google-auth-external-account-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/auth/external_account.py",
    "gcp-google-auth-identity-pool-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/auth/identity_pool.py",
    "gcp-google-auth-aws-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/auth/aws.py",
    "gcp-google-auth-impersonated-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/auth/impersonated_credentials.py",
    "gcp-google-auth-compute-engine-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/auth/compute_engine/_metadata.py",
    "aws-botocore-credentials-py": "https://raw.githubusercontent.com/boto/botocore/develop/botocore/credentials.py",
    "aws-botocore-utils-py": "https://raw.githubusercontent.com/boto/botocore/develop/botocore/utils.py",
    "aws-botocore-auth-py": "https://raw.githubusercontent.com/boto/botocore/develop/botocore/auth.py",
    "aws-botocore-eventstream-py": "https://raw.githubusercontent.com/boto/botocore/develop/botocore/eventstream.py",
    "azure-identity-default-py": "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/azure/identity/_credentials/default.py",
    "azure-identity-environment-py": "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/azure/identity/_credentials/environment.py",
    "azure-identity-managed-identity-py": "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/azure/identity/_credentials/managed_identity.py",
    "azure-identity-workload-py": "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/azure/identity/_credentials/workload_identity.py",
    "azure-identity-azure-cli-py": "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/azure/identity/_credentials/azure_cli.py",
    "azure-identity-certificate-py": "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/azure/identity/_credentials/certificate.py",
    "gcp-google-auth-environment-vars-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/auth/environment_vars.py",
    "gcp-google-auth-oauth2-credentials-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/oauth2/credentials.py",
    "gcp-google-auth-service-account-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/oauth2/service_account.py",
    "gcp-google-auth-jwt-py": "https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/auth/jwt.py",
    "azure-msal-assertion-py": "https://raw.githubusercontent.com/AzureAD/microsoft-authentication-library-for-python/dev/msal/oauth2cli/assertion.py",
    "gcp-api-keys": "https://cloud.google.com/docs/authentication/api-keys-use",
    # ---- GCP: Vertex ------------------------------------------------------
    "vertex-inference": "https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference",
    "vertex-locations": "https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations",
    "vertex-express-mode": "https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview",
    "vertex-claude": "https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude",
    "vertex-openai-compat": "https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/call-gemini-using-openai-library",

    "vertex-context-cache": "https://cloud.google.com/vertex-ai/generative-ai/docs/context-cache/context-cache-create",
    "vertex-batch": "https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/batch-prediction-gemini",
    "vertex-list-models": "https://cloud.google.com/vertex-ai/docs/reference/rest/v1/publishers.models/list",
    "vertex-errors": "https://cloud.google.com/vertex-ai/docs/general/troubleshooting",
    "anthropic-on-vertex": "https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai.md",
}


# AWS SigV4 test suite (vendored verbatim in botocore): the harness vectors.
# The complete suite (D15, verify/DECISIONS-2026-09-06.md): every case
# directory's .req/.creq/.sts/.authz, flat under aws-sigv4-suite/ (leaf
# names are unique across the nested normalize-path/ and post-sts-token/
# groups), plus the suite's LICENSE, NOTICE and the two group readmes.
# botocore's default branch is `develop` (there is no `main`).
_SIGV4_BASE = "https://raw.githubusercontent.com/boto/botocore/develop/tests/unit/auth/aws4_testsuite"
SIGV4_CASES = (
    "get-header-key-duplicate", "get-header-value-multiline", "get-header-value-order",
    "get-header-value-trim", "get-unreserved", "get-utf8", "get-vanilla-empty-query-key",
    "get-vanilla-query-order-encoded", "get-vanilla-query-order-key-case",
    "get-vanilla-query-order-key", "get-vanilla-query-order-value", "get-vanilla-query-unreserved",
    "get-vanilla-query", "get-vanilla-utf8-query", "get-vanilla-with-session-token", "get-vanilla",
    "normalize-path/get-relative-relative", "normalize-path/get-relative",
    "normalize-path/get-slash-dot-slash", "normalize-path/get-slash-pointless-dot",
    "normalize-path/get-slash", "normalize-path/get-slashes", "normalize-path/get-space",
    "normalize-path/get-special-character",
    "post-header-key-case", "post-header-key-sort", "post-header-value-case",
    "post-sts-token/post-sts-header-after", "post-sts-token/post-sts-header-before",
    "post-vanilla-empty-query-value", "post-vanilla-query", "post-vanilla",
    "post-x-www-form-urlencoded-parameters", "post-x-www-form-urlencoded",
)
for _case in SIGV4_CASES:
    _leaf = _case.rsplit("/", 1)[-1]
    for _ext in ("req", "creq", "sts", "authz"):
        SOURCES[f"aws-sigv4-suite/{_leaf}.{_ext}"] = f"{_SIGV4_BASE}/{_case}/{_leaf}.{_ext}"
for _doc in ("LICENSE", "NOTICE", "normalize-path/normalize-path.txt", "post-sts-token/readme.txt"):
    SOURCES[f"aws-sigv4-suite/{_doc.rsplit('/', 1)[-1]}"] = f"{_SIGV4_BASE}/{_doc}"


def html_to_text(raw: str) -> str:
    m = re.search(r"<main.*?</main>", raw, re.S) or re.search(r"<article.*?</article>", raw, re.S)
    text = m.group(0) if m else raw
    text = re.sub(r"<script.*?</script>", "", text, flags=re.S)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</(p|div|h\d|li|tr|pre|table|thead|tbody|section|dd|dt)>", "\n", text)
    text = re.sub(r"</t[dh]>", "\t", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip() + "\n"


def fetch(url: str) -> tuple[str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/markdown, text/html;q=0.9, */*;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return str(r.status), r.read()
    except urllib.error.HTTPError as e:
        return str(e.code), b""
    except Exception as e:  # noqa: BLE001 - transport failure is a finding
        return f"000 {type(e).__name__}", b""


def main() -> int:
    today = dt.date.today().isoformat()
    only = set(sys.argv[2:]) if len(sys.argv) > 2 and sys.argv[1] == "--only" else None
    previous = {}
    previous_date = today
    if only and (HERE / "manifest.json").exists():
        manifest = json.loads((HERE / "manifest.json").read_text())
        previous = {e["name"]: e for e in manifest["entries"]}
        previous_date = manifest.get("date", today)
    entries = []
    failures = 0
    for name, url in SOURCES.items():
        if only and name not in only and name in previous:
            # Kept as fetched: the per-entry date is the manifest date of the
            # run that fetched it (entries before 2026-09-07 carried none).
            entries.append({**previous[name], "fetched": previous[name].get("fetched", previous_date)})
            continue
        status, body = fetch(url)
        entry = {"name": name, "url": url, "status": status, "bytes": len(body), "used": False, "fetched": today}
        if status == "200" and body:
            is_md = url.endswith(".md") or "raw.githubusercontent.com" in url
            (HERE / name).parent.mkdir(parents=True, exist_ok=True)
            text = body.decode("utf-8", "replace")
            out = text if is_md else html_to_text(text)
            path = HERE / (name if "/" in name else f"{name}.md")
            path.write_text(out, encoding="utf-8")
            entry.update(used=True, sha256=hashlib.sha256(body).hexdigest(),
                         saved_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         saved=f"sources/{path.name if '/' not in name else name}", lines=out.count("\n"))
            print(f"  {name} ... {entry['lines']} lines")
        else:
            failures += 1
            print(f"  {name} ... FAILED ({status}) {url}", file=sys.stderr)
        entries.append(entry)
    (HERE / "manifest.json").write_text(json.dumps({"date": today, "entries": entries}, indent=1) + "\n")
    print(f"---\n{len(entries) - failures} saved, {failures} failed -> manifest.json")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
