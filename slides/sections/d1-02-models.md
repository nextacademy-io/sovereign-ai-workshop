---
layout: section
heading: "Modern language models"
time: "09:30"
minutes: 60
layer: runtime
question: "What does a model do between prompt and answer, and which of its properties become system constraints?"
---

---
layout: statement
---

# A language model scores every possible next token. Generating text is that step, repeated.

<!--
**Key:** Everything in this block hangs on one sentence: the model maps a sequence of tokens to a score for every possible next token, and the rest is a loop around it. **Example:** There is no separate "answer mode": a chat reply is the same step run a few hundred times, with each chosen token appended to the input of the next step. **Transition:** To see what that means for a system, we need the unit it works in, the token. **Question:** "Does the model plan the whole answer first?" The loop has no separate planning step: each token comes from one pass, and reasoning models make intermediate steps visible as extra tokens. **Deeper:** Training only matters here as far as it explains this loop; we keep it short and come back to it later in the block.
-->

---
layout: default
heading: "Tokens: the unit of everything we count"
---

<Flow :items='[{ "label": "Text" }, { "label": "Tokenizer", "sub": "splits into pieces" }, { "label": "Token ids", "sub": "integers" }, { "label": "Model", "layer": "runtime" }, { "label": "Token ids", "sub": "integers" }, { "label": "Text" }]' />

A token is usually a **word piece**, not a word. The model has a fixed vocabulary of pieces.

<div class="ki-row">
<span class="muted">Counted in tokens:</span>
<span class="ki-pill">prefill work</span>
<span class="ki-pill">KV memory</span>
<span class="ki-pill">decode steps</span>
<span class="ki-pill">price</span>
</div>

<!--
**Key:** The model never sees text, only integers from a fixed vocabulary, and every cost we will discuss later, prefill work, KV memory, decode steps, price, is counted in tokens, not in characters or words. **Example:** A word may be one token or several; the tokenizer decides, and a different model usually brings a different tokenizer. **Transition:** Instead of describing it, ask the live server how it counts. **Question:** "Is a token a syllable?" No, the pieces come from how the tokenizer was built, not from linguistic rules. **Deeper:** The input and output arrows are the same vocabulary: the model reads ids and emits ids, and only the tokenizer turns them into text.
-->

---
layout: default
heading: "Ask the server: how many tokens is this?"
---

<Terminal title="your group's GPU machine">

```bash
curl -s http://127.0.0.1:8000/tokenize \
  -H "Content-Type: application/json" \
  -d '{"model": "'"$WORKSHOP_MODEL"'", "return_token_strs": true,
       "prompt": "Your sentence here"}' \
  | python3 -m json.tool
```

</Terminal>

<Terminal title="the same call with the prompt Unabhängigkeit (output as measured on the workshop model)">

```json
{"count": 3, "max_model_len": 32768, "tokens": [1806, 138644, 50499],
 "token_strs": ["Un", "abhÃ¤ng", "igkeit"]}
```

</Terminal>

- `count`: tokens in your prompt
- `token_strs`: the pieces the tokenizer chose
- `max_model_len`: the context limit this server enforces
- Send `messages` instead of `prompt` to count the chat template too

<!--
**Key:** The server's own tokenizer is the only party that must agree with itself about token counts, which is why the benchmark harness uses this endpoint to size its prompts. **Example:** Run it live once on the trainer's machine, then let participants repeat it on their own group server with their own sentences. Run it once before the session: the endpoint is not covered by the API key, and the response fields are count, max_model_len, tokens and token_strs. **Transition:** Before anyone runs it, a prediction. **Question:** "Why the quote juggling around WORKSHOP_MODEL?" The shell variable is set at login and must sit outside the single quotes of the JSON body. **Deeper:** The chat form with messages shows what the template adds around your text, such as role markers; on Qwen3 the thinking switch is part of that template.
-->

---
layout: experiment
heading: "Predict before you run it"
step: prediction
---

<Prediction>

Write down the token count of each text, then run the command and compare.

</Prediction>

<div class="ki-stack">

<div class="ki-card">

- An English sentence of about ten words
- The same sentence in German
- A long German compound word
- One line of code

</div>

**Which text costs the most tokens per character? Which costs the fewest?**

</div>

<!--
**Key:** The aim is to find out whether our mental model of tokens, words and characters is good enough to be wrong by little, before the server answers. **Example:** Collect guesses in the chat or on a shared sheet first: most people guess one token per word, then see the German and the code line move. Do not show any numbers before the group has run the command; the answers come from the live server, not from this deck. **Transition:** Run it now, three minutes, then we explain. **Question:** "Can I use my own text?" Yes, and a real German document from your own work is the better test; that is exactly what Lab 1 asks for. **Deeper:** Predictions are hypotheses; only what the server printed counts as a result.
-->

---
layout: experiment
heading: "What the count tells you"
step: explanation
---

- Tokens are **not** words or characters: the count belongs to one tokenizer.
- The same content can cost different amounts in other languages, in code, and on other models.
- Every token counts against the context window, the KV cache and the price.

<Consequence>

Count tokens on the tokenizer you will serve, with your own documents, before you plan context length or cost.

</Consequence>

<!--
**Key:** Token counts are a property of a text and a tokenizer together, so context budgets, cost estimates and KV memory all depend on counting your real texts with the tokenizer you will deploy. **Example:** Ask two or three participants what they saw: usually the German line and the code line cost more tokens than their word count suggested. Whatever the group saw, the rule stays the same. **Transition:** Inside the model, each of those ids is first turned into a vector, an embedding. **Question:** "Does German always cost more?" Not as a rule: MODEL-SELECTION says the same content can cost more tokens in German and asks you to check on the real tokenizer. **Deeper:** In Lab 1, scenario A starts from real German documents, so the count feeds the context length you must allow.
-->

---
layout: two-col
heading: "Embeddings: from ids to vectors"
---

Inside the model, the first step turns each token id into a vector of numbers.

Qwen3-8B uses **4,096 numbers** per token. Similar meanings end up close together.

::right::

### A second meaning

An **embedding model** turns a whole text into one vector, for search.

This workshop: Qwen3-Embedding-0.6B, 1,024 dimensions, on Day 3 for RAG.

<Warning>

Never mix vectors of two embedding models.

</Warning>

<!--
**Key:** The word embedding names two things: the learned vector each token id is replaced by at the model's input, and a separate small model that produces one vector per text for retrieval. **Example:** The 4,096 comes from the hidden size in the model's configuration; the 1,024 is the output size of the embedding model that the RAG demo calls on a second vLLM instance. **Transition:** The input vectors then pass through a stack of identical layers. **Question:** "Can I reuse the model's own embeddings for search?" Not safely: retrieval needs a model trained for it, and vectors from two different models are not comparable, so a new model means re-embedding every document. **Deeper:** The embedding table and the output head together hold about 1.2 billion of the 8.2 billion parameters, which is also why the FP8 checkpoint is larger than half.
-->

---
layout: default
heading: "A transformer is a stack of identical layers"
---

<Flow :items='[{ "label": "Token ids" }, { "label": "Embedding", "sub": "id to vector" }, { "label": "36 layers", "sub": "attention + feed‑forward", "layer": "runtime" }, { "label": "Output head", "sub": "vector to scores" }, { "label": "Next-token scores" }]' />

| Layers | Hidden size | Query heads | KV heads | Head size |
| --- | --- | --- | --- | --- |
| 36 | 4,096 | 32 | 8 | 128 |

<span class="muted small">Qwen3-8B, from `config/models.yaml`. 8.2 B parameters in total, 6.95 B outside the embeddings (model card).</span>

<!--
**Key:** A model like Qwen3-8B is the same block repeated 36 times, each block with an attention part and a feed-forward part, and the handful of numbers in its configuration are what we need later to size memory. **Example:** Read the table aloud once: layers, hidden size, query heads, KV heads, head size; three of those five numbers appear again in the KV cache arithmetic in the GPU sizing block. **Transition:** The attention part is the one that connects tokens to each other, so let us look at it. **Question:** "Where are the 8 billion parameters?" Mostly in the layers' weight matrices, plus the embedding table and the output head; the card lists 6.95 billion outside the embeddings. **Deeper:** In a mixture-of-experts model the feed-forward part is replaced by many expert networks and a router; we get to that after the generation loop.
-->

---
layout: two-col
heading: "Attention: every token looks back"
---

- Each token asks: which earlier tokens matter for me?
- The answer is a weighted mix of what those tokens carry.
- A token sees only the tokens **before** it.

::right::

| Role | Intuition |
| --- | --- |
| Query | what this token looks for |
| Key | what an earlier token offers as a label |
| Value | what it hands over if selected |

<Takeaway>

Keys and values of earlier tokens are reused at every step. That store is the KV cache (block d1-06).

</Takeaway>

<!--
**Key:** Attention lets each token pull information from the tokens before it, by matching its query against their keys and taking a weighted mix of their values; because later tokens never change earlier keys and values, those can be stored and reused. **Example:** In "The animal did not cross the street because it was too tired", the word "it" has to find "animal"; attention is the mechanism that lets it. Draw nothing numeric; the point is the reuse. **Transition:** Storing all of those keys and values is expensive, and one architectural choice reduces the cost. **Question:** "Why is there no stored query?" A query is needed only at the moment its token is processed; no later token ever looks at an earlier query. **Deeper:** The KV cache formula and its arithmetic live in the GPU sizing block; here we only need the idea that the cache exists.
-->

---
layout: default
heading: "Grouped-query attention: share keys and values"
---

Several query heads share one key-value head. Fewer KV heads means a smaller cache per token.

| Model (pinned) | Query heads | KV heads | Query heads per KV head |
| --- | --- | --- | --- |
| Qwen3-8B | 32 | 8 | 4 |
| Qwen3-1.7B | 16 | 8 | 2 |
| Qwen3-30B-A3B | 32 | 4 | 8 |

<Takeaway>

Cache cost follows the **architecture**, not the parameter count. The arithmetic comes in block d1-06.

</Takeaway>

<!--
**Key:** In grouped-query attention many query heads read the same keys and values, so the model stores fewer of them, and the number of KV heads is one of the three architecture fields that decide the cache cost. **Example:** Qwen3-8B has 32 query heads and 8 KV heads, so four query heads share each KV head; the mixture-of-experts model shares eight query heads per KV head and stores the smallest cache of the three. **Transition:** The cache holds the tokens of a request, which brings us to how many tokens a request may have: the context window. **Question:** "Does sharing cost quality?" Designers accept some trade-off for the memory saved, so quality is a property of the checkpoint, not a setting. **Deeper:** Other designs, multi-head latent attention or sliding-window layers, change the cache again; read the architecture of the model you pin.
-->

---
layout: default
heading: "Context window: three different numbers"
---

| | Where it comes from | Qwen3-8B |
| --- | --- | --- |
| Supported by the model | model card, `config.json` | 32,768 native, 131,072 with YaRN |
| Served by your engine | `max-model-len`, bounded by memory | 32,768 in the workshop profiles |
| Reliable for your task | your own eval at that length | unknown until you test |

<Warning>

The card says static YaRN scaling can hurt quality on short texts.

</Warning>

<!--
**Key:** "Context window" hides three numbers: what the model supports, what your server allows, and what actually works on your task, and only the third decides the deployment. **Example:** The workshop servers run with max-model-len 32768; the configuration lists 40,960 positions, which the card splits into 32,768 output tokens and an 8,192-token prompt reservation. Longer context is paid for in KV cache memory, which is the next block's arithmetic. **Transition:** With the pieces in place, we can draw the loop that produces text. **Question:** "Should I set the maximum?" No, set max-model-len to what you need, because the maximum you allow reserves memory and shapes concurrency. **Deeper:** "Supports 262,144 tokens" is a vendor claim about positions, not a measurement of answer quality at that length.
-->

---
layout: default
heading: "Generation is one step, repeated"
---

<D02TransformerInference />

<!--
**Key:** One forward pass gives scores for the next token, a sampler picks one, the token is appended, and the same pass runs again; that loop is all of autoregressive generation. **Example:** Click through slowly: first the pass, then the sampler, then the loop back. Say aloud that the first pass over the prompt is called prefill and every later pass decode; both get a full block in the inference mechanics session. The bars are a shape only, not model output. **Transition:** The sampler is where randomness enters, so next its settings. **Question:** "Why one token at a time?" Each token depends on all previous ones, so the next pass cannot start before the current token exists; that serial dependency is why decode is slow per token and why batching matters later. **Deeper:** Output stops at the end-of-sequence token or when the request's token limit is reached, whichever comes first.
-->

---
layout: two-col
heading: "From scores to one token: sampling"
---

- **Temperature**: 0 picks the highest score; higher values spread the choice.
- **Top-p and top-k** cut off the unlikely tail before the draw.
- Above temperature 0 the draw is random: two runs can differ.

::right::

| Qwen3-8B card | Temperature | Top-p | Top-k |
| --- | --- | --- | --- |
| Thinking | 0.6 | 0.95 | 20 |
| Non-thinking | 0.7 | 0.8 | 20 |

<Warning>

The card says: do not use greedy decoding in thinking mode.

</Warning>

<!--
**Key:** The model produces scores; the sampler's settings decide how deterministic the answer is, and the right settings depend on the model and on whether it thinks. **Example:** The table shows the settings the Qwen3-8B card recommends per mode; these are the vendor's recommendation, not our measurement. In Lab 2 you change temperature on a live server and see what moves. **Transition:** Settings are one source of variation; model design is another, and the biggest design split is dense versus mixture of experts. **Question:** "Which temperature should production use?" Whatever your eval used; set it on every request and record it with each result. **Deeper:** The workshop profiles use the generation-config vllm setting, which ignores the model's own default file, so sampling is exactly what each request says.
-->

---
layout: default
heading: "Dense or mixture of experts: total versus active"
---

| Model | Type | Stored | Active per token | Layers | KV heads | Checkpoint |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3-8B | dense | 8.2 B | 8.2 B | 36 | 8 | 16.38 GB (BF16) |
| Qwen3-30B-A3B | MoE, 128 experts, 8 per token | 30.5 B | 3.3 B | 48 | 4 | 32.45 GB (FP8) |

<div class="ki-grid ki-cols-2">
<div class="ki-card">

**Memory** follows the stored parameters: every expert must be resident.

</div>
<div class="ki-card">

**Compute per token** follows the active parameters. Speed must be measured.

</div>
</div>

<span class="muted small">Values from `config/models.yaml`.</span>

<!--
**Key:** A mixture-of-experts model stores many expert networks and a router sends each token to only a few, so memory follows the total parameters while compute per token follows the active ones. **Example:** Qwen3-30B-A3B stores 30.5 billion parameters, uses 3.3 billion per token, and needs 32.45 GB of FP8 weights, about twice the dense 8B in BF16, although its compute per token is a fraction. **Transition:** Another architectural choice shows up in the request itself: whether the model thinks before it answers. **Question:** "Is the MoE model faster here?" We have no measurement of it on the workshop GPU in the repository, only the trainer demo on Day 2; MoE kernels are also where the open Blackwell issues in the research notes concentrate. **Deeper:** Never size VRAM from the active count; "A3B" does not mean the memory of a 3B model.
-->

---
layout: two-col
heading: "Reasoning models: thinking costs tokens"
---

- A reasoning model writes a **thinking trace** before its answer.
- Those tokens are decoded like any others: more time, more KV cache, more GPU work.
- Qwen3 thinks by default; Gemma 4 does not.

::right::

```json
{"chat_template_kwargs":
  {"enable_thinking": false}}
```

<Warning>

Evaluate with the thinking setting you will deploy.

</Warning>

<!--
**Key:** Thinking is not free text: every thinking token is a decode step with its own time and KV cache, so a thinking model has a different latency, output length and cost than the same model with thinking off. **Example:** The JSON fragment is what Lab 2 sends to switch thinking off per request. For a ticket classifier, thinking on pays its tokens on every request; for a hard coding task it may be what makes the answer right, and only your own items can tell. **Transition:** One more model class, multimodal, in brief. **Question:** "Where does the thinking text appear?" In a separate reasoning field of the response, named reasoning, not the older reasoning_content. **Deeper:** Skippable if you are behind schedule; then say only the cost. The extra tokens thinking costs on your items are not measured in this repository; measure them with your own eval.
-->

---
layout: default
heading: "Multimodal models, in brief"
---

- Image, audio or video input needs an encoder beside the language model: extra weights and profiling memory.
- A multimodal checkpoint can run text only, for example with `--language-model-only` on Qwen3.5.
- Do not choose multimodal for a text task.

<Warning>

Licences can differ for the multimodal variant: the Llama 4 acceptable-use policy has an EU clause. Read it; not legal advice.

</Warning>

<!--
**Key:** Take a multimodal model when you need the input type, not by default, because the encoder and the profiling cost memory that a text task would rather give to the KV cache. **Example:** Qwen3.5's card describes a text-only flag that skips the vision encoder and the multimodal profiling to free memory for the cache; the Llama 4 policy withholds the multimodal rights from EU-domiciled individuals and companies, and the research notes mark the exact reading as not reviewed by counsel. **Transition:** Next: how models come to exist, but only as far as inference needs it. **Question:** "Do we cover vision in the labs?" No, the labs use text models only. **Deeper:** This slide is skippable: if the room is behind, say it in one sentence. Model facts here are as researched for this delivery; re-check them before relying on them.
-->

---
layout: default
heading: "Training, only as far as it explains inference"
---

| Stage | What changes | What it costs you | When not to |
| --- | --- | --- | --- |
| Pre‑training | All weights, from a large text corpus: the base model | Nothing directly: the publisher paid; you inherit its data choices and gaps | Never by you: you cannot retrain it or audit its data |
| Fine‑tuning | Weights or a small adapter, from your examples | Labelled data, a new eval, a repeat for every new base model, a licence that allows derivatives | A better prompt, few-shot examples, retrieval, longer context or constrained output fixes it |
| Alignment | How the model follows instructions, refuses, uses the chat format | The publisher did it; it ships as the instruct checkpoint and its chat template | You rarely change it; choose the checkpoint, read the template |

<!--
**Key:** Three kinds of training, three different answers to "does this concern me": pre-training and alignment arrive inside the checkpoint you download, and fine-tuning is the one you may decide to do. **Example:** In Lab 1 you must justify "no fine-tuning needed" or "fine-tune" for at least one scenario; the cheaper levers come first, because a fine-tune belongs to one base revision and must be redone when the base changes. **Transition:** What all of this cannot give you is a model that never errs, so the last conceptual slide is about limits. **Question:** "Is alignment a security boundary?" No: BSI notes that protective mechanisms such as fine-tuning often prove insufficient, and the controls that hold are privilege limits and human approval. **Deeper:** Ordinary LoRA or full fine-tuning is far below the Commission's indicative compute criterion for becoming a model provider; engineering input, not legal advice.
-->

---
layout: default
heading: "Limits and errors you design for"
---

<div class="ki-grid ki-cols-2">
<div class="ki-card">

### Hallucination
Fluent text is not checked text.

**Design:** test items whose honest answer is "not in the documents".

</div>
<div class="ki-card">

### Context limits
Supported is not reliable.

**Design:** test at the length you serve.

</div>
<div class="ki-card">

### Non-determinism
Sampling makes two answers differ.

**Design:** set sampling per request, record it.

</div>
<div class="ki-card">

### Prompt sensitivity
Small prompt changes move results.

**Design:** name the output fields, test variants.

</div>
</div>

<!--
**Key:** None of these four is a bug to wait out: each is a property you absorb in design, with a test you can write before the first deployment. **Example:** Constrained decoding enforces syntax only: in an indicative smoke run, a schema whose fields the prompt never named ended in whitespace padding and truncated JSON. A confident answer to a policy question is the classic hallucination; scenario A asks for answers that say "not in the documents". **Transition:** To close the block, a table of what the model's properties decide for the system around it. **Question:** "Can temperature 0 make it deterministic?" It removes the sampling randomness and is what our evals use; record the settings anyway. **Deeper:** The Qwen3 card advises against greedy decoding in thinking mode, so a temperature-0 eval measures a different regime from a thinking deployment.
-->

---
layout: default
heading: "What the model decides for the system"
---

| Model property | What it decides | Where we use it |
| --- | --- | --- |
| Stored parameters | weight memory | `d1-06-gpu-sizing` |
| Layers, KV heads, head size | KV cache per token | `d1-06-gpu-sizing`, `d2-05-kv-cache` |
| Active parameters | compute per token | `d1-03-model-selection` |
| Context window | longest request, memory per request | `d1-06-gpu-sizing` |
| Thinking mode | output tokens, latency, GPU load | `d2-02-measuring` |
| Tokenizer | token counts, context budget | Lab 1 |
| Sampling settings | variation between answers | Lab 2 |

<Takeaway>

Parameters decide memory. Architecture decides KV cost. Output length decides time.

</Takeaway>

<!--
**Key:** Each property of the model reaches into one resource of the system: parameters into memory, architecture into the cache, active parameters into compute, output length into time. **Example:** If a colleague asks whether a model "fits", you now know to ask for four things: stored parameters, layers, KV heads and the context you need; the answer is arithmetic, and we do it in the sizing block this afternoon. **Transition:** First we choose models: the model selection block turns these properties into criteria. **Question:** "Why is sampling in Lab 2?" Lab 2 lets you change temperature, prompt length and output length one at a time and see which of them moves latency; sampling changes the text and, through output length, also the time. **Deeper:** The table is the bridge to the next blocks: selection uses it as criteria, sizing as arithmetic, mechanics as latency.
-->
