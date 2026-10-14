# shellcheck shell=bash disable=SC2034
# Where things live on a workshop pod. Sourced by every pod-side script, so the layout is defined once.
#
# Measured on a Runpod pod (docs/GPU-POOL.md): the persistent volume mounted at /workspace is a
# network FUSE filesystem on which chmod is ignored, chown fails and permissions are not enforced:
# any user can read, change or delete anything there, including files that root created with mode 0600.
# Therefore:
#   * /workspace is only a DOWNLOAD CACHE for model files (it survives pod restarts, so a rebuilt pod
#     does not download 30 GB again). Nothing secret and nothing root executes or loads is stored there.
#   * Everything that needs real permissions lives on the container disk: code, models actually
#     served, accounts and keys, caches that contain compiled code, logs, and participants' homes.
#     The container disk is wiped on a pod restart; `infra/deploy-to-pod.sh` rebuilds it, with
#     accounts recreated from the trainer's infra/participants.yaml, which stays the source of truth.

WS_PERSIST=${WS_PERSIST:-/workspace}            # network volume: download cache only
WS_PERSIST_HF=$WS_PERSIST/hf-cache              # model files kept across restarts

WS_OPT=${WS_OPT:-/opt/workshop}                 # root-owned, not writable by participants
WS_REPO=$WS_OPT/repo                            # the trusted copy of this repository
WS_HF=$WS_OPT/hf                                # HF_HOME of the servers (read-only for participants)
WS_MON=$WS_OPT/monitoring                       # Prometheus and Grafana binaries, config and data

WS_STATE=${WS_STATE:-/var/lib/workshop}         # accounts, public keys, API key, provenance (root-owned)
WS_LOGS=${WS_LOGS:-/var/log/workshop}           # server, monitoring and audit logs
WS_CACHE=${WS_CACHE:-/var/cache/workshop}       # vLLM / torch compile caches (contain generated code)
WS_BACKUPS=${WS_BACKUPS:-/var/backups/workshop} # archives of replaced homes and removed accounts
WS_LIB=/usr/local/lib/workshop                  # installed helper scripts
WS_HOMES=/home                                  # participant home directories
