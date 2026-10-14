# syntax=docker/dockerfile:1
#
# The workshop's vLLM server as a container image.
#
#   docker build -f deploy/vllm/Dockerfile -t ki-ohne-cloud/vllm:local .
#   docker run --rm --gpus all --ipc=host \
#     -e PROFILE=baseline -e VLLM_API_KEY="$VLLM_API_KEY" \
#     -v "$HOME/.cache/huggingface:/models" -p 127.0.0.1:8000:8000 ki-ohne-cloud/vllm:local
#
# What is pinned, what is deliberately not baked in:
#   pinned     the base image by DIGEST (a tag can be re-pushed), the profiles and the renderer
#   not baked  model weights. They come from a mounted cache at the revision pinned in
#              config/models.yaml, so the image stays small (about 9 GB compressed) and a model
#              change does not need a rebuild. Offline mode makes a missing model fail fast.
# Reproducibility also needs: the host driver (CUDA 13 images need R580 or newer), the revision
# of the model files, and the profile name. `docker run` alone records none of them.

# vllm/vllm-openai:v0.31.0 (multi-arch manifest list), observed 2026-10-14. Keep in sync with infra/versions.env.
ARG VLLM_IMAGE=vllm/vllm-openai@sha256:c1c9f6fd5c109ba7f0546a59f5b2f15fb87f64c77782e90a27b648b42a8e67c3
FROM ${VLLM_IMAGE}

LABEL org.opencontainers.image.title="KI ohne Cloud: vLLM server" \
      org.opencontainers.image.description="vLLM v0.31.0 with workshop profiles" \
      org.opencontainers.image.licenses="MIT"

# Telemetry off, models only from the mounted cache.
ENV HF_HOME=/models \
    HF_HUB_OFFLINE=1 \
    VLLM_NO_USAGE_STATS=1 \
    DO_NOT_TRACK=1

COPY config/vllm-profiles/ /opt/workshop/profiles/
COPY infra/pod/render-profile.py /opt/workshop/render-profile.py
COPY deploy/vllm/entrypoint.sh /opt/workshop/entrypoint.sh

# Model loading and CUDA graph capture take minutes: give the health check a long start period.
HEALTHCHECK --interval=30s --timeout=5s --start-period=900s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

EXPOSE 8000
ENTRYPOINT ["/opt/workshop/entrypoint.sh"]
