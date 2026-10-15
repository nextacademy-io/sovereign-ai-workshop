# Task 00 — Preflight

## Goal

Arrive at the first module with a laptop that can reach your group's GPU machine, so that no workshop time is spent on setup.

## Context

You do not need a GPU or a cloud account. The trainer provides one GPU machine per group; you connect over SSH with your own key. This task checks your tools and your key, and, once you have received your access details, your login.

## Scope

Done means the preflight ends with `0 failed` and your login test prints the GPU name. Out of scope: downloading models, starting servers or reading the course material in advance.

## Starting Point

A laptop with `git`, `ssh`, `docker`, `python3` (3.11 or newer) and `curl`, and about 20 GB of free disk. No model download is needed.

## Instructions

1. Clone the repository and run the preflight:

   ```bash
   git clone https://github.com/nextacademy-io/sovereign-ai-workshop.git ki-ohne-cloud
   cd ki-ohne-cloud
   ./scripts/preflight.sh
   ```

2. Fix every line that says `FAIL`. A `WARN` about Docker means the daemon is not running: start Docker Desktop.
3. If you have no SSH key, the preflight prints the command to create one. Send the trainer **one line**: the content of your `.pub` file. Never send the file without `.pub`.
4. When the trainer sends you a host, a port and a user name, test your login:

   ```bash
   ./scripts/preflight.sh --host <host> --port <port> --user <your-user>
   ```

## Expected Result

The preflight ends with `0 failed`, and the login test prints the GPU of your group's machine (an NVIDIA RTX PRO 6000 Blackwell Server Edition with about 96 GB of memory).

## Validation

- `./scripts/preflight.sh` exits with status 0.
- `ssh -p <port> <your-user>@<host> 'nvidia-smi --query-gpu=name --format=csv,noheader'` prints the GPU name without asking for a password.

## If You Get Stuck

| Symptom | Fix |
| --- | --- |
| `python3` too old | Install Python 3.11 or newer (for example with `uv` or your package manager). |
| Docker daemon not running | Start Docker Desktop and wait until it reports running. |
| `Permission denied (publickey)` | Wrong user name or port, or the trainer has not added your key yet. Check both and tell the trainer. |
| `Connection refused` | The port changes when a machine is rebuilt. Ask for the current port. |

More in [`docs/SETUP.md`](../docs/SETUP.md) and [`docs/TROUBLESHOOTING.md`](../docs/TROUBLESHOOTING.md).

## Further Exploration

- Open an SSH tunnel to the dashboard and the API: `ssh -p <port> -L 3000:127.0.0.1:3000 -L 8000:127.0.0.1:8000 <your-user>@<host>`, then browse to `http://127.0.0.1:3000`.
- Read `docs/SETUP.md` section 3 and explain why the server is not reachable without the tunnel.
