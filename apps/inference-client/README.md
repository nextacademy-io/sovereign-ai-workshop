# inference-client

Small clients for an OpenAI-compatible endpoint (the workshop's shared vLLM server). Python with the `openai` package; no framework. On a workshop machine the environment is already set (`OPENAI_BASE_URL`, `OPENAI_API_KEY`, `WORKSHOP_MODEL`); on your laptop use an SSH tunnel (`docs/SETUP.md` section 3).

| Script | What it shows | Example |
| --- | --- | --- |
| `chat.py` | A streamed chat request; the last line prints prompt tokens, time to first token, completion tokens and decode speed | `python3 apps/inference-client/chat.py "Explain batching in one paragraph."` |
| `structured.py` | JSON that must match a schema (constrained decoding); name the fields in the prompt as well | `python3 apps/inference-client/structured.py "My parcel never arrived and I was charged twice."` |
| `batch_extract.py` | Offline document processing with bounded concurrency and a throughput report (workshop scenario D in miniature) | `python3 apps/inference-client/batch_extract.py --docs 48 --concurrency 16` |

`chat.py` options: `--max-tokens`, `--temperature`, `--system`, `--think` (Qwen3 thinking mode, off by default so that speed measurements are about the answer). In the validation sessions `batch_extract.py` processed about 7.7 documents per second at concurrency 16 and 13 at concurrency 32 on one GPU (96 synthetic documents of about 1,300 tokens, schema-constrained output of at most five items per list, zero invalid replies); a first version that asked for "every" item and allowed 200 output tokens had 43 of 48 replies cut off mid-list.

## Container

`Dockerfile` builds a CPU-only image of these clients for the Day 3 exercise (non-root user, base image pinned by digest, Python packages pinned in `requirements.txt`, about 72 MB). The commands are in its header; it runs on your laptop against the tunnel.

```bash
docker build -f apps/inference-client/Dockerfile -t ki-ohne-cloud/client:local .
docker run --rm -e OPENAI_API_KEY="$OPENAI_API_KEY" ki-ohne-cloud/client:local "Say hello in German."
```
