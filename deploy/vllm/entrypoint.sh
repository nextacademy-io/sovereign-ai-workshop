#!/usr/bin/env bash
# Container entrypoint: render a workshop profile, then become `vllm serve`.
#   docker run ... -e PROFILE=fp8 -e VLLM_API_KEY=... <image>
# Extra `--set key=value` arguments are passed through to the renderer (allowlisted keys only).
set -euo pipefail

profile="${PROFILE:-baseline}"
python3 /opt/workshop/render-profile.py "$profile" --dir /opt/workshop/profiles --container \
  --out /tmp/active.yaml "$@" >/tmp/active.json
cat /tmp/active.json

: "${VLLM_API_KEY:?set VLLM_API_KEY: the server refuses to start without an API key}"
exec vllm serve --config /tmp/active.yaml
