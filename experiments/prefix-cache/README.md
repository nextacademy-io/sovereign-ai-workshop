# Experiment: prefix-cache

## Question

How much prefill does a long shared prefix save, and when does the cache not help?

## Hypothesis (a prediction to test, not a result)

With a long shared system prompt or document, prefix caching removes most of the prefill work after the first request: time to first token drops sharply and the hit rate approaches the shared fraction. With prompts that share nothing it changes nothing. Turning it off makes every request pay full prefill.

## What changes, what stays the same

Prefix caching on against off, with 2,000 of 2,200 prompt tokens shared by all requests; control: 2,200 unique tokens with caching on.

## Run it

```bash
# on the trainer's laptop: runs on the pod, copies results to benchmark/results/<date>-rtxpro6000-<label>/
experiments/run-session.sh --host <ip> --port <port> --label <label> prefix-cache
```

`experiments/runner.py` restarts the shared server with the profiles below, runs the benchmark harness with fresh prompts
at every level, and stores each result with its hardware, model revision, engine version, server arguments and date.

Profiles: `baseline` (caching is on by default in vLLM V1), `no-prefix-cache`

## What is measured

Time to first token, prefix-cache hit rate and prompt tokens computed against served from cache, per concurrency.

## Results

See [`RESULTS.md`](RESULTS.md) for what was measured, on which hardware and date, and what surprised. Raw JSON lives under `benchmark/results/`.
