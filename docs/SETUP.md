# Participant setup

What to do before the workshop and how to connect on the day. You do **not** need a GPU, a cloud account or a model download: the trainer provides one GPU machine per group and you connect to it over SSH.

## 1. Before the workshop (15 minutes)

You need: `git`, `ssh`, `docker`, `python3` (3.11 or newer), `curl`, about 20 GB of free disk for Docker images, and an SSH key.

```bash
git clone <repository-url> ki-ohne-cloud
cd ki-ohne-cloud
./scripts/preflight.sh
```

The preflight checks your tools and your SSH key. It downloads nothing and changes nothing. Fix every `FAIL`; a `WARN` for Docker means the daemon is not running (start Docker Desktop before Day 3).

### Your SSH key

If the preflight says you have no key:

```bash
ssh-keygen -t ed25519 -C "your.name@workshop"
```

Send the trainer **one line**: the content of `~/.ssh/id_ed25519.pub`. That is your *public* key and is safe to share. Never send the file without `.pub`: it is your private key.

### Your access

The trainer replies with a host, a port and your user name, for example `gpu-01.example.org`, `22290`, `anna`. Test it:

```bash
./scripts/preflight.sh --host <host> --port <port> --user <your-user>
```

It prints the GPU of your group's machine if the login works. If it fails: check the user name and the port (the port changes if the trainer rebuilds the machine), then tell the trainer.

## 2. Connecting on the day

```bash
ssh -p <port> <your-user>@<host>
```

After the login you are in your own home directory with your own copy of this repository (`~/ki-ohne-cloud`). Everything the labs need is already in your environment:

| Variable | Value |
| --- | --- |
| `OPENAI_BASE_URL` | `http://127.0.0.1:8000/v1`, your group's shared vLLM server |
| `OPENAI_API_KEY` | the group's API key |
| `WORKSHOP_MODEL` | the model name the server answers to |
| `EMBEDDING_BASE_URL` | `http://127.0.0.1:8001/v1`, for the RAG demo |

Try it:

```bash
curl -s -H "Authorization: Bearer $OPENAI_API_KEY" $OPENAI_BASE_URL/models
python3 apps/inference-client/chat.py "What is a KV cache? One sentence."
./scripts/gpu-status.sh
```

### The server is shared by your group

Your group's model server is a single process that every member uses. That is on purpose: you will see queueing, batching and contention first-hand. It also means:

- `sudo wsctl status` shows what runs. `sudo wsctl profiles` lists the configurations you may start.
- `./scripts/start-vllm.sh <profile>` **restarts the server for everyone in your group** and takes one to three minutes. Tell your group first. If a new profile fails to start, the previous one is restored automatically.
- Start only what the labs ask for. Do not start your own copy of a model: the GPU memory belongs to the shared server.

## 3. Using the API and the dashboard from your laptop

You can run the example apps on your laptop against the group's server, and open Grafana in your browser, through an SSH tunnel:

```bash
ssh -p <port> -L 8000:127.0.0.1:8000 -L 3000:127.0.0.1:3000 <your-user>@<host>
```

Leave that terminal open. In another terminal:

```bash
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY=$(ssh -p <port> <your-user>@<host> 'cat /var/lib/workshop/api-key')
```

Grafana is then at `http://127.0.0.1:3000` (the dashboard *KI ohne Cloud: inference*). Nothing is exposed publicly: the server answers only on the machine's own loopback address, and the tunnel is the only way in.

## 4. If something breaks

| Symptom | What to do |
| --- | --- |
| `Permission denied (publickey)` | Wrong user name or port, or your key was not added. Check with the trainer. |
| `Connection refused` | The port changed after a rebuild. Ask for the new port. |
| `401 Unauthorized` from the API | Missing or old key. Log in again (the key is set at login). |
| The model does not answer | `sudo wsctl status`. If the server is stopped, `sudo wsctl start baseline`. Give it up to three minutes. |
| You changed files and want a clean start | Ask the trainer to run the reset for you, or run `./scripts/reset.sh lab-NN` for the lab you are on. Your workshop artifacts are kept. |
| Something else | See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md). |

## 5. What you will keep

Your work lives in `~/ki-ohne-cloud/workshop-artifacts/` and `benchmark/results/mine/`. **Copy it to your laptop at the end of every day**:

```bash
scp -P <port> -r <your-user>@<host>:ki-ohne-cloud/workshop-artifacts ./my-artifacts
```

The machines are deleted after the workshop and your access ends with them.
