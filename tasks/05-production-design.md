# Task 05 — Production architecture

## Goal

Design an inference platform for a realistic scenario, estimate its capacity from measured numbers, and defend the design for five minutes.

## Context

You can now run, measure and optimize one server. A production system adds replicas, an API gateway, authentication, observability, scaling and a security boundary, and it has a cost. There is no single correct answer: the capstone is judged on the quality of the engineering reasoning.

## Timebox

45 minutes.

## Starting Point

- Your measured results (`benchmark/results/mine/`) and the reference results (`benchmark/results/reference/`, from `./scripts/reset.sh lab-05`).
- `workshop-artifacts/production-architecture.md`, the template, with the 15 decision questions at the end.
- Everything from the earlier days: `docs/MODEL-SELECTION.md`, `docs/METRICS.md`, `docs/SECURITY.md`, `docs/DIGITAL-SOVEREIGNTY.md`.

## Instructions

Your scenario (the trainer assigns one per group):

| | Scenario | Facts you can rely on |
| --- | --- | --- |
| A | Internal assistant handling sensitive enterprise data | 800 employees, 5 % of them active at peak, answers from internal documents (RAG), data must stay in the company, availability 99.9 % |
| B | German customer-service assistant | 2,000 chats a day, peaks of 60 simultaneous chats, short answers, GDPR applies, must not give wrong legal advice, a human can take over |
| C | Coding assistant for 100 developers | long repository context (16k to 32k tokens), interactive latency matters most, usage clustered at working hours, agents may make many calls per request |
| D | Offline document-processing pipeline | 2 million documents per month, no interactive users, cost per document matters, can use cheap or interruptible capacity |

1. **Requirements.** Write the workload and the SLO in the template's YAML. Estimate concurrency from the facts (concurrency is arrival rate times time in the system).
2. **Capacity.** Use your measurements: how many requests per second does one GPU deliver at the SLO? How many GPUs, then? State the bottleneck you expect (compute, memory bandwidth, KV cache, queueing).
3. **Model, precision, GPU, engine, context.** Justify each against the scenario, and say what you would measure to confirm it.
4. **Architecture.** Gateway, authentication, replicas and routing, observability (which three dashboards panels would page you), scaling strategy, cold-start time (use what you measured: about 40 seconds for a restart with warm caches, about 3 minutes for the first start on a new machine; `benchmark/results/reference/startup/`), failure behaviour.
5. **Security and sovereignty.** Draw the data flows (prompts, responses, logs, embeddings, weights, telemetry) and mark where each goes. Name your boundary and one attack you defend against at the infrastructure layer and one at the application layer. If agents or RAG are part of the design, count their extra model calls.
6. **Cost.** Estimate cost per useful workload (per ticket, per thousand documents, per developer per month) from GPU price and throughput. Say what "useful" means.
7. **Answer the 15 questions** at the end of the template, one line each.
8. **Prepare five minutes**: about three to present and two for the questions another group will ask.

## Expected Result

`workshop-artifacts/production-architecture.md`, complete, with every number labelled *measured*, *estimated* or *assumed*, and a defended recommendation. The strongest designs name what they would measure first and what would make them change their mind.

## Validation

- Your GPU count follows from a measured throughput and a stated SLO, not from a guess.
- Every row of the design table has a *because* that mentions a trade-off.
- The security section names a boundary and says what is **not** protected.
- You can answer: what is the first thing that breaks at ten times the load?

## If You Get Stuck

- No measured number for your case? Take the closest reference result, say that it is a proxy, and say how far from your case it is.
- Do not know where to start? Start from the SLO and work backwards: tokens per second needed, tokens per second per GPU, number of GPUs, then redundancy.
- The GPU price: use the price quoted on the slide for the workshop GPU and say that your own prices differ.

## Further Exploration

- Redo the cost estimate with FP8 and with a cheaper GPU class and see which scenario changes its answer.
- Add a second region or provider. What does it do to sovereignty, cost and operations?
- Take the strongest objection another group raised and answer it in writing.
