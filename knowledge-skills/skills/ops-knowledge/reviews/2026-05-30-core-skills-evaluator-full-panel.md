---
date: 2026-05-30
reviewer: core-skills-evaluator v0.1.5 (full-panel, 9 critics)
target: ops-knowledge v1.0.0
mode: full-panel
status: open — findings for triage (not confirmed defects)
---

# Review — ops-knowledge · core-skills-evaluator 9-critic full panel

> Produced by `core-skills-evaluator` (9-critic) on 2026-05-30, reading `ops-knowledge` cold
> (SKILL.md, skill.json, ROADMAP.md, CHANGELOG.md, file tree). Adversarial inputs for triage.
> **The strongest ops-* skill** — mature (v1.0.0), design-sound; its First Principles are the
> shape the thinner siblings should adopt.

## Strengths (the family exemplar)
The **First Principles** pre-satisfy several critics by construction:
- *Idempotent by default* ("UPSERT safer than INSERT+UPDATE because idempotent") — **Farley**.
- *Show the diff before commit* — **Huyen** (human gate on irreversible writes).
- *The chat is not the source of truth* + the "treating chat as canon" anti-pattern — **Simon**
  (treats conversation as untrusted relative to persisted files — a real trust boundary).
- *Identity before update* — **Wlaschin** (refuses to operate without resolving which entry → an
  illegal state ("update with no identity") is structurally prevented).
- Plus: Output Format, a 7-point Quality Checklist (incl. an idempotency check), strong anti-patterns,
  `peer_skills` + real tags + 4 reference files. This is *not* a thin skill.

## Standing findings
- **Elon [Major]** — 11-verb vocabulary contains near-synonym pairs: UPSERT/APPEND, MERGE/DEDUPE,
  SUPERSEDE/RETRACT. Designed-not-emerged risk. Justify each verb's distinct semantics or collapse the
  pairs — a smaller vocabulary is easier for the agent to route correctly.
- **Charity [Major]** — No **operation ledger**. Per-entry provenance is required (good), but there's
  no queryable history of *operations* applied to the knowledge base (ops-repo has `audit-history/`;
  ops-memory logs reconciliations at step 7). You can see why an entry looks the way it does, but not
  replay what the skill has done over time.
- **Boris / Wlaschin [Minor]** — The CHANGELOG `### Files` block (lines 37-43) duplicates
  `skill.json` `files[]` **and** has already drifted from it (omits `ROADMAP.md`). Two sources of
  truth for the file list; delete the CHANGELOG copy.
- **Boris [Minor]** — No routing eval corpus; `§SelfAudit` is not named (the Quality Checklist
  substitutes acceptably).
- **Simon [Minor]** — The "external doc" source path (Ingestion) has no untrusted-content guard;
  "chat is not source of truth" covers chat, not a fetched/pasted external doc that could carry
  injected directives.

## Synthesis
- **No Critical** — mature, well-designed, the family exemplar.
- **Top 3:** (1) trim/justify the verb vocabulary (Elon); (2) add an operation ledger (Charity);
  (3) single-source the file list + add a routing eval (Boris/Wlaschin).
- **Cross-skill recommendation:** promote these First Principles into a **shared ops-* skill
  template** and bring ops-memory / ops-postmortem up to it.
- **Coverage gaps:** none of note — engages all nine lenses, several positively.
