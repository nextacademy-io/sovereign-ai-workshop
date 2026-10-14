# syntax=docker/dockerfile:1
#
# CPU-only client image for the Day 3 containerization exercise (runs on participants' laptops).
#
#   docker build -f apps/inference-client/Dockerfile -t ki-ohne-cloud/client:local .
#   ssh -L 8000:127.0.0.1:8000 <your-user>@<gpu-host> -p <port>        # in another terminal
#   docker run --rm -e OPENAI_API_KEY="$OPENAI_API_KEY" ki-ohne-cloud/client:local "Say hello in German."
#
# The client only needs the network: the model runs on the GPU host, behind your SSH tunnel.
# On Docker Desktop (macOS, Windows) `host.docker.internal` reaches the tunnel on your laptop.
# On Linux add `--add-host host.docker.internal:host-gateway` and bind the tunnel to the docker
# bridge address (ssh -L 172.17.0.1:8000:127.0.0.1:8000 ...) instead of all interfaces.
#
# Pinned: base image by digest (python:3.12-slim, observed 2026-10-14) and Python packages by version.

FROM python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

# Dependencies first: this layer is cached until requirements.txt changes.
COPY apps/inference-client/requirements.txt apps/inference-client/requirements.txt
RUN pip install -r apps/inference-client/requirements.txt

COPY apps/common.py apps/common.py
COPY apps/inference-client apps/inference-client
COPY benchmark/infbench benchmark/infbench

# Do not run as root.
RUN useradd --create-home --uid 10001 app
USER app

ENV OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
    WORKSHOP_MODEL=Qwen/Qwen3-8B

ENTRYPOINT ["python", "apps/inference-client/chat.py"]
