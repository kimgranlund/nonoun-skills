---
date: 2026-05-31
status: draft
version: "0.1.0"
---

# Rubric Quality — Best Practices Rubric

**A rubric that uses adjective-only level descriptors, unlabeled criteria, and untested hypotheses asserted as facts generates noise, not measurement.** Two reviewers applying such a rubric to the same artifact reach different scores because the rubric has not told them what to look for — only what adjective applies. The result is calibration failure: the rubric compiles, but it does not measure.

**Grounding:** The RQ evaluator topical section (RQ1–RQ5 in `eval-prompts.md`) operationalizes this rubric as adversarial prompts. The `[gate]`/`[review]`/`[hypothesis]` labeling convention is documented in `rubric-foundations.md`. The Judge Paradox from Prometheus research (a weaker model on a well-specified rubric outperforms a stronger model on a vague one) is the empirical foundation: rubric quality dominates judge quality.

**Companion docs:**

- `rubric-foundations.md` (this folder) — foundational knowledge on rubric design (criteria × levels × descriptors × aggregation)
- `skills-authoring.md` (this folder) — D5 drift resistance (citing substrate, not describing it)
- `evaluation-workflows.md` (this folder) — D3 evaluator independence, D5 regression detection

---

## §The Problem

A rubric library that has grown by accretion develops four failure modes that compound over time:

1. **Label drift.** Criteria are added without `[gate]`/`[review]`/`[hypothesis]` labels. Consumers cannot tell which criteria are mechanically checkable and which require expert judgment. The rubric is applied inconsistently, and scores across runs or reviewers are not comparable.

2. **Adjective ladders.** Level descriptors change only the adjective: "excellent / adequate / poor." The reviewer knows which level to assign ("it's excellent") but not why — what they observed in the artifact that justified the label. Two reviewers using adjective ladders reliably disagree at the boundary.

3. **Hypotheses as facts.** Performance claims ("the skill compounds over invocations — 2h → 15min") are stated as `[gate]` or `[review]` without measurement. The criterion is a belief, not a verified property. Future runs cannot distinguish real improvement from measurement noise.

4. **Conflated criteria.** One dimension asks two independent questions: "Does the skill have a clear description AND produce a useful output?" A skill can pass one and fail the other; the dimension cannot distinguish them.

The rubric below scores rubric quality on six dimensions. D1, D3, and D5 are `[gate]`; D2, D4, and D6 are `[review]`.

---

## §First Principles

### 1. A rubric is a measurement instrument, not an opinion

Per Popham (1997): the measure of a rubric is whether two independent reviewers, applying it to the same artifact, reach the same conclusion. A rubric that produces different scores across reviewers is not a rubric — it is a structured opinion. The instrument fails before the measurement begins.

### 2. `[gate]`/`[review]`/`[hypothesis]` labels are the honesty layer

- **`[gate]`**: mechanically checkable — any reviewer running the check reaches the same binary result. Suitable for CI automation.
- **`[review]`**: requires expert judgment — two reviewers may differ by 1 point, but the criterion specifies what evidence to cite and what would constitute each level.
- **`[hypothesis]`**: a stated property not yet verified across real invocations. Must carry a measurement plan; cannot be scored as fact.

A mislabeled criterion over-claims (a `[review]` labeled `[gate]`) or under-claims (a `[gate]` labeled `[review]`). Both degrade the rubric's utility.

### 3. Behavioral anchors are the mechanism that enables calibration

A level descriptor that reads "evidence of strong inversion" requires judgment about what "strong" means. A level descriptor that reads "every repeatable procedure with clear pass/fail is cited as a script command; no step-by-step prose for mechanizable operations" is behavioral — two reviewers can scan the artifact and count mechanize-bait steps. The count is the evidence; the count determines the level.

### 4. Criterion independence eliminates halo effects

When two criteria measure overlapping properties, a high score on one systematically inflates the other — the halo effect. Each dimension should assess a property the others do not. If two dimensions correlate at > 0.8 across a calibration set, they are conflated and one should be removed or subdivided.

### 5. Every `[hypothesis]` dimension needs a measurement plan before it is actionable

A hypothesis without a measurement plan is a belief. "The skill compounds over invocations" is not measurable without: a metric (time-to-complete per invocation), a sample size (≥5 invocations), a comparison baseline (first vs. fifth), and a judgment call on what constitutes "compounding." Without these, the dimension produces neither evidence nor improvement signal.

---

## §The Rubric

### Dimension 1 — Label completeness `[gate]`

Does every criterion in the rubric carry a type label (`[gate]`, `[review]`, or `[hypothesis]`)?

Count unlabeled criteria. A dimension that has a scoring table but no label is unlabeled. A label that appears in the section heading but not the criterion itself is ambiguous.

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every dimension is labeled. Labels appear consistently in the dimension heading (e.g., `### Dimension 3 — Inversion quality \`[review]\``). No dimension is ambiguous. |
| **4 — Good** | 0–1 unlabeled dimensions. The unlabeled one is a general dimension (not a performance claim) where the type is inferable from context. |
| **3 — Adequate** | 2–3 unlabeled dimensions. Consumer must infer type from the scoring table. |
| **2 — Poor** | 4+ unlabeled dimensions. The rubric cannot be applied consistently — different reviewers will treat dimensions as gate or review inconsistently. |
| **1 — Failing** | No labels anywhere. The rubric does not distinguish mechanically-checkable from judgment-based criteria. All scores are implicit review judgments. |

**Test:** Count dimensions without `[gate]`, `[review]`, or `[hypothesis]` in their heading. Count > 1: FAIL.

---

### Dimension 2 — Label accuracy `[review]`

Are the type labels correct? Do `[gate]` criteria specify a check any reviewer could run mechanically? Do `[review]` criteria specify the evidence to cite and what it shows?

A `[gate]` labeled criterion that requires expert judgment to apply is mislabeled as `[gate]`. A `[review]` criterion with a mechanical pass/fail check is mislabeled as `[review]`.

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every `[gate]` criterion names a specific, runnable check (command, count, binary condition). Every `[review]` criterion names the evidence source and what it shows at each level. No mislabeled criteria. |
| **4 — Good** | 0–1 mislabeled criteria. The mislabeled one is a borderline case (a check that could be automated but currently requires manual inspection). |
| **3 — Adequate** | 2–3 mislabeled criteria. The most common error: a `[gate]` criterion whose check requires judgment ("is the description quality sufficient?"). |
| **2 — Poor** | 4+ mislabeled criteria. The rubric claims mechanical checkability it does not have. |
| **1 — Failing** | Most `[gate]` criteria require expert judgment. The rubric over-claims automation. Consumers will automate checks that are actually judgment calls. |

**Test:** Pick each `[gate]` criterion. Can a script or grep produce the pass/fail result without human review? If no: mislabeled. Count mislabeled > 2: FAIL.

---

### Dimension 3 — Behavioral anchor quality `[gate]`

Do the level descriptors (the scoring table rows) describe observable evidence — what the reviewer should see in the artifact at each level — rather than adjective-only labels?

Count levels with adjective-only descriptors ("excellent," "adequate," "poor," "strong," "weak") where the adjective is the entire criterion rather than accompanying a behavioral observation.

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every level descriptor contains at least one behavioral observation: a count, a specific presence/absence, an observable property of the artifact. "Score 4: most procedures are inverted — 1–2 multi-step prose blocks remain for genuinely judgment-heavy steps" is behavioral. |
| **4 — Good** | 0–1 levels across all dimensions use adjective-only language. All others have behavioral observations. |
| **3 — Adequate** | 2–4 levels use adjective-only language. Reviewers at the boundary between adjacent levels must apply personal judgment about what "adequate" means. |
| **2 — Poor** | 5+ levels are adjective-only. The rubric provides labels without evidence criteria. Different reviewers will score the same artifact differently. |
| **1 — Failing** | Most levels are adjective-only. The rubric is a structured opinion — it tells reviewers what to conclude, not what to look for. |

**Test:** Read each level descriptor in the scoring tables. Count levels where the only distinguishing content is an adjective ("excellent," "poor") with no behavioral observation. Count > 3: FAIL.

---

### Dimension 4 — Criterion independence `[review]`

Do the dimensions assess distinct properties — properties that can vary independently — or do they measure overlapping constructs that will produce correlated scores?

Two criteria are conflated when: improving one automatically improves the other (e.g., "description quality" and "routing accuracy" are downstream of the same root); or when a single artifact property is scored twice (e.g., "verification gate present" and "termination stack verified").

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each dimension assesses a property that can fail independently of all others. No two dimensions would score the same artifact identically. If a calibration set existed, inter-dimension correlation would be < 0.5. |
| **4 — Good** | 0–1 dimension pairs are somewhat correlated but measure genuinely distinct properties — an artifact can pass one and fail the other with a realistic scenario. |
| **3 — Adequate** | 2 dimension pairs are substantively correlated. One could be removed or merged without losing diagnostic information. |
| **2 — Poor** | 3+ dimension pairs are correlated. The rubric over-counts a narrow set of properties while missing others entirely. A high scorer on one cluster is almost guaranteed to score high on others. |
| **1 — Failing** | Most dimensions measure the same underlying property (e.g., all test "is the output well-structured?"). The rubric's N dimensions collapse to 1–2 independent signals. |

**Test:** For each pair of dimensions: name a concrete artifact that passes D_i but fails D_j. If no such artifact exists: the dimensions are conflated. Count conflated pairs > 1: FAIL.

---

### Dimension 5 — Hypothesis measurement plan `[gate]`

For every `[hypothesis]` dimension: does it carry an explicit measurement plan — a named metric, a sample size, a comparison baseline, and a judgment rule?

A `[hypothesis]` without a measurement plan is an asserted belief. The rubric should not score it as a property of the artifact; it should score the presence and quality of the plan to verify it.

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every `[hypothesis]` dimension carries: (a) a specific metric ("time-to-complete per invocation"), (b) a minimum sample size (≥5 invocations), (c) a comparison baseline (first vs. Nth), and (d) a judgment rule (what constitutes "compounding"). |
| **4 — Good** | Every `[hypothesis]` has a measurement plan but one element is vague (e.g., sample size is "sufficient" rather than a number). |
| **3 — Adequate** | Some `[hypothesis]` dimensions have partial plans (metric named, no sample size, no baseline). The dimension is directional but not actionable. |
| **2 — Poor** | Most `[hypothesis]` dimensions assert the property as observable fact ("the skill compounds") without any measurement plan. |
| **1 — Failing** | `[hypothesis]` dimensions are present but treated as `[review]` dimensions — scored on "does it seem like it compounds?" without any measurement. The distinction between hypothesis and verified fact is erased. |

**Test:** List all `[hypothesis]` dimensions. For each: does it contain (a) metric, (b) sample size, (c) baseline, (d) judgment rule? If any is absent: FAIL for that dimension. Count failing dimensions > 0: overall FAIL.

---

### Dimension 6 — Calibration potential `[review]`

If two independent reviewers applied this rubric to the same artifact, would they agree within 1 point on `[review]` dimensions?

Calibration potential is assessed by reading the `[review]` criteria and asking: does the level descriptor give me enough specificity to score consistently? Or would I score differently from a colleague who has the same expertise but no shared reference?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every `[review]` criterion specifies: what evidence to look for, what distinguishes level N from level N+1, and what would constitute each level in the artifact under review. Two calibrated reviewers would score within 1 point with > 80% probability. |
| **4 — Good** | Most `[review]` criteria are specific enough for calibration. 1–2 criteria have ambiguous level boundaries (e.g., "many" vs. "most") that would produce occasional 2-point disagreements. |
| **3 — Adequate** | `[review]` criteria are directionally correct but lack the specificity for consistent calibration. Reviewers will agree on obvious cases (1 and 5) but disagree on boundary cases (2, 3, 4). |
| **2 — Poor** | Most `[review]` criteria use adjective-only language. Inter-reviewer agreement would be at chance for non-extreme scores. |
| **1 — Failing** | The rubric is not calibratable. Two reviewers applying it to the same artifact would disagree on most dimensions by 2+ points. |

**Test (calibration test):** Apply the rubric to a known artifact with a second independent reviewer. For each `[review]` dimension: do scores agree within 1 point? Count dimensions where disagreement > 1: failing = count > 2 across 6 dimensions.

---

## §Anti-Patterns

### AP-RQ-1 — The adjective ladder

**Symptom:** Each level in the scoring table changes one adjective: "5 — Excellent: strong inversion / 4 — Good: mostly inverted / 3 — Adequate: partially inverted / 2 — Poor: weak inversion / 1 — Failing: no inversion." Each level uses the word "inversion" without specifying what counts as evidence of inversion at each level. **Root cause:** Authors describe conclusions ("inversion quality") rather than evidence ("count of mechanize-bait steps remaining"). **Correction:** Replace each adjective with a behavioral observation: "Score 4: most procedures are inverted; 1–2 prose blocks remain for steps that cannot be mechanized." The reviewer observes the count, not the conclusion.

### AP-RQ-2 — The hypothesis asserting as fact

**Symptom:** A `[gate]` or `[review]` dimension claims "the skill compounds over invocations" — a performance property — without specifying measurement conditions. It is scored as an observable artifact property rather than a testable hypothesis. **Root cause:** Authors know the property is important and want it scored; they do not have measurement data yet and skip the hypothesis label to avoid signaling weakness. **Correction:** Label the dimension `[hypothesis]` and add a measurement plan. This is honest: the property is claimed but not verified. "The hypothesis is X; it will be verified by measuring [metric] across ≥5 invocations and comparing first vs. Nth."

### AP-RQ-3 — The conflated criterion

**Symptom:** One dimension asks two questions: "Does the skill have a clear description AND does it produce useful output?" An artifact can pass one and fail the other; the dimension cannot distinguish them. Reviewers face a forced choice at the boundary. **Root cause:** Authors combined related properties to reduce the number of dimensions. **Correction:** Split into two dimensions. Each criterion should be independently falsifiable — a specific artifact configuration that passes D_i but fails D_j must be constructable.

### AP-RQ-4 — The gated gate

**Symptom:** A `[gate]` dimension says "PASS if the description is sufficient for routing accuracy." "Sufficient" requires expert judgment; this is a `[review]` criterion mislabeled as `[gate]`. **Root cause:** Authors want the certainty of a gate label without the effort of specifying a mechanical check. **Correction:** Replace the vague `[gate]` check with a mechanical one ("routing corpus F1 ≥ 0.70 on a 20-phrase eval") or relabel as `[review]` and add level descriptors with behavioral anchors.

---

## §Hard Tests

1. **The label audit test:** List every dimension. Count those without a `[gate]`/`[review]`/`[hypothesis]` label. Count > 1: D1 fails.

2. **The gate execution test:** For each `[gate]` dimension: run the check mechanically (script, grep, count). If any check requires expert judgment to execute: mislabeled as `[gate]`. Count mislabeled > 2: D2 fails.

3. **The behavioral anchor test:** Read every level descriptor. Count those where the only distinguishing content is an adjective without a behavioral observation. Count > 3: D3 fails.

4. **The conflict test:** For each pair of dimensions: name a concrete artifact that passes D_i but fails D_j. If no such artifact exists for a pair: conflated. Count conflated pairs > 1: D4 fails.

5. **The hypothesis plan test:** List every `[hypothesis]` dimension. Verify each has (a) metric, (b) sample size, (c) baseline, (d) judgment rule. Any missing: D5 fails.

6. **The calibration test:** Apply the rubric with a second independent reviewer. For each `[review]` dimension: agree within 1 point? Count disagreements > 1 point: failing > 2 dimensions: D6 fails.
