---
date: 2026-05-31
status: research-verified
coverage: canonical
version: "1.0.0"
primary_sources:
  - "Zheng et al. (NeurIPS 2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. arXiv:2306.05685"
  - "Anthropic Engineering (2025). Demystifying Evals for AI Agents"
  - "Anthropic Alignment (2025). Bloom: An Open Source Tool for Automated Behavioral Evaluations"
  - "Huyen, C. (2025). AI Engineering. O'Reilly"
  - "Liang et al. (Stanford CRFM). HELM: Holistic Evaluation of Language Models"
  - "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge (2024). arXiv:2410.02736"
  - "Braintrust (2025). Eval-Driven Development"
---

# What Is an Eval? — Foundational Knowledge Document

## The Core Claim

An **eval** is a systematic, repeatable measurement of whether a probabilistic system meets defined quality criteria across a representative input distribution. It differs from a benchmark, a test, and a metric in purpose, scope, and operational role. Understanding these distinctions is the prerequisite for building reliable LLM-based systems.

The fundamental problem evals solve: you cannot test a probabilistic system with deterministic assertions. Given identical inputs, an LLM produces different outputs across runs. Traditional software testing (assert output == expected) fails completely. Evals replace that model with: evaluate across many inputs → score distributions → compare against baselines → gate deployment on threshold compliance.

---

## The Four-Way Distinction

These four terms are constantly conflated. Each occupies a distinct role:

**Benchmark** — A standardized, industry-wide dataset and task suite for cross-model comparison. Benchmarks (MMLU, BIG-Bench, HELM, HumanEval, SWE-bench) answer: "How capable is this model in general?" They are pre-specified, publicly replicable, and designed for comparison, not application fitness. HELM (Stanford CRFM) spans 42 scenarios across 30 models, measuring accuracy, calibration, robustness, fairness, toxicity, and efficiency — a canonical academic benchmark. Their weakness: they measure what is measurable and standardized, which is often not what a production system needs to do.

**Eval** (evaluation) — An application-specific assessment of whether _this system_ does the right thing _for these users, in this domain, under these constraints_. Evals answer: "Does our system behave correctly for its actual use case?" They are custom-built, evolve over time, and operate on real or realistic production data. A benchmark narrows model choice; an eval builds understanding of system behavior (Thoughtworks mental model).

**Test** — A pass/fail check that validates specific behavior. Tests operationalize eval insights by establishing thresholds. They commit to CI. You decide what the tests enforce by running evals first. Tests are what evals become when their results are stable enough to automate.

**Metric** — A single measurable quantity (F1, BLEU, latency, hallucination rate). Metrics are the atomic outputs of evaluation. No single metric captures overall quality. Evals compose metrics across dimensions into a quality signal.

The hierarchy: benchmarks → evals → tests → metrics. Each layer is more specific, more operational, and more continuously executed than the layer above it.

---

## Three Structural Problems Evals Solve

**The comprehension gap** — Understanding how the system behaves across the full input distribution, not just a handful of spot-checked examples. A system that looks good on the ten examples developers happened to try can fail on the eleventh example every user actually sends.

**The specification gap** — Translating fuzzy quality intentions ("be accurate and helpful") into measurable criteria. This is where rubrics enter the eval structure: the rubric specifies what "accurate" and "helpful" mean in terms the evaluator can apply consistently.

**The generalization gap** — Ensuring reliability across diverse inputs, not just the cases that were tested. An eval suite with 500 diverse inputs and known failure modes provides statistical evidence of generalization; a suite of 10 happy-path examples provides none.

---

## Taxonomy of Eval Types

### By purpose

**Capability evals** measure what the system _can_ do. They are used during development to identify targets for improvement. They intentionally start at low pass rates — the goal is to find the ceiling, not confirm current performance. A capability eval on SWE-bench Verified (whether the agent fixes failing tests without breaking passing ones) establishes the hard frontier.

**Regression evals** protect against degradation over time as prompts, models, retrieval pipelines, or tool configurations change. They maintain near-100% pass rates on a versioned golden set — a collection of inputs representing critical functionality that must always work. Every relevant change triggers regression evals. If any score falls below threshold, the change is blocked. Regression evals are the CI gate for probabilistic systems.

**Behavioral evals** measure whether the system does the right thing end-to-end for specific behavioral properties: does it follow instructions, maintain appropriate tone, stay within scope, resist sycophancy? Anthropic's Bloom framework is a canonical behavioral eval infrastructure — it generates evaluation scenarios with simulated user personas, runs them until target behaviors emerge, and quantifies elicitation rate and severity. Bloom achieved 0.86 Spearman correlation with human annotations.

**Adversarial evals** deliberately attempt to break the system — via jailbreaks, prompt injection, edge cases, or inputs designed to surface failure modes before users do. HarmBench (2024) achieved 3.9× higher vulnerability discovery rates than manual red-teaming through automated adversarial scenario generation. The input distribution for adversarial evals has three tiers: typical cases → edge cases → adversarial cases.

**Routing evals** verify that an orchestration layer correctly dispatches inputs to the right model, agent, or tool. Misrouting is a silent failure mode — a complex query sent to a lightweight model produces poor output even when both the router and the downstream model are individually correct. Routing evals measure classification accuracy of the dispatch decision independently from downstream quality.

**Safety evals** measure policy compliance: does the system avoid harmful content, resist prompt injection, treat user groups fairly, stay within organizational guardrails? A specialized behavioral sub-class.

### By environment

**Offline evals** run on a fixed dataset in development or staging — fast, cheap, suitable for CI regression gating. They test known failure modes and curated edge cases.

**Online evals** run on sampled live production traffic — catching distribution shift and emergent failures that offline tests don't anticipate. Typically 1-5% sampling rate with automated judge scoring.

**Component evals** isolate individual system parts (retriever, parser, generator, router) to locate failure sources when end-to-end scores drop.

**End-to-end evals** measure full system behavior including multi-turn trajectories, tool calls, and terminal outcome states.

---

## The Evaluator Stack

Every eval needs a scorer. There are three canonical types with distinct tradeoffs (Anthropic's taxonomy):

### Tier 1: Code-based (deterministic) scorers

Fast, cheap, objective, reproducible. Check: format compliance, schema validity, exact/regex match, tool call correctness, binary outcome verification. They are necessarily brittle to valid variations — a correct answer phrased differently fails an exact-match check.

Best for: objective, verifiable criteria with unambiguous ground truth. "Did the output include a citation?" "Is the JSON schema valid?" "Did the API call succeed without error?"

### Tier 2: LLM-as-judge (model-based) scorers

Handle subjective, nuanced criteria that resist deterministic capture: reasoning quality, tone, instruction adherence, factual faithfulness. Flexible and scalable.

Zheng et al. (NeurIPS 2023) validated this approach: strong LLM judges (GPT-4) achieved >80% agreement with human preferences on multi-turn chat evaluation — comparable to human-to-human agreement — confirming that LLM evaluation is "a scalable and explainable way to approximate human preferences."

**Structural requirements for reliable LLM judges:**

- Evaluate one dimension at a time. Separate calls for separate criteria prevent the halo effect where strength in one criterion inflates scores in others.
- Use binary PASS/FAIL or narrow scales (1–5 with behavioral descriptors). Continuous 1–10 scales produce high variance and poor calibration.
- Provide explicit descriptors for each rating level with concrete examples of pass and fail. Abstract labels without anchors ("excellent" vs. "poor") produce inter-rater disagreement close to chance.
- Request chain-of-thought reasoning before the verdict. G-Eval demonstrated this improves calibration — the judge must gather evidence against the rubric before committing to a score.
- Set temperature near zero. Consistency, not creativity, is the evaluation goal.
- Include few-shot examples calibrated against human-labeled ground truth.
- Use structured JSON output for pipeline integration.
- Run from a different model family than the system being evaluated to mitigate self-enhancement bias.

### Tier 3: Human evaluators

The gold standard. Essential for calibrating automated judges, validating that LLM judges agree with domain experts, and sampling ongoing judge drift. Prohibitively expensive for high-volume evaluation. The workflow: human annotation defines ground truth → automated judges calibrated against it → ongoing human sampling validates that calibration holds.

Chip Huyen's maxim applies: "Manual inspection of data has probably the highest value-to-prestige ratio of any activity in machine learning." Even a small number of carefully reviewed examples reveals failure patterns that automated pipelines miss.

**Calibration requirement before production use:** Build a calibration set of 30–50 expert-labeled examples. If the automated judge disagrees with domain experts more than 20% of the time on clear cases, the judge prompt needs revision. The calibration set is the measurement instrument for the measurement instrument.

---

## Known Biases in LLM-as-Judge

The 2024 "Justice or Prejudice?" paper catalogued 12 bias types across LLM evaluators. The most operationally significant:

| Bias | Mechanism | Mitigation |
| --- | --- | --- |
| **Position bias** | Favors responses by ordinal position; robustness drops below 0.5 with 3+ options | Run pairwise comparisons in both orders; average results |
| **Verbosity bias** | Prefers longer responses regardless of quality | Include conciseness explicitly as a rubric criterion |
| **Self-enhancement bias** | Favors outputs from same model family | Use judge models from different families; LLM juries |
| **Authority bias** | Grants credibility to sources regardless of content | Rubric instruction to evaluate content, not attribution |

These biases are not eliminated by prompt engineering alone. Structural mitigations (swapping evaluation order, using multiple judges, purpose-built evaluation models) are required for production reliability.

---

## Personas: Adversarial Evaluators

A persona is a simulated evaluator identity designed to surface failures that a neutral evaluator would miss. The mechanism: define the persona's prior beliefs, failure hypotheses, and quality concerns → generate adversarial prompts from that perspective → score the system's response relative to the persona's quality standard.

Bloom (Anthropic, 2025) generates "simulated user personas" during evaluation scenario ideation to create diverse, realistic conditions. The same logic underlies the 9-critic council in this skill's **critique** mode: each critic (Boris Cherny, Steve Yegge, Elon Musk, Charity Majors, Andrej Karpathy, Simon Willison, Scott Wlaschin, Chip Huyen, David Farley) applies a distinct adversarial lens, collectively covering failure territory no single evaluator would surface.

Personas are particularly effective for behavioral evals because they model the diversity of real users — different mental models, different intentions, different prior expectations — in a way that abstract test cases cannot.

---

## The Probabilistic → Reliable Translation

The fundamental challenge: a probabilistic system cannot be evaluated with deterministic assertions. Five interlocking techniques translate probabilistic behavior into reliable quality signals:

**Statistical aggregation over datasets** — evaluate against hundreds or thousands of inputs, not one. Quality is a distribution, not a point estimate. A system that passes 95% of 500 test cases under reproducible conditions is a reliable quality claim even if no individual output is guaranteed. Score stability under dataset resampling is the validity check.

**Multiple-run metrics** — pass@k (probability of at least one success in k attempts) and pass^k (probability all k attempts succeed) quantify the distribution of success rather than pretending outputs are deterministic. A system passing 18/20 trials has meaningfully different reliability than one passing 1/20.

**Rubric-anchored scoring** — criteria with behavioral descriptors convert open-ended quality judgments into consistent classification tasks. The rubric is the bridge between fuzzy human intent and machine-scorable criteria. (See `rubric-foundations.md` for the full logical structure.)

**Calibrated automated judges** — when calibrated against human ground truth and validated at <20% disagreement on clear cases, LLM judges become reliable proxies for human judgment at scale. The calibration step is what makes automation trustworthy rather than just fast.

**Versioned golden sets and baselines** — holding the evaluation dataset and scoring criteria constant means score changes reflect real system behavior changes rather than measurement noise. Drift in judge behavior or dataset distribution is detectable because the baseline is anchored.

The resulting system is not deterministic — it is _statistically reliable_. The eval translates "this probabilistic system sometimes produces good outputs" into "this system produces outputs satisfying defined criteria at X% rate, measured reproducibly, with a known baseline."

---

## Evals as CI Infrastructure: Eval-Driven Development

Chip Huyen's Evaluation-Driven Development principle (AI Engineering, O'Reilly 2025) mirrors Test-Driven Development: _define how you will evaluate your application before you start building it_. This forces upfront clarity on what "good" means and prevents the common failure mode of building a system and then discovering it cannot be reliably evaluated.

**EDD pipeline stages:**

1. Define what "good" means for each use case (rubric design)
2. Curate datasets covering typical cases, edge cases, known failure modes
3. Build the evaluation pipeline (deterministic checkers → LLM judges → human calibration)
4. Validate the eval pipeline itself — check signal quality, reproducibility, correlation with actual user value
5. Evaluate all system components, not just end-to-end output

**The CI/CD gate architecture:**

| Trigger | Gate | Action on failure |
| --- | --- | --- |
| Every PR touching prompts, model config, retrieval | Smoke eval — fast subset of golden set | Block merge |
| Before staging promotion | Full regression suite — complete golden dataset | Block promotion |
| Before production promotion | Safety/compliance evals | Block promotion |
| 1–5% of live traffic | Online eval via automated judge | Alert; no blocking |

**Thresholds and tolerances:** Regression thresholds define acceptable score variance. A 5% improvement on tone might offset a 1% decrease in accuracy under defined tolerances; a 3% accuracy drop triggers automatic block. Thresholds are versioned alongside code — changes require justification and re-baselining.

The operational insight from OpenAI's documentation: "run evals on every change, not just at launch." Code-based evals can run on every commit; model-graded evals typically run on PR-level changes. Treating evaluation as infrastructure — rather than a periodic quality check — is the distinction between teams that catch regressions before users do and teams that learn about failures from support tickets.

---

## Eval Maturity Levels

Practitioner surveys in 2025–2026 reveal that most teams operate at Level 0–1:

| Level | What exists | What's missing |
| --- | --- | --- |
| 0 | Manual spot-checks | Any systematic evaluation |
| 1 | Offline evals on golden sets | CI integration; no regression blocking |
| 2 | CI-gated evals; regression blocking on core metrics | Online evals; automated adversarial testing |
| 3 | Online evals on production traffic; automated red-teaming; eval-driven prompt optimization | — |

Level 2 is the practical minimum for any production LLM system where reliability matters. Level 3 is appropriate for high-stakes or high-volume systems.

---

## Evals in This Skill Library

The routing eval corpus in every skill in this library (e.g., `evals/routing-corpus.json` in `ops-repo`) is a routing eval — it measures classification accuracy of the skill activation decision. The `[gate]` dimensions in rubrics are code-based scorers. The `[review]` dimensions require an LLM-as-judge or human evaluator applying the rubric. This skill's **critique** full-panel mode is a behavioral eval using adversarial critic personas.

The 10-dimension `skills-holistic.md` rubric functions as the master rubric for a full skill quality eval — it specifies the criteria (what to evaluate), the levels (1–5 scale), and the tests (evidence-gathering steps). Running it against a skill is an analytic eval; a single holistic score at a release gate is a simplified threshold eval.

The relationship between rubrics and evals: rubrics specify what quality means; evals operationalize that specification into a measurement pipeline. Neither is sufficient without the other. A rubric without an eval is a stated intention with no measurement. An eval without a rubric is measurement without a defined target.

---

## Source Citations

1. Zheng, L., et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023. [arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
2. Liu, Y., et al. (2023). "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment." EMNLP 2023. [arXiv:2303.16634](https://arxiv.org/abs/2303.16634)
3. Anthropic Engineering (2025). "Demystifying Evals for AI Agents." [anthropic.com/engineering](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
4. Anthropic Alignment (2025). "Bloom: An Open Source Tool for Automated Behavioral Evaluations." [alignment.anthropic.com](https://alignment.anthropic.com/2025/bloom-auto-evals/)
5. Huyen, C. (2025). _AI Engineering_. O'Reilly. Chapters 3–4: Evaluation-Driven Development.
6. Liang, P., et al. "Holistic Evaluation of Language Models (HELM)." Stanford CRFM.
7. "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge." (2024). [arXiv:2410.02736](https://arxiv.org/abs/2410.02736)
8. HarmBench (2024). Standardized evaluation framework for automated red-teaming. [arXiv:2402.04249](https://arxiv.org/abs/2402.04249)
9. Braintrust (2025). "Eval-Driven Development." [braintrust.dev](https://www.braintrust.dev/articles/eval-driven-development)
10. Thoughtworks (2024). "LLM Benchmarks, Evals and Tests — A Mental Model." [medium.com/thoughtworks](https://thoughtworks.medium.com/llm-benchmarks-evals-and-tests-9bf2826f6c55)
11. Evidently AI (2025). "LLM Evaluation Guide." [evidentlyai.com](https://www.evidentlyai.com/llm-guide/llm-evaluation)
12. Comet (2025). "LLM-as-a-Judge: How to Build Reliable, Scalable Evaluation." [comet.com](https://www.comet.com/site/blog/llm-as-a-judge/)
