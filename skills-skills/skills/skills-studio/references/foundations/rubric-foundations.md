---
date: 2026-05-31
status: research-verified
coverage: canonical
version: "1.0.0"
primary_sources:
  - "Popham, W.J. (1997). What's Wrong—and What's Right—with Rubrics. Educational Leadership 55(2):72–75"
  - "Liu et al. (EMNLP 2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. arXiv:2303.16634"
  - "Kim et al. (ICLR 2024). Prometheus: Inducing Fine-Grained Evaluation Capability in Language Models. arXiv:2310.08491"
  - "Bai et al. (2022). Constitutional AI: Harmlessness from AI Feedback. arXiv:2212.08073"
  - "AutoRubric (2025). A Unified Framework for Rubric-Based LLM Evaluation. arXiv:2603.00077"
  - "Anthropic Engineering (2025). Demystifying Evals for AI Agents"
---

# What Is a Rubric? — Foundational Knowledge Document

## The Core Claim

A **rubric** is a structured scoring guide that translates a multidimensional judgment into a reproducible decision. It is not a formula, not a checklist, and not a specification. It is a protocol for making consistent quality judgments where the thing being evaluated is too complex, contextual, or open-ended for a formula to capture.

This matters for LLM systems specifically because: probabilistic outputs cannot be evaluated with deterministic assertions, but they _can_ be evaluated with structured criteria applied consistently. The rubric is the mechanism that bridges a probabilistic system and a reliable quality signal.

---

## The Logical Structure

Every rubric has exactly three components, first formalized by Popham (1997) in educational measurement and reproduced without change in G-Eval, Constitutional AI, and every modern LLM evaluation framework:

**1. Evaluative criteria** — the dimensions of quality to be measured. Each criterion must be:

- _Independently meaningful_ — it assesses something the other criteria do not
- _Generalizable_ — it applies across instances of the task, not just one specific case
- _Teachable_ — a new evaluator can understand it without reading all prior outputs

Criteria that only apply to one specific artifact are "instructionally fraudulent" (Popham's term): they serve scoring but cannot inform improvement. Good criteria reveal what the system should get right, not just what this output happened to get wrong.

**2. Quality levels with behavioral descriptors** — for each criterion, a set of performance levels (typically 3–5) with explicit descriptions of what the evaluator should _observe_ to justify each level. Weak descriptors swap one adjective per level ("excellent" → "adequate" → "poor") without telling the evaluator what to look for. Good descriptors are parallel, observable, and mutually exclusive across levels.

**3. Aggregation rule** — how per-criterion scores combine into a final judgment. Two canonical strategies:

- **Analytic**: score each criterion independently, aggregate via weighted sum or explicit rules. Diagnostic — reveals _which_ dimension failed and _how far_ from the target.
- **Holistic**: collapse all criteria into a single overall score. Faster, cheaper, suitable for threshold decisions but diagnostic-blind.

Production practice: use analytic during development (identify which dimension regressed), switch to holistic at release gates (fast threshold check). Often combined: analytic rubrics surface findings; holistic score gates deployment.

---

## What Rubrics Are Not

Understanding rubrics requires being clear about what they are _not_. Three adjacent concepts are regularly conflated with rubrics:

**A metric** (ROUGE, BERTScore, BLEU, perplexity) is a single-dimensional formula applied mechanically to a surface feature of text. Metrics are deterministic and reproducible. Their fatal limitation: they penalize valid paraphrasing, reward surface similarity over semantic correctness, and fail entirely on open-ended generation where no canonical reference exists. G-Eval (EMNLP 2023) demonstrated this empirically: on the SummEval benchmark, rubric-conditioned LLM evaluation achieved 0.514 Spearman correlation with human judgment, outperforming all metric-based approaches by a large margin.

**A checklist** is a set of binary pass/fail gates — present or absent, met or unmet. Checklists cannot express gradation. They tell you _whether_ something is present, not _how well_ it is done. The gradation rubrics provide is not cosmetic: it enables gradient-like optimization (you know not just that a system failed, but how far it is from the target and on which dimension) and enables calibration (two evaluators can converge on a 3 vs. a 4 by discussing the descriptors; two evaluators cannot converge on "kind of present vs. mostly present" without a rubric to anchor them).

**A specification** describes what to build. A rubric describes how to evaluate what was built. Specifications are upstream of rubrics. A rubric without a corresponding specification may float free from intended behavior; a specification without a rubric has no measurement mechanism.

|  | Metric | Checklist | Rubric |
| --- | --- | --- | --- |
| Dimensionality | 1 (formula) | N (binary) | N (ordinal) |
| Gradation | None | None | Explicit levels |
| Evidence | Formula input | Presence/absence | Descriptors + reasoning |
| Diagnostic power | None | Which items failed | Which dimensions, at what level |
| Open-ended tasks | Fails (needs reference) | Limited | Native |
| Optimization target | Tune the formula | Fix failing items | Improve failing dimensions |

---

## The Probabilistic → Deterministic Bridge

This is the central insight about why rubrics are the right tool for LLM systems.

An LLM output is probabilistic: identical inputs produce different outputs across runs. Human judgment of that output is also probabilistic: different evaluators emphasize different things, apply different standards, reach different conclusions. The problem is not eliminating probability — it is **structuring and stabilizing judgment** so that the same quality produces consistent evaluations across runs, raters, and time.

The mechanism has four stages:

**Criteria decomposition** — "Is this good?" is an infinite open question. "Does this criterion meet level 3 or level 4?" is a bounded decision. Decomposition reduces the judgment space from unbounded to manageable.

**Anchor specification** — Each level of each criterion is described with explicit behavioral evidence. Anchors convert impressions ("this seems pretty good") into observable evidence checks ("the response cites sources from the provided context and does not assert facts the context doesn't support").

**Evidence-gathering** — The evaluator works through the rubric before scoring, gathering evidence per criterion. G-Eval formalizes this as chain-of-thought reasoning before scoring — the CoT steps force the evaluator to engage with each criterion rather than pattern-match to a holistic impression.

**Explicit aggregation** — A defined formula converts per-criterion scores to a final judgment, preventing post-hoc rationalization and ensuring the aggregation rule is auditable.

The result: LLM outputs remain probabilistic. The _evaluation_ of those outputs becomes structurally reproducible. The rubric is the boundary between the stochastic system and the reliable quality signal.

---

## Constitutional AI as Production-Scale Rubric

Constitutional AI (Bai et al., 2022) is the most consequential deployment of rubric logic in LLM training. The "constitution" — a set of principles from UN Human Rights frameworks, Apple ToS, Sparrow Rules, and Anthropic research — functions as a multi-criterion rubric applied during two training phases.

**Phase 1 (Supervised fine-tuning)**: Model generates a response → critiques it against a randomly sampled constitutional principle → revises. This is rubric-based self-evaluation: each principle is a criterion, the critique is evidence-gathering, the revision is scoring-driven correction.

**Phase 2 (RLHF from AI feedback)**: Model evaluates pairs of responses against constitutional principles to determine which is "more harmless." This preference data trains a reward model — a learned function approximating constitutional principle adherence. The reward model _is_ an implicit rubric: it maps (input, output) to a scalar reflecting criterion satisfaction.

Key finding: short, broad principles worked better than long, specific ones — matching Popham's finding from educational measurement that generalizable criteria outperform task-specific ones. Constitutional AI also made explicit what had previously been implicit: the rubric human raters were intuitively applying was written down and operationalized. Making the implicit rubric explicit enabled it to be applied at scale without human labeling.

---

## The Judge Paradox (Prometheus)

Prometheus (Kim et al., ICLR 2024) produced the most important empirical finding in LLM rubric evaluation: **rubric quality dominates judge capacity**.

A weaker judge model operating on a well-specified, fine-grained rubric outperforms a stronger judge model on a vague prompt. The rubric carries the domain knowledge; the model applies it. This finding directly inverts the common assumption that evaluation quality is primarily a function of model capability.

Implications for practice:

1. Invest in rubric design before investing in judge model selection
2. A smaller purpose-built evaluation model (fine-tuned on rubric application) can outperform GPT-4 on a vague prompt for specialized domains
3. Rubric specificity is not a cost — it is the mechanism that enables smaller, faster, cheaper evaluation

---

## Production Principles

From G-Eval, AutoRubric (2025), Anthropic's production guidance, and AWS Nova Rubric Judge:

**Structure:**

- 3–6 criteria per rubric. More causes reviewer fatigue and criterion conflation (the halo effect, where strength in one dimension inflates scores in others). Fewer makes the rubric too blunt for diagnosis.
- Discrete, bounded score spaces. Continuous 1–10 scales produce high variance from LLM judges. Labeled categorical options (MET/UNMET, or 5-level Likert with explicit behavioral descriptions per level) are more reliable.
- Behavioral anchors at minimum for the bottom, middle, and top levels. Abstract level labels without anchors produce inter-rater agreement close to chance.
- Criterion independence. Each criterion should assess something the others do not. Overlapping criteria introduce systematic bias where one dimension's score contaminates another's.
- Explicit evidence rules. Specify what the evaluator is and is not allowed to consult (provided context only? prior conversation? external knowledge?).
- Adjudication rules for edge cases. Without these, evaluators invent inconsistent rules on the fly.

**Reliability targets** (from psychometrics literature applied to LLM systems):

- Krippendorff's α ≥ 0.800 for production systems
- Cohen's κ ≥ 0.600 acceptable; ≥ 0.800 strong
- A gold calibration set of 30–50 examples with reference scores and rationales is required before any automated judge is deployed

**Versioning and governance:**

- Rubrics should be version-controlled with the same rigor as code. Changes to a rubric are changes to the measurement instrument and invalidate historical comparisons.
- Changes require recalibration: re-run the gold set, re-establish inter-rater agreement, re-establish the baseline.
- In regulated contexts (EU AI Act compliance, NIST AI RMF), rubrics appear in documentation as the specification of what "safe and fair" means for the system.

**One-judge-per-criterion:** Anthropic's production guidance and AutoRubric both recommend evaluating each criterion with a separate model call to prevent criterion conflation. A single call asked to assess five criteria simultaneously is susceptible to the halo effect — strong performance on one criterion inflates scores on others. Isolated dimension grading is more reliable and more debuggable.

---

## Rubrics in This Skill Library

The `[gate]`, `[review]`, and `[hypothesis]` labels in this library's rubrics directly encode the three evaluability types that AutoRubric and psychometrics distinguish:

- `[gate]` = binary/mechanical — can be checked without judgment. Analogous to AutoRubric's `binary (MET/UNMET)` criterion type. Highest reliability; suitable for automation.
- `[review]` = ordinal with judgment — requires a human or calibrated LLM applying the descriptor at each level. Analogous to AutoRubric's `ordinal` criterion type with behavioral anchoring.
- `[hypothesis]` = claimed property not yet verified — the criterion is stated as a quality property of the skill but no measurement plan has been executed. Must carry a measurement plan to be actionable.

The `skills-holistic.md` rubric represents an 8-criterion analytic rubric for skill design quality. Each dimension in that rubric follows the structure above: one criterion, 5-level scale, behavioral descriptors per level, explicit test (evidence-gathering step), and a pointer to the detailed rubric for drill-down.

---

## Source Citations

1. Popham, W.J. (1997). "What's Wrong—and What's Right—with Rubrics." _Educational Leadership_ 55(2), 72–75. [ERIC EJ552014](https://eric.ed.gov/?id=EJ552014)
2. Liu, Y., et al. (2023). "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment." EMNLP 2023. [arXiv:2303.16634](https://arxiv.org/abs/2303.16634)
3. Kim, S., et al. (2023). "Prometheus: Inducing Fine-Grained Evaluation Capability in Language Models." ICLR 2024. [arXiv:2310.08491](https://arxiv.org/abs/2310.08491)
4. Bai, Y., et al. (2022). "Constitutional AI: Harmlessness from AI Feedback." Anthropic. [arXiv:2212.08073](https://arxiv.org/abs/2212.08073)
5. AutoRubric (2025). "A Unified Framework for Rubric-Based LLM Evaluation." [arXiv:2603.00077](https://arxiv.org/abs/2603.00077)
6. Anthropic Engineering (2025). "Demystifying Evals for AI Agents." [anthropic.com/engineering](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
7. AWS ML Blog (2025). "Evaluate Generative AI Models with an Amazon Nova Rubric-Based LLM Judge on Amazon SageMaker AI." [AWS](https://aws.amazon.com/blogs/machine-learning/evaluate-generative-ai-models-with-an-amazon-nova-rubric-based-llm-judge-on-amazon-sagemaker-ai-part-2/)
8. Anthropic (2022). "Claude's Constitution." [anthropic.com](https://www.anthropic.com/news/claudes-constitution)
