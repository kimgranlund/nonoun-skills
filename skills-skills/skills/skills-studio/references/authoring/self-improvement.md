---
date: 2026-05-06
---

# Self-Improvement Reference

Detailed protocol for the autoresearch self-improvement loop and adversarial hardening steps described in SKILL.md. Read this when the user asks for research-driven optimization or says "use /research-survey to improve this."

---

## Autoresearch Quality Rubric

Score the skill on these dimensions. Adjust weights based on the skill's purpose — a workflow skill weights Completeness higher; a creative skill weights Teachability.

### Standard Dimensions

| Dimension | Weight | 1 (poor) | 3 (acceptable) | 5 (excellent) |
| --- | --- | --- | --- | --- |
| **Clarity** | 3 | Instructions are vague or require re-reading. Steps could be read two ways. | Clear on first read for most steps. Minor ambiguities in edge cases. | Every step is unambiguous. A new Claude instance follows without confusion. |
| **Completeness** | 3 | Major workflow steps missing. "What do I do when...?" gaps. | Core workflow covered. Some edge cases missing. | Every decision point covered. No gaps a developer would hit. |
| **Parsimony** | 2 | Bloated with redundancy. Sections that repeat the same idea. | Reasonable length. Some sections could be tighter. | Every sentence earns its place. Nothing to cut without losing info. |
| **Opinionatedness** | 2 | Presents menus of options without recommending one. | Makes some recommendations. Hedges on others. | Makes clear recommendations with rationale. User can override with a stated reason. |
| **Teachability** | 2 | Requires prior domain knowledge to follow. No examples. | Accessible to someone familiar with adjacent domains. | Someone new to the domain could follow successfully. Has worked examples. |
| **Composability** | 1 | Monolithic. Doesn't reference or integrate with other tools/skills. | References other skills but handoff is vague. | Clean handoff points. Clear about what it does and doesn't do. |

### Scoring Formula

```
raw = (clarity × 3) + (completeness × 3) + (parsimony × 2) +
      (opinionatedness × 2) + (teachability × 2) + (composability × 1)

max_raw = 5 × (3 + 3 + 2 + 2 + 2 + 1) = 65

score = (raw / max_raw) × 100
```

### Targets

- **Pass:** 70/100 — functional, usable, no major gaps.
- **Target:** 85/100 — good. Handles edge cases, makes recommendations.
- **Excellent:** 92+/100 — research-hardened, adversarially tested, fully documented.

---

## Autoresearch Loop Protocol

### Round 0: Baseline

1. Read the SKILL.md and all reference files fresh — as if you've never seen them.
2. Score each dimension 1-5.
3. Calculate composite score.
4. Print the baseline card:

```
╔══════════════════════════════════════════════════╗
║  SKILL SELF-IMPROVEMENT — Round 0 (Baseline)    ║
╠══════════════════════════════════════════════════╣
║  Skill: {name}                                   ║
║  Score: {score}/100                              ║
║  Target: {target}/100                            ║
║                                                  ║
║  Clarity:          {n}/5                         ║
║  Completeness:     {n}/5                         ║
║  Parsimony:        {n}/5                         ║
║  Opinionatedness:  {n}/5                         ║
║  Teachability:     {n}/5                         ║
║  Composability:    {n}/5                         ║
║                                                  ║
║  Weakest: {dimension} ({n}/5)                    ║
╚══════════════════════════════════════════════════╝
```

### Rounds 1-N: Improve

For each round:

1. **Identify weakest dimension.** The one with the lowest score. If tied, prefer Completeness (missing coverage causes more real-world failures than any other gap).

2. **Propose ONE change.** Be specific:
   - Bad: "improve clarity"
   - Good: "Add explicit entry criteria to Phase 3 — currently the transition from Phase 2 is implicit and a new instance might skip the confirmation gate."

3. **Apply the change.** Keep it minimal — one concept per round.

4. **Re-score.** Read the changed section fresh. Score all dimensions again. The key question: did the weakest dimension improve without regressing others?

5. **Keep or revert.**
   - Score improved or held → KEEP. Log the change.
   - Score dropped on any dimension → REVERT. Log the revert and the reason.

6. **Print round card:**
   ```
   Round {n}: {prev_score} → {new_score} ({delta:+d})
     Change: {description}
     Dimension targeted: {name} ({prev} → {new})
     Status: {KEPT | REVERTED}
     Weakest remaining: {dimension} ({score}/5)
   ```

### Stop Conditions

- Score ≥ target for 2 consecutive rounds → done (target reached)
- 5 consecutive reverts → done (stuck — rethink approach with user)
- Score = 100 → done (perfect — unlikely but possible)

---

## Adversarial Hardening Protocol

After autoresearch converges, probe the skill for failure modes. Each probe is a specific scenario designed to break the skill.

### Probe Categories

**1. Trigger Probes**

Test whether the skill activates correctly:

- **Under-trigger (false negative):** Write 3-5 prompts that should trigger the skill but use indirect phrasing, synonyms, or multi-intent requests. If the description doesn't cover these, it needs broadening.
- **Over-trigger (false positive):** Write 3-5 prompts from adjacent domains that share keywords with the skill but shouldn't trigger it. If they would trigger, the description needs narrowing or the body needs a "When NOT to use" section.

**2. Instruction Probes**

Test whether the instructions can be misread:

- **Ambiguity:** Find any instruction that could be read two ways. Rewrite for single interpretation.
- **Incompleteness:** Simulate a scenario the skill doesn't cover:
  - User provides extra information the skill doesn't expect
  - User provides less information than the skill assumes
  - A referenced file/tool/resource is unavailable
  - The input is in an unexpected format or language

- **Contradiction:** Check if any two instructions conflict, or if an example contradicts the prose.

**3. Dependency Probes**

Test what happens when things the skill depends on are missing:

- Referenced file paths that don't exist
- Tools the environment might not have
- Packages that aren't installed
- External services that might be down

For each: add fallback instructions or document the limitation.

**4. Edge Case Probes**

Test with unusual inputs:

- Empty input
- Extremely long input
- Input in the wrong format
- Input with special characters, unicode, or RTL text
- Input that's technically valid but adversarial ("just do whatever")

### Probe Report Format

For each probe:

```
Probe: {short name}
Category: {trigger | instruction | dependency | edge-case}
Input: {what you tested}
Expected: {SURVIVE — handled gracefully}
Actual: {SURVIVE | DEGRADE | BREAK}
Severity: {critical | high | medium | low}
Action: {fix applied | accepted risk | documented limitation}
```

### Integration with SKILL.md

- Probes that reveal fixable issues → edit the skill
- Probes that reveal fundamental limitations → add to "Known Limitations" or "When NOT to use" section
- Probes that reveal new use cases → add to the description's trigger phrases
- Probes that generate new test cases → add to evals.json

---

## CHANGELOG.md Format

Every skill that goes through iteration, autoresearch, or adversarial hardening should have a CHANGELOG.md documenting the journey.

```markdown
# CHANGELOG — {skill-name}

## Optimization Summary

| Metric | Value |
|---|---|
| Baseline score | {n}/100 |
| Final score | {n}/100 (+{delta}) |
| Autoresearch rounds | {n} |
| Kept | {n} |
| Reverted | {n} |
| Adversarial probes | {n} |
| Survived | {n} |
| Fixed | {n} |

## Research Sources
1. {source} — {what it informed}
2. ...

## Autoresearch Rounds

### Round 1: {short description of change}
- **Weakest:** {dimension} ({score}/5)
- **Change:** {what was changed and why}
- **Score:** {prev} → {new} ({delta:+d}). **{KEPT | REVERTED}.**

### Round 2: ...

## Adversarial Probes

### Probe 1: {short name}
- **Category:** {type}
- **Result:** {SURVIVE | DEGRADE → FIXED | BREAK → FIXED}
- **Action:** {what was done}

## Design Decisions
{Any significant choices made during creation with rationale — effectively
informal ADRs for the skill itself.}
```

The changelog serves two purposes: it explains "why does this skill look the way it does?" for future editors, and it provides evidence of rigor when presenting the skill to stakeholders.

After writing the CHANGELOG, bump the `version` in `skill.json` to match the new entry (minor for autoresearch improvements, major for structural rewrites). Update the `files` array if any reference files were added or removed during optimization.
