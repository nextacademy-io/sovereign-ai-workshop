# Digital sovereignty

Digital sovereignty as an architecture property: five dimensions you can inspect, score and test, with the trade-offs each one brings. The workshop's own pods are the worked case.

> **This is not legal advice.** It collects engineering inputs from EU texts and guidance so that a team can ask better questions. It has not been reviewed by counsel. Where a question is legal, it says so and stops.

Facts come from [`RESEARCH.md`](RESEARCH.md), cited by section number (for example "RESEARCH 12.6"), and were verified on 2026-10-14. Laws, guidance, licences and prices change: re-check before every run. Security controls are in [`SECURITY.md`](SECURITY.md).

How statements are labelled:

- **Fact**: stated by a cited source.
- **Measured**: observed while building the workshop pods.
- **Derived**: arithmetic done here, shown where it is used.
- **Inference**: the author's reasoning. Argue with it.
- **Not verified**: could not be confirmed. Do not repeat it as fact.

| Section | Topic |
| --- | --- |
| 1 | The model: five dimensions, one property |
| 2 | The five dimensions in practice |
| 3 | Frameworks mapped onto the model |
| 4 | Open weights, open source and licence drift |
| 5 | What the slogans leave open |
| 6 | Case study: the workshop's own setup |
| 7 | Scoring worksheet |
| 8 | Portability checklist |
| 9 | The EU AI Act for engineers |
| 10 | GDPR touchpoints for inference |
| 11 | Where the facts live |

## 1. The model: five dimensions, one property

```text
DATA CONTROL + MODEL CONTROL + INFRASTRUCTURE CONTROL + OPERATIONAL CONTROL + PORTABILITY = DIGITAL SOVEREIGNTY
```

Read the plus signs as AND, and the equals sign as "is the name we give to". It is not arithmetic. Each dimension is judged on its own evidence. A system is as sovereign as its weakest dimension that matters for the data it handles (Inference).

Three rules keep this useful:

- **It is an architecture property, not a position.** A sovereign system can be slow, expensive and badly patched. A fast, cheap, secure system can depend on one vendor. Neither is wrong. You decide on purpose, with the dependencies named.
- **It is per workload.** Synthetic data on a rented GPU and patient records need different answers on the same architecture.
- **Zero dependency is not the target.** The Commission's own lessons-learnt text calls its top level, SEAL-4 ("no critical non-EU dependencies"), "not today relevant" given the dependence on chip and hardware supply chains (RESEARCH 12.11). The target is dependencies that are known, bounded and tested.

More control costs work. The table shows where.

| Dimension | What you gain | What it costs you | Example from this workshop |
| --- | --- | --- | --- |
| Data | Say who reads prompts, logs and embeddings, and for how long | You own retention, deletion, access control and the impact assessment | Request logging is off by default; every log you turn on is yours to justify (SECURITY.md, section 3.8) |
| Model | Pinned, auditable weights under a licence you read | You own evaluation, selection and licence drift | Licences changed within one family in 2026 (section 4.3) |
| Infrastructure | A named operator, region and jurisdiction | Capacity risk and price | The workshop GPU showed "Low" availability in every listed EU data center; capacity had to be confirmed before the event (RESEARCH 7.7) |
| Operations | Patch autonomy and visibility | You track advisories and run the on-call | 104 vLLM advisories were published, 27 in 2025 and 77 in 2026 (RESEARCH 13.3) |
| Portability | A credible exit | A second environment, tests and lowest-common-denominator features | Section 8 |

## 2. The five dimensions in practice

| Dimension | The question | Evidence you can collect | Typical dependency |
| --- | --- | --- | --- |
| **DATA CONTROL** | Who can read prompts, responses, logs and embeddings? Where are they stored? Who holds the keys? How long do they stay? | A data-flow map (SECURITY.md, section 4); the canary test; a retention policy; key custody | The provider's access to memory and disks; sub-processors; log platforms; telemetry endpoints |
| **MODEL CONTROL** | Which weights run? Can you reproduce and audit them? What does the licence allow? Can the publisher change it under you? | The pinned commit SHA; the licence file at that SHA; safetensors only; a copy in your own storage | The publisher's licence terms; the hub that hosts the files; opaque training data |
| **INFRASTRUCTURE CONTROL** | Who owns and operates the hardware, host, network and data center? Under which law? In which region? | Contracting entity, governing law, sub-processor list, data-center id and tags, accelerator supply | The operator's home jurisdiction; the accelerator supply chain |
| **OPERATIONAL CONTROL** | Who patches, monitors, logs, rotates keys and responds to incidents? Can you without the vendor's staff? | Advisory check dates; monitoring; runbooks (SECURITY.md, section 8); audit logs | Provider patching of host and driver; vendor support; managed services |
| **PORTABILITY** | Can you move the workload? At what effort? Have you tried? | A tested exit drill with time and cost | Proprietary APIs and SDKs; model-specific features; data formats; hardware |

## 3. Frameworks mapped onto the model

The frameworks below were written for cloud procurement and certification, not for model serving. Use them as vocabulary and as question lists. This repository claims no conformity with any of them.

### 3.1 EU Cloud Sovereignty Framework

Fact (RESEARCH 12.11): the Cloud Sovereignty Framework (CSF) comes from DG DIGIT and is tied to the Cloud III tender (EUR 180 million over six years, launched October 2025). Version 1.2.1 was read from a third-party host (Caution). The later official "Implementation guidance" is the better source. The Commission's June 2026 explainer says scoring uses 48 criteria.

| Objective | Dimension | Weight (v1.2.1) |
| --- | --- | --- |
| SOV-1 | Strategic Sovereignty | 15 % |
| SOV-2 | Legal and Jurisdictional Sovereignty | 10 % |
| SOV-3 | Data and AI Sovereignty | 10 % |
| SOV-4 | Operational Sovereignty | 15 % |
| SOV-5 | Supply Chain Sovereignty | 20 % |
| SOV-6 | Technology Sovereignty | 15 % |
| SOV-7 | Security and Compliance Sovereignty | 10 % |
| SOV-8 | Environmental Sustainability | 5 % |

SEAL, the Sovereignty Effective Assurance Level: SEAL-0 No Sovereignty; SEAL-1 Jurisdictional Sovereignty; SEAL-2 Data Sovereignty; SEAL-3 Digital Resilience (v1.2.1) or "Technological Sovereignty" (implementation guidance; the two documents name it differently); SEAL-4 Full Digital Sovereignty. The contracting authority sets a minimum SEAL per objective. The score only ranks offers that clear the minimum. The Commission notes that self-declaration is a heavy verification burden.

### 3.2 The five-part model against the frameworks

This mapping is editorial (RESEARCH 12.11): it is not a claim made by any framework.

| Model dimension | Closest CSF objectives | What the framework looks at (selected criteria) | Other frameworks |
| --- | --- | --- | --- |
| DATA CONTROL | SOV-3, SOV-2 | "Only the customer, not the provider, has effective control over cryptographic access to their data"; "auditability of AI model usage"; confinement of storage and processing to European jurisdictions "with no fallback to third countries"; exposure to non-EU laws with cross-border reach, such as the US CLOUD Act | Gaia-X label level 2 offers an EEA-only processing option; level 3 requires processing exclusively in the EEA |
| MODEL CONTROL | SOV-3, SOV-6 | AI models and pipelines "developed, trained, hosted, and governed under EU control"; open licences with "rights to audit, modify, and redistribute" | The AI Act's duties for general-purpose model providers (Art. 53) are a separate legal axis (section 9) |
| INFRASTRUCTURE CONTROL | SOV-5, SOV-1, SOV-8 | Origin of hardware, firmware and software packaging and updates; strategic dependence; power efficiency and emissions disclosure | Gaia-X level 3 also requires headquarters and main establishments in the EEA. BSI C3A allows localisation requirements: data-centre location and origin of operating staff |
| OPERATIONAL CONTROL | SOV-4, SOV-7 | Customer or EU authority can oversee logs, alerts and monitoring; "maintenance Autonomy" | C3A assumes the provider already meets BSI C5 |
| PORTABILITY | SOV-4, SOV-6 | "Ease of migrating workloads ... without vendor lock-in"; non-proprietary APIs | Gaia-X lists portability and interoperability among its goals |
| Not in the five-part model | SOV-1 Strategic (15 %), SOV-8 Environmental (5 %) | | Add them to your own worksheet or exclude them explicitly |

### 3.3 BSI C5, C3A, EUCS and Gaia-X

| Item | Status (Fact, RESEARCH 12.11, 12.12) |
| --- | --- |
| BSI C5:2026 | Published 7 April 2026, with new treatment of container management, confidential computing and post-quantum cryptography. The press release says sovereignty criteria are not part of C5:2026 and will be published separately. Not verified: its transition rule and criteria counts |
| BSI C3A | "Criteria enabling Cloud Computing Autonomy", published 27 April 2026. It follows the CSF in structure and objectives, assumes the provider already meets C5, has no regulatory effect, and will get C5-like audits |
| EUCS | **Not verified.** ENISA lists EUCS among "Schemes under development"; the only EUCS document found is a draft candidate scheme dated 22 December 2020. No adoption was found, and the Commission's June 2026 explainer does not mention it. Treat it as unadopted until you read otherwise |
| Gaia-X | Compliance Document summary of 9 July 2025: Standard Compliance plus label levels 1 to 3. Level 1 is declaration-based; level 2 adds third-party verified cybersecurity criteria and an EEA-only option; level 3 requires EEA-only processing and EEA headquarters. Built on standards such as ISO/IEC 27001 and BSI C5. Not verified: whether a newer document than the 2025 releases exists |

## 4. Open weights, open source and licence drift

### 4.1 Open weights versus open source

Fact (RESEARCH 11.1): the Open Source Initiative's Open Source AI Definition 1.0 (28 October 2024) grants four freedoms: use for any purpose, study, modify and share. It requires access to the "preferred form to make modifications", which includes three elements.

| Element | What it requires |
| --- | --- |
| Data Information | Sufficiently detailed information about the training data that a skilled person can build a substantially equivalent system, including a description of unshareable data |
| Code | The complete source code used to train and run the system: data processing, training, validation, tokenizers, inference code, architecture |
| Parameters | Weights or other configuration settings, under OSI-approved terms |

OSI's FAQ lists models that passed its validation (Pythia, OLMo, Amber, CrystalCoder, T5) and models analysed that did not (Llama 2, Grok, Phi-2, Mixtral). These are "not certifications of any kind".

**Inference (RESEARCH 11.1):** "open weights" means the parameters are published, often under a permissive or custom licence, without the full data information and training code. By the definition's wording the Qwen, Gemma, Mistral, DeepSeek, gpt-oss and Llama checkpoints are at best open weights, even under Apache-2.0 or MIT (not audited per model: Not verified per model). Several licences also impose scale or field-of-use conditions, which is the opposite of "use for any purpose".

Course rule: say **open-weight** for every model in this repository, and **open source** only where the definition's elements are met.

What this means for MODEL CONTROL: you control the artefact and not its origin. You can run, inspect, quantise and fine-tune the weights. You cannot retrain them from scratch or audit the training data. Say so in the worksheet.

### 4.2 The AI Act open-source exemption for general-purpose AI models

Fact (RESEARCH 11.2, 12.4): Art. 53(2) exempts providers of qualifying open-source models from some of the duties. The exemption is about the provider's duties. It does not decide whether you may run the model.

| Condition | Source | Effect on the models in this repository |
| --- | --- | --- |
| Licence is free and open-source: it allows access, use, modification and distribution; no limit triggered by user scale | Art. 53(2); Commission guidelines | The pinned models are all Apache-2.0 (`config/models.yaml`), so the licence test does not block them |
| Parameters, architecture information and usage information are public | Art. 53(2) | Not assessed per model |
| Not monetised: no price, paid support tied to the model, paid hosting-only access, or personal data as a condition of access | Recital 103; guidelines | Not assessed per model. Making components available through open repositories is not in itself monetisation |
| Not a model with systemic risk (presumed above 10^25 FLOPs of training compute) | Art. 51(2), Art. 53(2) | Not verified for the very large models: training compute is not disclosed in the cards read |

What the exemption covers: the technical documentation (Art. 53(1)(a)), the information for downstream providers (Art. 53(1)(b)) and the authorised-representative duty (Art. 54). What it never covers: the copyright policy (Art. 53(1)(c)) and the public training-content summary (Art. 53(1)(d)). It does not apply to models with systemic risk.

Two related but separate points:

- Art. 2(12): the Regulation does not apply to AI systems released under free and open-source licences, unless they are placed on the market as high-risk systems or fall under Art. 5 or Art. 50. This is separate from the model exemption.
- Derived (RESEARCH 11.2): licences with thresholds of the kind the guidelines name, such as the Llama 4 limit of 700 million monthly active users, the Kimi limits, the Qwen3.8 licences, the Mistral Modified MIT (monthly revenue of US$20 million) and GLM-5.3, would not pass the licence test for their providers. Apache-2.0 and MIT releases pass that test but still need the other three conditions.

The Commission guidelines are non-binding. They exist in two copies with different headers (C(2025) 5045 final of 18 July 2025 and C(2025) 7719 final of 19 November 2025), and the paragraph numbers differ. Which copy is current is Not verified. Cite sections of RESEARCH, not paragraph numbers, until you have read the copy you rely on.

### 4.3 Licence drift

Fact (RESEARCH 11.4): the licence is per repository and per version, not per family or publisher. Within one family adjacent models can differ.

| Family | Earlier | Now |
| --- | --- | --- |
| Qwen | Qwen3, 3.5, 3.6 and 3.8-27B: Apache-2.0 | Qwen3.8-2.4T-A95B under the "Qwen3.8-Max License"; Qwen3.8-Flash-Next under the "Qwen Community License 1.0" (both from August 2026) |
| Mistral | Most models Apache-2.0 | Medium 3.5 and Devstral 2: Modified MIT with a US$20 million monthly revenue ceiling that applies to the licensee's company or employer |
| Moonshot | Kimi K2.x: Modified MIT | Kimi K3: a stricter licence with a Model-as-a-Service agreement clause and a display rule |
| Zhipu | GLM-5.2, 5.1, 4.7-Flash: MIT | GLM-5.3: custom licence with a security-review clause; GLM-5.3-Flash stays MIT |
| Google Gemma | Older Gemma repositories keep the `gemma` licence tag | Gemma 4: Apache-2.0 |
| DeepSeek | V3: DeepSeek License Agreement with use-based restrictions | V3-0324, R1 and V4: MIT |

Practice (RESEARCH 11.5), one row per model, filled on the day you pin:

1. Resolve the full 40-character SHA and write the date.
2. Compare three places: the licence tag on the Hub, the `LICENSE` file at that SHA, and any separate policy file (an acceptable-use policy or a usage policy). They can disagree.
3. Find every threshold and what it is measured on: users, monthly revenue, trailing-12-month service revenue, or the employer's revenue.
4. Find naming and attribution duties, use restrictions, territorial limits and gating.
5. Read third-party quantised or fine-tuned builds against their own licence field and the base model's terms.
6. Write the commercial consequence in one sentence for your situation, and what you could not determine. Ask counsel for anything beyond internal evaluation.

`config/models.yaml` holds the revision and the licence of each pinned model. `scripts/check-repo.mjs` rejects a revision that is not a full SHA.

## 5. What the slogans leave open

Each row is a sentence you will hear. The first column is what it gets right. The second is what it leaves open. The third is a test.

| The claim | What it gets right | What it leaves open | A test to apply |
| --- | --- | --- | --- |
| "We run an open model on a non-EU hyperscaler." | MODEL CONTROL is real: weights are pinned, inspectable and not served by a model vendor. The model vendor is out of the prompt path | INFRASTRUCTURE and OPERATIONAL CONTROL belong to the operator. The operator's home law may reach data it controls. The CSF lists "exposure to non-EU laws with cross-border reach" as a criterion. The CLOUD Act text says a covered provider must disclose data in its "possession, custody, or control, regardless of whether" it is stored in or outside the United States. Whether it reaches your data is a legal question that the notes do not answer | Score all five dimensions. Ask who can read memory and disk, and under whose law |
| "Ollama runs on my developer laptop." | DATA CONTROL on one machine is strong: nothing leaves it. Ollama is MIT-licensed and binds `127.0.0.1` by default (RESEARCH 3.13) | It is a local runner built for one user: `OLLAMA_NUM_PARALLEL` defaults to 1. Nobody patches, monitors, authenticates, audits or is on call. Hosts that were made reachable were found and used: 175,108 reachable Ollama hosts in 130 countries; 214 of 1,139 exposed instances (about 18.8 %) answered a benign unauthenticated prompt (RESEARCH 13.4) | Who operates it on day 200? Where is the second copy? Who is the on-call? Can ten colleagues use it? |
| "The data center is in the EU." | Physical location is a useful fact | **EU region does not equal EU jurisdiction.** The contracting entity, the governing law, the sub-processors and the commitment on region placement decide the rest (section 6). A region is not a jurisdiction | Contracting entity, governing law, sub-processors, region commitment, certifications (RESEARCH 7.10) |
| "The provider has a GDPR tag, ISO 27001 or SOC 2." | Independent security attestation is evidence of a management system | A "GDPR" tag in a catalogue is a provider label, not a legal guarantee. An absent tag means "not reported". C5:2026 does not contain sovereignty criteria | Read the contract, the DPA and the sub-processor list, not the badge |
| "It is open source." | Open weights allow inspection and change | Open weights are not open source in the OSI sense (section 4.1) | Which of data information, code and parameters is public? |
| "It is air-gapped." | Offline operation removes calls to the Hub | "Offline" is a property to test per version, not a flag to trust. Two upstream issues show friction. The offline switch does not disable vLLM usage statistics, and the reverse also holds (RESEARCH 13.11) | Cut the network and start the exact version |
| "We pinned it." | A digest or SHA gives reproducibility | It gives no provenance: the notes found no signature or attestation for the official image. `--revision` does not cover every artefact (CVE-2026-47155) | Does the loaded file equal the pinned one? Run offline from staged files |
| "It is self-hosted, so there is no processor." | A model-API provider leaves the data path | Controller duties stay. A rented GPU pod still involves an infrastructure provider, so the processor-agreement and transfer questions move to that provider (RESEARCH 12.8) | Who is a processor for this data? |
| "We want full independence." | A clear aim | Not achievable today for accelerators and chips. The Commission calls SEAL-4 "not today relevant" | List the dependencies you accept, with an exit path for each |

## 6. Case study: the workshop's own setup

The workshop is the worked case: **an open model, a European region, a US provider.** The facts below are from RESEARCH 7.10 and the pod build. They were read on 2026-10-14; the live catalogue changes, so re-read it before a session.

### 6.1 Facts about the provider

| Question | Answer |
| --- | --- |
| Contracting entity | Runpod Inc., a US company. The state of incorporation is Not verified |
| Contract basis | A public data processing agreement (DPA) using EU Standard Contractual Clauses, Module 2, under Irish law |
| Sub-processors named | AWS, GCP, Cloudflare, Datadog and Snowflake |
| Commitment on region | "Reasonable efforts" to use a nearby server |
| Company certifications | SOC 2 Type II, SOC 3, ISO/IEC 27001:2022 |
| Product used | Secure Cloud (T3 and T4 data centers, public IP), not Community Cloud, which is a peer-to-peer network of individual hosts (RESEARCH 7.2, 7.3) |
| HTTP proxy path | Goes through Cloudflare. The workshop does not use it: only `22/tcp` is exposed |
| Whether the US CLOUD Act applies to Runpod | An inference, not a Runpod statement (Not verified). It is a legal question |

### 6.2 The data centers used

Fact (RESEARCH 7.8, live read): compliance tags are per data center.

| Data center | Where it is used | Tags reported |
| --- | --- | --- |
| EUR-IS-2 | The pod that produced the measured numbers ran here. It is in Iceland: inside the EEA, but not in the EU | GDPR, HIPAA |
| EU-RO-1 | Listed in `infra/runpod/pod-spec.example.json`; the id carries the country code RO, so confirm the location in the live read | GDPR, HIPAA |
| EUR-IS-1 | Listed in `infra/runpod/pod-spec.example.json` | None reported |

The pod specification lists all three. If the distinction between the EU and the EEA matters to your audience, pin `dataCenterIds` to `EU-RO-1` and accept lower availability (`infra/provision.md`, section 2). A tag is a provider label, not a legal guarantee. The workshop claims no compliance status beyond what the live read reports. Do not call a Runpod EU pod "EU-sovereign" (RESEARCH 7.10).

### 6.3 What data actually reaches the provider

| Data | Reaches the provider? | Why that is acceptable here |
| --- | --- | --- |
| Model weights | Yes: stored on the pod's container disk and on the `/workspace` volume | They are public Apache-2.0 files |
| Prompts and responses | Yes: they are processed on rented hardware | By rule they are synthetic, fictional or public (SECURITY.md, section 2.6). The generated benchmark prompts are original filler sentences, the handbook is fictional, the inventory is fictional |
| SSH public keys | Yes | They are public keys |
| Participants' connection metadata (source IP, timing) | Yes: it crosses the provider's network | Operational data; removed with the pod. Names and key fingerprints are also in the audit log on the pod |
| Server logs and monitoring data | Yes: on the pod disks | Request logging is off; metrics hold no prompt text |
| The trainer's account data and API credentials | Yes: they are the Runpod account | They never go onto a pod |
| Download metadata at Hugging Face | At download time Hugging Face sees the pod's IP and the repository names (RESEARCH 4.5) | Public repositories; metadata, not content |

What the provider can technically see beyond what the DPA text says is not in the notes (RESEARCH 7.10). The provider controls the layers a participant cannot see: host, driver and the network path.

### 6.4 What would change for real data

Each line is a design input, not a legal conclusion.

1. **Processor agreement.** The GPU provider would act for you. Read the DPA against GDPR Art. 28: documented instructions, sub-processor authorisation, transfers (RESEARCH 12.8).
2. **Sub-processors.** AWS, GCP, Cloudflare, Datadog and Snowflake are US companies. Ask which of them can see content, and which see only metadata.
3. **Transfers.** The DPA relies on SCCs. Schrems II requires "essentially equivalent" protection and an assessment of the third country's legal system. The EU-US Data Privacy Framework's adequacy decision stood at first instance (General Court, T-553/23, 3 September 2025). An appeal (C-703/25 P) is reported only by secondary sources: Not verified. Check the court register before saying the framework is settled.
4. **Jurisdiction.** Section 5, row 1. Take legal advice.
5. **Region.** "Reasonable efforts" is not a guarantee. Check the data center of every pod.
6. **Keys.** The CSF asks that only the customer has effective control over cryptographic access to data. The notes describe no mechanism in this setup that gives you exclusive control over data in use. Until shown otherwise, treat data in GPU memory and on pod disks as readable by the operator (Inference).
7. **Logging and retention.** Decide purpose, access and retention for every log, and whether an impact assessment is due (GDPR Art. 35).
8. **Tenancy and identity.** Replace the shared group key with per-client identities. vLLM does not isolate tenants in one process: one instance per tenant or an authenticating gateway, with `cache_salt` (SECURITY.md, section 3.3).
9. **Provider choice.** Evaluate EU-headquartered providers against the same checklist: contracting entity, governing law, sub-processors, region commitment, certifications. The notes surveyed Verda, Hetzner and Scaleway. They did not evaluate them.
10. **Roles.** A team that wraps the model in its own named system is likely the provider of that AI system (section 9).

Provider choice and engine choice are independent. The same vLLM image and profiles run on any NVIDIA host with a suitable driver (R580 or newer for the CUDA 13 image).

### 6.5 Classifying the components

Who controls each dimension for each component of this setup (Lab 5, outcome 20). "Us" is the trainer and the participants.

| Component | Data | Model | Infrastructure | Operations | Portability |
| --- | --- | --- | --- | --- | --- |
| GPU pod on Runpod Secure Cloud | Provider (storage and memory); content is synthetic | n/a | Provider | Shared: the provider runs host, driver and network; we run the container | Us: scripts rebuild it; image pinned by digest |
| vLLM engine and profiles | Us | n/a | n/a | Us: pin, patch, configure | Us: OpenAI-compatible API, container image |
| Model weights (pinned Apache-2.0) | n/a | Us: SHA, licence read, safetensors | n/a | Us | Us: files are portable; no mirror in our own storage yet |
| Hugging Face Hub (download source) | Third party sees download metadata | Third party hosts the only upstream copy | Third party | Third party | Weak until mirrored |
| Monitoring stack (Prometheus, Grafana) | Us: metrics only | n/a | Provider hosts it | Us | Us: open formats and dashboards as code |
| The trainer's cloud account | Provider holds billing and account data | n/a | Provider | Us: keys, spend limits | Us: scripts hold no provider lock beyond the pod specification |

## 7. Scoring worksheet

Apply it to an architecture, once per workload. Fill one row per dimension. Add SOV-1 and SOV-8 rows if you want the full CSF vocabulary.

The levels are a **teaching scale made for this workshop**. They are not CSF scores, not SEAL levels and not a certification.

| Level | Meaning |
| --- | --- |
| 0 | Unknown: nobody has looked |
| 1 | A third party controls it; no documented exit |
| 2 | We control it by contract or configuration; the exit is documented but untested |
| 3 | We control it technically; the exit was tested, with a stated time and cost |

Rules:

- Write evidence in the row: a file, a log line, a test, a contract clause. No evidence, no level above 1.
- Do not average. Name the weakest dimension and say whether you accept it.
- Write the cost of exit in time, money and risk, in numbers if you can.
- Record the date. Revisit the sheet when the architecture changes.

The blank sheet:

| Dimension | What do we control? | What depends on a third party? | Exit path | Cost of exit | Evidence | Level (0 to 3) |
| --- | --- | --- | --- | --- | --- | --- |
| DATA CONTROL | | | | | | |
| MODEL CONTROL | | | | | | |
| INFRASTRUCTURE CONTROL | | | | | | |
| OPERATIONAL CONTROL | | | | | | |
| PORTABILITY | | | | | | |

Worked example: the workshop pods, scored **for real data** (they would score differently for the synthetic data they actually hold). This is a teaching estimate by the author.

| Dimension | What do we control? | What depends on a third party? | Exit path | Cost of exit | Evidence | Level |
| --- | --- | --- | --- | --- | --- | --- |
| DATA CONTROL | Data classes; request logging off; telemetry off; loopback-only access | The provider hosts disks and memory; sub-processors; Hugging Face sees downloads | Delete the pod; its volume disk goes with it | Minutes. Nothing to migrate for synthetic data | `infra/verify-machine.sh`; SECURITY.md, section 4 | 1 |
| MODEL CONTROL | Pinned SHAs; Apache-2.0 read per repository; safetensors only | The only upstream copy is on Hugging Face; the cache lives on a provider volume | Mirror the pinned files into our own storage (not done) | Hours, plus storage | `config/models.yaml`; `infra/pod/fetch-models.py` | 2 |
| INFRASTRUCTURE CONTROL | The choice of data center and provider | The operator is a US company; region is "reasonable efforts"; the accelerator supply chain | Another NVIDIA host with a driver of R580 or newer | A rebuild; a second provider was not tested | `infra/provision.md`; RESEARCH 7.10 | 1 |
| OPERATIONAL CONTROL | Image pin, patching, accounts, monitoring, revocation, runbooks | Host, driver and network are the provider's | The same scripts on another host | The rebuild after a pod restart took 5 min 41 s with the model cache present (Measured) | SECURITY.md, section 8; `infra/deploy-to-pod.sh` | 2 |
| PORTABILITY | OpenAI-compatible API, image by digest, profiles as YAML, scripts in git | Provider-specific pod specification; the vLLM and Qwen features the apps use | Rebuild elsewhere from the repository | Not measured on a second provider | `apps/common.py`; `deploy/vllm/Dockerfile` | 2 |

Weakest dimensions: DATA and INFRASTRUCTURE. That is acceptable only because the data on the pods is synthetic.

Use it in Lab 5. The deliverable `workshop-artifacts/production-architecture.md` asks for a security boundary and the risks. Paste the filled sheet there and name the weakest dimension.

## 8. Portability checklist

Portability is not "we use open source". It is a result you test.

- [ ] **OpenAI-compatible API, and its edges.** Clients depend only on a base URL, a key and a model name (`apps/common.py`). The protocol is a subset: structured output (`response_format`), tool-call parsers, reasoning output and `chat_template_kwargs` in `extra_body` are engine- and model-specific (`apps/inference-client/structured.py`, `apps/tool-calling-demo/agent.py`). Test the features you use against a second server.
- [ ] **Weights pinned, and in your own storage.** A full commit SHA, a copy in object storage or a registry you control, a checksum list, and a run with `HF_HUB_OFFLINE=1` from that copy. Today the only upstream copy is on the Hub and the cache is on a provider volume.
- [ ] **Containers by digest.** The engine image by digest, a Dockerfile that builds it (`deploy/vllm/Dockerfile`), and the digest recorded in every file that holds it.
- [ ] **Configuration as files in git.** Engine profiles as YAML (`config/vllm-profiles`), provisioning as a specification (`infra/runpod/pod-spec.example.json`). No click-ops.
- [ ] **No proprietary SDK or service in the hot path.** The apps use the `openai` Python package as a client for an open protocol; plain HTTP would do. Check hosted vector databases, hosted guardrails and tracing services for lock-in.
- [ ] **Observability in open formats.** Prometheus metrics and dashboards as code (`monitoring/grafana/build_dashboard.py`).
- [ ] **Data you can export.** Logs, indexes and conversations in documented formats. Embeddings are tied to the embedding model: `Qwen/Qwen3-Embedding-0.6B` produces 1,024 dimensions, and a different model means re-embedding (Inference).
- [ ] **Hardware assumptions written down.** An NVIDIA host with a driver of R580 or newer for the CUDA 13 image (checked by `infra/verify-machine.sh`). The upstream project publishes ROCm and XPU images as well (RESEARCH 13.10); they are different images and need their own test.
- [ ] **Exit drill done, with numbers.** Rebuild the service on another host or provider from the repository and the pinned artefacts. Record time to ready and cost. Measured here on one provider: a pod rebuild after a restart took 5 min 41 s with the cache present; a download of the 16 GB primary model took 12.4 s at about 1.3 GB/s.
- [ ] **Contract exit terms** (outside engineering): data return and deletion, notice periods, and the sub-processor change process.

## 9. The EU AI Act for engineers

Treat the Act as a source of design inputs. All statements below were verified on 2026-10-14 and are **not legal advice**. Re-check before each run. Guidance documents are non-binding.

### 9.1 Role questions

Ask these in order. They are engineering questions with legal consequences.

1. Who develops the system, or has it developed?
2. Under whose name or trademark is it put into service?
3. Is it supplied for first use to a deployer, or for the builder's own use in the Union? ("Putting into service" includes own use, so an in-house system can make the builder a provider.)
4. Is it high-risk (Annex III or an Annex I product)?
5. Did we modify a general-purpose AI (GPAI) model? How much training compute did the modification use?
6. Does it interact directly with people, or generate synthetic audio, image, video or text? (Art. 50)

### 9.2 Provider and deployer

Fact (RESEARCH 12.1):

| Role | Definition | Engineering reading |
| --- | --- | --- |
| Provider (Art. 3(3)) | Develops an AI system or a GPAI model, or has one developed, and places it on the market or puts it into service under its own name or trademark, for payment or free of charge | The team that builds and names the product |
| Deployer (Art. 3(4)) | Uses an AI system under its authority, except in a personal non-professional activity | The team that uses a system someone else provides |
| Putting into service (Art. 3(11)) | Supply for first use to the deployer, or for own use in the Union for its intended purpose | An in-house tool can make the builder a provider |
| Placing on the market (Art. 3(9)) | First making available on the Union market | Guidance examples include copying a model onto a customer's own infrastructure |
| Downstream provider (Art. 3(68)) | Provider of an AI system that integrates an AI model, whether or not it provides the model itself | Anyone who builds an application around a model |

### 9.3 When a deployer becomes a provider

| Trigger | Source | Note |
| --- | --- | --- |
| Putting your name or trademark on a high-risk system already on the market | Art. 25(1)(a) | High-risk systems only |
| A substantial modification of a high-risk system that stays high-risk | Art. 25(1)(b) | A "substantial modification" is a change not foreseen in the initial conformity assessment (Art. 3(23)) |
| Changing the intended purpose of a system, including a GPAI system, so that it becomes high-risk | Art. 25(1)(c) | |
| Wrapping a model in your own named system and putting it into service | Art. 3(3), 3(11) | Inference: you are likely the provider of that AI system, not only a deployer. Open-source licensing of the system does not exempt Art. 50 (Art. 2(12)) |
| Modifying an existing generative system, for example with new training data, and putting it into service under your own name | Commission Art. 50 guidelines, para (11) (guidance) | You "become a provider of the new system" |
| Modifying a GPAI model | Commission GPAI guidelines (guidance) | You become the provider of the modified model only if the change is significant. The indicative criterion is training compute for the modification above one third of the original model's compute. "Few modifications" are expected to meet it |
| The Omnibus changed Art. 25(2) and (4) | Regulation (EU) 2026/1744 | The initial provider is no longer considered the provider of that specific AI system and must cooperate with the new provider. The written-agreement duty now also names AI model suppliers and still exempts free and open-source components other than GPAI models |

Derived arithmetic (RESEARCH 12.5), for teams that fine-tune. Training compute is about 6 times parameters times tokens. Fine-tuning a 7-billion-parameter model on 1 billion tokens is about 6 x 7e9 x 1e9 = 4.2e19 FLOP. The fallback threshold is one third of 1e23, about 3.3e22 FLOP. The fine-tune is roughly three orders of magnitude below it. A 70-billion-parameter model on the same tokens is 4.2e20 FLOP, still about 80 times below. This concerns the GPAI model role only. It does not remove system-level duties such as Art. 50 or Art. 25.

### 9.4 Art. 50 transparency

Fact (RESEARCH 12.3). Art. 50 applies from 2 August 2026. Non-compliance is subject to fines up to EUR 15 million or 3 % of worldwide annual turnover, whichever is higher (Art. 99(4)(g)).

| Paragraph | Who | Duty | Design input |
| --- | --- | --- | --- |
| 50(1) | Providers | Systems that interact directly with people are designed so that people are informed they are interacting with an AI system, unless that is obvious | A visible notice at the first interaction |
| 50(2) | Providers | Synthetic audio, image, video or text is "marked in a machine-readable format and detectable as artificially generated or manipulated"; exception for assistive editing or no substantial change of input | A marking technique and a detector: watermarks, metadata, provenance signatures, logging or fingerprints, alone or combined |
| 50(3) | Deployers | Inform people exposed to an emotion-recognition or biometric-categorisation system | A notice in the product |
| 50(4) | Deployers | Disclose deep fakes; disclose AI text published to inform the public on matters of public interest, unless it has undergone human review or editorial control | A label, and an editorial step that is recorded |
| 50(5) | All | Information is "clear and distinguishable", at the latest at the first interaction or exposure | Interface design, not a footer |

Guidance (Commission guidelines C(2026) 5054 final of 20 July 2026):

- An in-house chatbot put into service for the organisation's own use and under its name or trademark makes the organisation a provider.
- Open-source AI systems in scope still need to comply. Providers of open-source components that are not themselves an AI system are not subject to Art. 50.
- Disclosure is not needed where it is obvious, "almost no doubt left". Examples: an internal assistant for properly trained AI-literate staff, and code-assistance chatbots for professional developers.
- A Code of Practice on Transparency of AI-generated Content was published in final form on 10 June 2026 as a voluntary tool. It does not give a presumption of conformity (Omnibus recital 41).

The workshop apps are teaching apps; the notes give no basis for designing a labelling feature into them. Teams that put a system into service should list Art. 50 as a design input.

### 9.5 GPAI obligations

Fact (RESEARCH 12.4, 11.2). These are duties of the **upstream model provider**. They matter to you through the information you receive, the licence and any modification you make.

| Obligation | Article | Open-source exemption (Art. 53(2))? |
| --- | --- | --- |
| Technical documentation (Annex XI) | 53(1)(a) | Exempt if the conditions in section 4.2 are met |
| Information for downstream providers (Annex XII) | 53(1)(b) | Exempt on the same conditions |
| Policy to comply with Union copyright law | 53(1)(c) | Not exempt |
| Public summary of training content, on the AI Office template | 53(1)(d) | Not exempt |
| Authorised representative in the Union for third-country providers | 54 | Exempt unless the model has systemic risk |
| Systemic risk presumed above 10^25 FLOP of training compute; notify the Commission "without delay and in any event within two weeks" | 51(2), 52(1) | No exemption |
| Systemic-risk extras: adversarial testing, risk assessment, serious-incident reporting, cybersecurity | 55(1) | No exemption |

Further points:

- Codes of practice may be used to demonstrate compliance until a harmonised standard exists (Art. 53(4), 55(2)). The GPAI Code of Practice was published on 10 July 2025.
- Fines: up to 3 % of worldwide turnover or EUR 15 million (Art. 101(1)). Chapter V applied from 2 August 2025, with Art. 101 excepted, so fines are enforceable from 2 August 2026. The Commission says it treats providers that are not yet fully compliant with their Code commitments as acting in good faith in the first year (guidance).
- Recital 97 (interpretive): model obligations should not apply when a model is used for purely internal processes that are not essential to providing a product or service to third parties and do not affect people's rights.
- Not verified: whether the Commission has classified any common open-weight family as a model with systemic risk.

### 9.6 Dates

Fact (RESEARCH 12.6, 12.7). On 2026-10-14 the 2 August 2026 duties are live and the next dated milestone is 2 December 2026. Re-check before each workshop run.

| Date | What applies | Basis |
| --- | --- | --- |
| 2 Feb 2025 | Chapters I and II: definitions, AI literacy (Art. 4), prohibitions (Art. 5) | Art. 113(a) |
| 2 Aug 2025 | GPAI obligations (Chapter V), governance, penalties, except Art. 101 | Art. 113(b) |
| 2 Aug 2026 | General application, including Art. 50 transparency; Art. 101 fines for GPAI providers; national enforcement | Art. 113 |
| 2 Dec 2026 | New prohibitions on non-consensual intimate imagery and CSAM generation; end of the grace period for Art. 50(2) marking for systems placed on the market before 2 Aug 2026 | Omnibus, Art. 111(4) |
| 2 Aug 2027 | GPAI models placed on the market before 2 Aug 2025 must comply; national sandboxes operational | Art. 111(3); Omnibus |
| 2 Dec 2027 | High-risk requirements for Annex III systems | Omnibus |
| 2 Aug 2028 | High-risk systems under Annex I product legislation (the original date of 2 Aug 2027 is replaced) | Omnibus |

### 9.7 The Omnibus: Regulation (EU) 2026/1744

Fact (RESEARCH 12.7): "Digital Omnibus on AI", adopted 8 July 2026, published in the Official Journal on 24 July 2026 and in force on 27 July 2026. Cite it by number and ELI (`reg/2026/1744/oj`), so that readers do not rely on older summaries that say the Omnibus delays Art. 50.

| Area | What changed | For engineers |
| --- | --- | --- |
| Art. 50 | Art. 50(7) replaced: the Commission, not the AI Office, encourages and assesses codes of practice. New Art. 111(4): systems generating synthetic content placed on the market before 2 Aug 2026 comply with Art. 50(2) by 2 Dec 2026 | The only relief is a four-month grace period for marking. The text of Art. 50(1) to (5), the 2 Aug 2026 start for 50(1), (3) and (4), and the fine tier are unchanged. Disclosure for directly interacting systems must be ensured from 2 Aug 2026 even for partly generative systems (guidance) |
| GPAI | Arts. 51 to 55 and the Art. 101 fine regime are unchanged; Art. 56(6) replaced | The 10^25 FLOP presumption and the open-source exemption are unchanged |
| Art. 4 AI literacy | Providers and deployers "shall take measures to support the development of AI literacy of their staff"; no duty to guarantee a specific level for any individual | A hands-on workshop is one way to support it. The notes do not say any training format satisfies it. This workshop makes no compliance claim |
| High-risk dates | Annex III moved to 2 Dec 2027, Annex I to 2 Aug 2028 | Log-keeping duties for high-risk systems move with them (SECURITY.md, section 3.8) |
| Art. 25(2), (4) | See section 9.3 | |
| Art. 75 and new Arts. 75a to 75d | The AI Office is exclusively competent for AI systems based on GPAI models where model and system come from the same provider, with carve-outs; it gains market-surveillance powers | Relevant to model vendors that also ship products |
| Data protection | New Art. 4a lets providers exceptionally process special categories of personal data for bias detection and correction under conditions. Art. 27(4) lets a deployer cross-reference a GDPR Art. 35 impact assessment. Art. 2(7) restates that data protection law applies | Section 10 |
| Annex XIV | Lists "generative AI systems" and "Agentic AI" among emerging technologies | Agents are named in the Act's annexes now |

Cautions: the separate "Digital Omnibus" on GDPR, ePrivacy, the Data Act and NIS2 was proposed on 19 November 2025 and is only "proposed" (Not verified beyond that). Treat the GDPR as unchanged. The Omnibus also amends Art. 50 of the aviation Regulation (EU) 2018/1139; that has nothing to do with Art. 50 of the AI Act.

## 10. GDPR touchpoints for inference

Treat each row as a design input. Prompts, responses and logs that relate to an identifiable person are personal data, and storing them is processing (GDPR Art. 4(1), 4(2); RESEARCH 12.8).

| Touchpoint | Article | Design input | In this repository |
| --- | --- | --- | --- |
| Data minimisation and storage limitation | 5(1)(c), (e) | Log metadata (request id, token counts, latency, status), not bodies. Set a retention period for every log. Do not keep what you do not need | Request logging is off; `wsctl` keeps ten archived server logs; Prometheus keeps 3 days |
| Data protection by design and by default | 25(1), (2) | Pseudonymise where you can. By default process only what is necessary for the purpose, and limit storage period and accessibility | Synthetic data only; log directory permissions; SECURITY.md, section 4 |
| Lawful basis and special categories | 6, 9 | Classify data before it reaches a prompt. Special categories need a condition under Art. 9(2) | Data classes in SECURITY.md, section 2.6 |
| Processor agreements | 28 | Every party in the data path that processes for you needs a contract with documented instructions, sub-processor control and transfer terms. Self-hosting removes a model-API provider from the path; a rented GPU provider is still a party | Section 6 |
| Records of processing | 30 | Record the inference service as a processing activity | Not done: the workshop processes no real personal data |
| Security of processing | 32 | Encryption, pseudonymisation, confidentiality, integrity, availability, resilience, regular testing | SECURITY.md sections 2 and 3; `infra/verify-machine.sh` is a regular test |
| Impact assessment | 35 | Ask the question when you use new technology on personal data at high risk, or on large-scale special categories | Lab 5: name the question in the design |
| Transfers | 44 to 49 (Chapter V) | A US-hosted API sends prompts across the boundary. An EU-located pod does not, but who operates it remains a question. SCCs need a transfer assessment | Section 6.4 |
| Accountability for model provenance | 5(2); EDPB Opinion 28/2024 | A model trained on personal data "cannot, in all cases, be considered anonymous". A deployer should show it checked that the model was not developed by unlawful processing. Keep the model card, licence and training-data statement for each model | `config/models.yaml` records the publisher, licence and SHA; it has no field for a per-model provenance or training-data note |
| Logs and retention (guidance) | 5, 25 | The EDPB expert report (the author's views, not the EDPB's) lists unintended logging, unauthorised access to logs and lack of retention policy as risks. No official retention period for LLM logs exists in the notes | SECURITY.md, section 3.8 |
| On-premise for sensitive data (guidance) | 32 | CNIL: for personal or sensitive data, on-premise deployment "generally seems more appropriate and secure". Recording history is a setting for the deployer to secure | Section 5 |
| Fines | 83(4), 83(5) | Up to EUR 10 million or 2 % for Arts. 25 to 39; up to EUR 20 million or 4 % for Arts. 5, 6, 7, 9 and for transfers under Arts. 44 to 49 | n/a |

The AI Act keeps the GDPR in force (Art. 2(7), as replaced by the Omnibus) and limits log retention for high-risk systems "unless provided otherwise in ... Union law on the protection of personal data". Audit logs and minimisation pull in opposite directions. Decide it explicitly (SECURITY.md, section 3.8).

## 11. Where the facts live

| Topic | RESEARCH section |
| --- | --- |
| The provider case study | [7.10](RESEARCH.md#710-jurisdiction-and-the-data-processing-agreement-a-sovereignty-case-study), [7.8](RESEARCH.md#78-eu-data-centers-and-compliance-tags), [7.2](RESEARCH.md#72-why-runpod) |
| Open weights, open source, licences | [11.1](RESEARCH.md#111-open-weights-vs-open-source-osi-open-source-ai-definition-10), [11.2](RESEARCH.md#112-eu-ai-act-the-open-source-exemption-for-general-purpose-ai-models), [11.3](RESEARCH.md#113-licence-table-per-family), [11.4](RESEARCH.md#114-licences-changed-recently), [11.5](RESEARCH.md#115-practical-checklist-publisher--model--revision--license--commercial-implications--source) |
| Roles, Art. 50, GPAI, modifiers | [12.1](RESEARCH.md#121-ai-act-roles-provider-deployer-and-when-a-deployer-becomes-a-provider), [12.3](RESEARCH.md#123-art-50-transparency-who-is-obligated-and-from-when), [12.4](RESEARCH.md#124-gpai-obligations-open-source-exemption-systemic-risk-threshold), [12.5](RESEARCH.md#125-commission-guidelines-on-modifiers-and-fine-tuners) |
| Timeline and the Omnibus | [12.6](RESEARCH.md#126-application-timeline-after-the-omnibus), [12.7](RESEARCH.md#127-the-ai-omnibus-amendment-regulation-eu-20261744) |
| GDPR, EDPB, transfers | [12.8](RESEARCH.md#128-gdpr-articles-relevant-to-inference), [12.9](RESEARCH.md#129-edpb-opinion-282024), [12.10](RESEARCH.md#1210-transfers-schrems-ii-and-the-eu-us-data-privacy-framework) |
| Sovereignty frameworks | [12.11](RESEARCH.md#1211-sovereignty-frameworks) |
| What could not be verified | [12.12](RESEARCH.md#1212-not-verified-section-12) |
| Engines and local runners | [3.13](RESEARCH.md#313-other-engines-positioning-and-licences), [13.4](RESEARCH.md#134-exposure-incidents-for-local-inference-servers-ollama-family) |

Sources behind these sections are listed once, in the EU and compliance and Infrastructure provider sections of [`REFERENCES.md`](REFERENCES.md).
