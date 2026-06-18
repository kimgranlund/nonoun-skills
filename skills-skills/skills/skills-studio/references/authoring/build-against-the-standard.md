# Build against the standard — the bi-directional bridge

**The point of `skills-studio`: the same knowledge powers building _and_ evaluating.** When you `author` a skill you are not following a separate template and _then_ getting it scored — you build it **against the same rubric library, foundations, and critics** that `score` and `critique` use to judge it. This file is the bridge: for each holistic dimension it names what you **build from**, what it gets **scored with**, the **gate** the produced skill must ship, and the **critic** who will try to break it.

Read this at the start of any `author` or `edit` job. It turns "author a draft → then evaluate it" (a hand-off) into "author _as_ an evaluator would score it" (a shared standard).

## The 10-dimension bridge

The spine is `../rubrics/skills-holistic.md` (D1–D10). For each dimension:

| Dim | Build it from (foundation) | Score it with (rubric) | Ship-gate the produced skill must pass | Red-team lens |
| --- | --- | --- | --- | --- |
| **D0** Runtime Target | `../foundations/runtime-environment-foundations.md` | `../rubrics/runtime-compatibility.md` (D0–D2 always; D3/D4/D5 by scope) | `skill.json` has `"target": "agent"\|"chat"\|"both"`; §SelfAudit has matching runtime gates; tool refs consistent with declared target | Simon |
| **D1** Instructions & Harness | `../foundations/instructions-harness-foundations.md` | `../rubrics/harness-design.md` + `skills-authoring.md` | `## Quick Start` (first 50 lines) + `## Invocation` present | Boris |
| **D2** Control Mode | `../foundations/control-mode-foundations.md` | `../rubrics/prompt-control-modes.md` | each mode's control mode matches its task entropy (instruction/procedure/rubric/objective/mission) | Huyen |
| **D3** Rubric Quality | `../foundations/rubric-foundations.md` | `../rubrics/rubric-quality.md` | every scoring criterion labeled `[gate]`/`[review]`/`[hypothesis]` | Wlaschin |
| **D4** Mechanization | `../foundations/mechanization-foundations.md` | `../rubrics/mechanization-best-practices.md` | mechanize-bait (countable/repeatable/silent-fail checks) is scripted, not prose | Elon |
| **D5** Evaluation | `../foundations/eval-foundations.md` | `../rubrics/evaluation-workflows.md` | `evals/routing-corpus.json` (≥10 trigger + ≥5 adversarial), **scored** before the description locks | Boris / Karpathy |
| **D6** Extensibility | `../foundations/extensibility-foundations.md` | `../rubrics/skill-extensibility.md` | `ROADMAP.md` populated (Planned / Deferred / Out-of-scope), not template-only | Steve |
| **D7** Security & Trust | `../foundations/security-foundations.md` | `../rubrics/security-and-scope-containment.md` | `## §SelfAudit` with a trust boundary **iff** the skill ingests untrusted content (data-not-instructions) | Simon |
| **D8** Observability | `../foundations/observability-foundations.md` | `../rubrics/observability-and-telemetry.md` | `## Verify Target` names a real external signal, not "files present" / "tests pass" | Charity |
| **D9** Context Engineering | `../foundations/context-engineering-foundations.md` | `../rubrics/context-engineering.md` + `progressive-context-construction.md` | references load on explicit conditions (progressive disclosure), nothing front-loaded | Boris / Karpathy |
| **D10** Plan Anatomy | `../foundations/plan-anatomy-foundations.md` | `../rubrics/plan-anatomy.md` | the skill's procedure has verifiable subgoals + a checkpoint before any expensive/irreversible step | Wlaschin / Farley |

_Governance (`../foundations/governance-foundations.md` ⊨ `../rubrics/governance.md`) is cross-cutting and team-scale — it is **not** a per-skill holistic dimension; score it separately only for multi-author / runtime systems._

If the skill's **output is a document** (a report/PRD/spec generator), also build against the matching document-authoring rubric: `../rubrics/report-authoring.md` / `prd-authoring.md` / `spec-authoring.md` (claim→evidence traceability, source/trust boundary, BLUF, audience fit).

## How to use it while authoring

1. **Pick the dimensions the skill actually has.** Not every skill needs all ten (a single-mode utility may skip D2/D10). The `skills-holistic.md` §Scope says which are load-bearing for which skill type.
2. **For each live dimension, read its foundation before you write that part.** Build D7 from `security-foundations.md`, D5 from `eval-foundations.md`, etc. — so the draft is grounded, not guessed.
3. **Make each ship-gate true as you go**, not after. The gate column above _is_ the produced skill's `## §SelfAudit` checklist — `quick_validate.py --strict` enforces the structural ones (routing corpus, Verify Target, Quick Start, §SelfAudit presence, labels, ROADMAP).
4. **Then red-team your own draft** (next section) before declaring done.

## Build-time red-team — summon the critics on your _own_ draft

Authoring is not done at "passes `quick_validate.py`." Run `critique` on the draft you just wrote — the same 9-critic panel that `evaluate` mode uses, turned on your own output. This is self-review, so the cold-read/no-author-knowledge rule is relaxed, but the adversarial bar is not: push for ≥1 Critical or document why none exists.

**Stakes-tiered default:**

| When | Red-team pass |
| --- | --- |
| **Every produced skill, before ship** (the floor) | `critique single-critic simon` (trust boundary — the campaign's most recurring Critical) **+** `single-critic wlaschin` (structure, labels, illegal states). Cheap; catches the two highest-frequency failure classes. |
| **Pre-v1.0 / `stable` promotion**, OR the skill **ingests untrusted content**, OR it's a **multi-agent / orchestrator** | `critique full-panel` + synthesis — the full 9 lenses. The orchestrator case especially: a fan-out amplifies an injection, so Simon's lens compounds. |
| **A targeted edit** to one concern | the one or two critics who own that dimension (see the table's "Red-team lens" column). |

Fold the surviving Critical/Major findings back into the draft (the `edit`/`improve` step) before packaging. That is the loop closing on itself: **author → score/critique/eval → edit**, all inside one skill, over one shared body of knowledge.

## Why this matters

Without this bridge, `skills-studio` is two halves bolted together — an authoring toolkit and an evaluation toolkit that happen to share a directory. _With_ it, the authoring side draws on the **same foundations, rubrics, and critics** the evaluation side scores against, so a skill is built to the standard it will be judged by. That is the bi-directionality: not a hand-off, a shared standard.
