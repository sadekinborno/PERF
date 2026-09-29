# PERF FYDP Roadmap
**"Are NLP Golden Standards Truly Golden?"**
Prompt Ensemble Re-annotation Framework (PERF)
Team 261-035 · Supervisor: Mr. Nahid Hossain, UIU

Full process from problem definition to thesis defense.

---

## Phase 0 — Foundations *(complete)*

- [x] Define the research problem: are widely-used NLP gold-standard benchmarks actually reliable?
- [x] Literature review on annotation noise, inter-annotator disagreement, and label error studies (Northcutt et al., Gururangan et al., etc.)
- [x] Select 10 NLP classification tasks + one gold-standard dataset per task (SST-5, GoEmotions, HateXplain, LIAR-PLUS, Reuters-21578, SNIPS NLU, PAWS, SNLI, SemEval-2016 Task 6, iSarcasm)
- [x] Document known annotation issues per dataset (Update 02 deliverable)

**Output:** Update 02 — Task & Dataset Selection Summary

---

## Phase 1 — Methodology & Framework Design

- [ ] Finalize the **four PERF re-annotation strategies** (prompting styles/approaches the ensemble will use — e.g. zero-shot, few-shot, chain-of-thought, rationale-based). Nail down exact definitions and pseudocode for each.
- [ ] Select ensemble composition: which LLMs (how many, which providers/sizes, why — diversity of training data/architecture strengthens the ensemble signal)
- [ ] Design the **confidence voting mechanism**: how per-model outputs + confidence scores combine into a single re-annotation decision, and the threshold for flagging a label as "disputed"
- [ ] Define audit metrics: agreement rate with gold label, disagreement rate, flag rate, correlation with each dataset's documented known issue (e.g. does PERF actually catch SST-5's dampening effect or SNLI's neutral–contradiction noise?)
- [ ] Define sampling strategy per dataset (full dataset vs. stratified sample — especially for SNLI's 570K and PAWS' 65K, which are too large to fully audit on a student budget/timeline)
- [ ] Get sign-off from Nahid Hossain on the finalized methodology before building anything

**Output:** Update 03 — Methodology Document

---

## Phase 2 — Pipeline Implementation

- [ ] Build data loaders/preprocessors for all 10 datasets (standardize format: text, gold label, metadata)
- [ ] Implement the LLM ensemble caller (API integration, batching, error handling, rate-limit management, cost tracking)
- [ ] Implement each of the four prompting strategies as reusable prompt templates
- [ ] Implement the confidence voting aggregator
- [ ] Implement logging: store every model's raw output, confidence score, final PERF decision, and comparison to gold label
- [ ] Build a small internal dashboard/spreadsheet to track progress per dataset (rows audited, flag counts, cost so far)

**Output:** Working PERF pipeline (codebase)

---

## Phase 3 — Pilot Study

- [ ] Run the full pipeline end-to-end on the two smallest datasets first: **iSarcasm** (4,484 examples) and **SemEval-2016 Task 6** (4,818 examples)
- [ ] Sanity-check outputs manually on a small sample (~50 examples) — do flagged disagreements look legitimate?
- [ ] Tune confidence thresholds and prompt wording based on pilot results
- [ ] Estimate total cost/time to scale to all 10 datasets and adjust sampling plan if needed

**Output:** Pilot results + refined pipeline

---

## Phase 4 — Full-Scale Re-annotation

- [ ] Run PERF across the remaining 8 datasets (SST-5, GoEmotions, HateXplain, LIAR-PLUS, Reuters-21578, SNIPS NLU, PAWS, SNLI)
- [ ] Store all raw ensemble outputs, confidence scores, and flags per dataset
- [ ] Monitor for API failures/inconsistencies and re-run as needed

**Output:** Complete re-annotation dataset (10/10)

---

## Phase 5 — Analysis

- [ ] Compute agreement/disagreement rates per dataset and per class
- [ ] Cross-reference flagged disagreements against each dataset's documented known issues (does PERF independently rediscover HateXplain's boundary ambiguity, LIAR-PLUS's single-annotator problem, etc.?)
- [ ] Identify which of the four PERF strategies performs best per task type (e.g. does chain-of-thought help more on topic classification than sentiment?)
- [ ] Statistical analysis: error rate estimates, confidence intervals, comparison to Northcutt et al.'s SNLI error-rate benchmark as a validation check
- [ ] Produce visualizations: per-dataset flag rates, per-strategy agreement, confusion matrices on disputed labels

**Output:** Update 04 — Results & Analysis

---

## Phase 6 — Human Validation

- [ ] Draw a random sample of flagged (disputed) labels across datasets
- [ ] Have human reviewers (you + teammates, possibly Nahid Hossain or peers) independently judge a subset
- [ ] Compute inter-rater reliability between PERF's flags and human judgment
- [ ] Use this to validate (or caveat) PERF's overall reliability as an audit tool

**Output:** Validation results — supports the thesis's core claim

---

## Phase 7 — Thesis Writing

- [ ] Introduction & motivation
- [ ] Related work / literature review
- [ ] Methodology (PERF framework, four strategies, confidence voting)
- [ ] Dataset selection & known issues (adapt from Update 02)
- [ ] Implementation details
- [ ] Results & analysis (from Phase 5)
- [ ] Human validation (from Phase 6)
- [ ] Discussion: what this means for benchmark reliability, limitations of PERF itself
- [ ] Conclusion & future work
- [ ] Full reference list, appendices (prompts used, extra tables)

**Output:** Full thesis draft

---

## Phase 8 — Defense Preparation

- [ ] Build defense slide deck (problem → method → results → contribution)
- [ ] Prepare a demo of the PERF pipeline if required
- [ ] Anticipate committee questions (why these 10 datasets, why this ensemble, how is PERF's own bias controlled for, cost/scalability)
- [ ] Mock defense run-through with Nahid Hossain
- [ ] Final thesis submission

**Output:** Thesis defense, final submission

---

## Immediate Next Step

You're at the start of **Phase 1**. The highest-priority open item is formalizing the four PERF re-annotation strategies and the confidence voting mechanism — everything downstream (pipeline, pilot, full run) depends on that spec being locked first.
