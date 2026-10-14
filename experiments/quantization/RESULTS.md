# Results: quantization

Raw files: [`benchmark/results/reference/quantization/`](../../benchmark/results/reference/quantization/). Every file carries hardware, model revision, engine version, server arguments and date. Hypotheses: [`README.md`](README.md).

## Setup

1× NVIDIA RTX PRO 6000 Blackwell Server Edition, vLLM 0.31.0, 1,200 input and 180 output tokens, fresh random prompts. Profiles: `baseline` (Qwen3-8B BF16), `fp8` (`Qwen/Qwen3-8B-FP8`, the publisher's own FP8 checkpoint at its own pinned revision), `kv-fp8` (BF16 weights with `--kv-cache-dtype fp8`). Concurrency 1 (24 requests) and 16 (96 requests). Quality: `experiments/quality_probe.py`, 240 generated items, greedy decoding, thinking off. One session, no repetitions.

## Speed and memory

| Profile | Concurrency | TTFT p50 (ms) | TTFT p95 (ms) | ITL p50 (ms) | Tokens/s per request | Aggregate tokens/s | Power (W) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 1 | 68 | 69 | 11.6 | 86.2 | 84.0 | 362.7 |
| fp8 | 1 | 47 | 51 | 7.3 | 138.2 | 133.8 | 317.9 |
| kv-fp8 | 1 | 72 | 74 | 11.5 | 86.8 | 84.3 | 360.3 |
| baseline | 16 | 616 | 772 | 13.5 | 69.4 | 896.6 | 425.3 |
| fp8 | 16 | 360 | 554 | 9.3 | 97.0 | 1,322.8 | 390.0 |
| kv-fp8 | 16 | 534 | 830 | 12.3 | 72.3 | 963.3 | 430.1 |

| Profile | Weights in memory | KV pool | KV capacity | Maximum concurrency at 32,768 tokens | Start (restart, warm) |
| --- | --- | --- | --- | --- | --- |
| baseline | 15.27 GiB | 58.64 GiB | 426,992 tokens | 13.03× | 39.3 s |
| fp8 | 8.85 GiB | 65.00 GiB | 473,312 tokens | 14.44× | 41.3 s |
| kv-fp8 | 15.27 GiB | 58.26 GiB | 848,400 tokens | 25.89× | 37.3 s |

The first start of the `fp8` profile, with a new checkpoint to load and compile, took 143 s (138 s in an independent dry run on another machine).

### What the data says

**FP8 weights make the decode step 37 % shorter and the system 48 % faster at concurrency 16.** ITL at concurrency 1 falls from 11.6 to 7.3 ms (86 to 138 tokens/s per request, ×1.60); at concurrency 16 aggregate throughput rises from 897 to 1,323 tokens/s (×1.48) and the time to first token p50 from 616 to 360 ms. Power drops as well (363 to 318 W at one request): energy per generated token falls from 4.3 J to 2.4 J at concurrency 1.

**The bytes explain it, but not all of it.** One decode step reads the weights once: 16.38 GB for BF16 (bound 10.3 ms, measured 11.6, ratio 1.13) and 9.44 GB for the FP8 checkpoint (bound 5.9 ms, measured 7.3, ratio 1.23). Halving the weight bytes does not halve the step because the embeddings and the output head stay in BF16, and because some fixed costs (scheduling, kernel launches, de-quantisation) do not shrink. The GPU is still memory-bound at concurrency 1, which is what makes weight quantization pay off.

**FP8 weights free memory but not much capacity on this card.** They release 6.4 GiB, which the KV pool takes (58.6 to 65.0 GiB); capacity rises by 11 % (426,992 to 473,312 tokens). On a card where the weights fill most of the memory the same saving would matter far more. On a 96 GB card FP8 weights buy decode speed, not capacity.

**An FP8 KV cache buys capacity, not decode speed at low load.** It doubles the tokens the pool holds (426,992 to 848,400) because each token costs 73,728 bytes instead of 147,456. At concurrency 1 the step does not change (11.5 against 11.6 ms: the KV of one request is a small part of the bytes). At concurrency 16 the KV reads are about 3.0 GB per step and FP8 halves them, which saves about 1.5 GB or 0.95 ms by arithmetic; the measured ITL falls by 1.2 ms (13.5 to 12.3) and aggregate throughput rises by 7 %.

### GPU-time cost of the example workload

At USD 2.49 per GPU-hour (arithmetic from the table): concurrency 16 costs 0.77 USD per million output tokens with BF16 and 0.52 USD with FP8 weights (−32 %).

## Quality: the check that has to sit next to the speed-up

240 items in three kinds: arithmetic (one step of working allowed), extracting a number from a policy text, classifying a customer message. Greedy decoding.

| Profile | Accuracy | 95 % interval | Arithmetic | Extract | Classify | Right in BF16, wrong here | Wrong in BF16, right here | Identical completions to BF16 (open prompts) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 79.6 % | 74.0 to 84.2 % | 38.8 % | 100 % | 100 % | | | |
| fp8 | 77.1 % | 71.4 to 81.9 % | 31.3 % | 100 % | 100 % | 12 | 6 | 3 % |
| kv-fp8 | 78.8 % | 73.1 to 83.5 % | 36.3 % | 100 % | 100 % | 5 | 3 | 28 % |

- **The probe cannot show a difference of two points, and it should not be read as if it could.** The intervals overlap almost completely. FP8 weights lose 2.5 points (12 items flipped to wrong, 6 to right), all of them in the one category that is not at the ceiling (arithmetic, 38.8 to 31.3 %). The extraction and classification kinds are saturated at 100 % in every profile and cannot discriminate. With the example SLO's regression bound of 2 percent, this check neither proves nor disproves compliance: it says the regression is below about five points, and a decision needs a larger eval on the user's own items.
- **The outputs are different even where the answers agree.** Only 3 % of the greedy completions of open prompts under FP8 weights, and 28 % under an FP8 KV cache, are character-for-character identical to BF16 (the shared prefix before the first difference is 43 % and 52 % of the length). Anything that depends on exact outputs (regression tests, golden files, reproducibility claims) changes with the precision.

## What surprised

- The first version of the probe gave the arithmetic category only 16 tokens, so answers that began with the equation were cut mid-number and scored wrong (14 % in every profile): a quality probe with a floor effect cannot show quality loss. It now allows 48 tokens.
- FP8 weights did not double the speed (×1.6 at best) and gave only 11 % more KV capacity: both follow from the arithmetic, but neither is what the label "half the precision" suggests.
- The FP8 KV cache is almost free in speed and quality at this scale and doubles the capacity: for a constrained pool it is the cheaper lever (see [`../context-length/RESULTS.md`](../context-length/RESULTS.md)).

## Caveats

- One session; 24 requests at concurrency 1, 96 at 16. The speed differences are far larger than run-to-run variation (about 1 %); the quality differences are not.
- The FP8 checkpoint is the publisher's build, not our own quantization: its calibration and which tensors stay in BF16 are the publisher's choices. KV-cache FP8 uses vLLM's default scales.
- Only one model family and one GPU generation with native FP8 support was tested. On GPUs without FP8 tensor cores the weights-only gain would come from bandwidth alone and kernels may differ.

## Production consequence

Quantization changes the resource profile: FP8 weights are a latency and cost lever when memory bandwidth is the limit; an FP8 KV cache is a capacity lever when the KV pool is the limit. Both change the outputs. Treat the precision as part of the model version: pin the checkpoint, run your own eval on your own items before the switch, and keep the BF16 profile as the rollback.
