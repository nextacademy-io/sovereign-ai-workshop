# Task 01 — Model selection

## Goal

Choose, size and defend an open model for realistic scenarios (four are on offer), using the smallest model that reliably does the job.

## Context

Model choice decides memory, speed, cost and legal exposure. A leaderboard rank does not tell you whether a model fits your GPU, speaks German, calls tools reliably or may be used commercially. You work in your group and produce one document.

This lab follows the GPU, sizing, inference-mechanics and model-selection modules, so you already have the tools it needs: the KV-cache arithmetic for a given context and concurrency, the difference between prefill and decode, and TTFT as the number a user waits for. Use them here: every scenario gives you numbers to design for, so the arithmetic can check your choice.

## Scope

Done means that every scenario your group worked on has a complete block in `workshop-artifacts/model-selection.md` (model, precision, context length, trade-off) and that the license table covers every model you named. Each sub-group takes **one** scenario first and finishes it before taking another or swapping with a sub-group. Reduced scope is a legitimate outcome: two complete, defended blocks are better than four thin ones. Out of scope: running or benchmarking the candidate models; this lab decides with arithmetic, model cards and licenses.

## Starting Point

- Your group's GPU machine, or your laptop: the commands below run anywhere with Python.
- `workshop-artifacts/model-selection.md`, the template for this task (`./scripts/reset.sh lab-01` creates it if it is missing).
- The models of this workshop in `config/models.yaml`, and the criteria in `docs/MODEL-SELECTION.md`.

## Instructions

Scenarios (split your group into sub-groups; each sub-group takes **one** scenario first, finishes it, and then takes another or swaps with another sub-group; your trainer may name the first scenario):

| | Scenario | Numbers to design for |
| --- | --- | --- |
| A | Internal German-language assistant for 300 employees, answering from company documents | 20 concurrent users at peak; data must not leave the company; answers within 10 s; 3,000 tokens of retrieved context per question |
| B | Customer-service classification and information extraction | 40,000 tickets per day, peaks of 5 per second; 300 input and 60 output tokens; JSON output; 95 % of tickets within 2 s |
| C | Coding assistant for a development team | 100 developers; chat with 16,000 to 32,000 tokens of repository context; first token within 1 s for 95 % of requests |
| D | Document-processing pipeline, run once a month | 2 million documents, 3,000 input and 300 output tokens each; finish within 72 hours; cost per document matters, latency does not |

For each scenario:

1. Decide what quality is needed and how you would test it (one sentence is enough).
2. Name a model, a precision, an inference engine and a context length. Check the license in `config/models.yaml` or on the model card.
3. Check that it fits the GPU:

   ```bash
   python3 scripts/sizing.py --model primary --precision bf16 --context 8192 --concurrency 16
   python3 scripts/sizing.py --model quantized --precision fp8 --kv-dtype fp8 --context 32768 --concurrency 8
   ```

4. Decide on thinking mode (reasoning) and say why.
5. Write down **what you gave up**. A choice without a trade-off has not been thought through.

Fill in `workshop-artifacts/model-selection.md` as you go. Then copy your best scenario into the *Selected Model* section of `workshop-artifacts/inference-report.md`.

## Expected Result

`workshop-artifacts/model-selection.md` has a block for every scenario your group worked on. Every block names a model, a precision, a context length and a trade-off, and the license table lists every model you named with its commercial implications. Blocks for scenarios you did not reach stay empty, and you say so.

## Validation

- For each choice you can show a `sizing.py` run that says it fits, or you can say precisely why it needs more than one GPU.
- You can answer the trainer's question "which smaller model did you consider, and why did you reject it?" for every scenario you worked on.
- No license entry says only "open": each names the license and one consequence.

## If You Get Stuck

- Unsure how to size? Run `python3 scripts/sizing.py --help` and start with weights, then add the KV cache for your context and concurrency.
- Unsure about a license? Read the `LICENSE` file of the model repository, not a blog post (licenses differ between versions of the same family).
- No model fits scenario C or D? That is a finding: say what you would need (a bigger GPU, quantization, several GPUs) and what it would cost.

## Further Exploration

- Repeat scenario A with FP8 weights and an FP8 KV cache and see how many more users fit.
- Pick a model from a family that is not in `config/models.yaml` and check its license for thresholds that would apply to your employer.
