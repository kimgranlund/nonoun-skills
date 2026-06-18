# meta-expert-author — Holistic 10-dim + 9-critic full panel (2026-05-31)

**Method:** two **fresh-context** subagents (blind) — a `skills-holistic` v0.2.0 (D1–D10) scorecard + a
9-critic adversarial panel — run with a **root-cause probe**: *does this authoring standard mandate the
four things downstream expert skills keep shipping without* (trust boundary, calibrated rubrics, Verify
Target, eval corpus)? All Criticals verified against the files. **Target:** meta-expert-author v1.6.0
(`status: complete`).

## Verdict

**Overall 3 / 5 — and this is the most consequential review in the campaign: meta-expert-author is the
systemic ROOT CAUSE of the recurring D7/D3/D5 gaps in the library's expert skills.** It is the standard
the expert-knowledge skills (`ref-*`, `core-brand-studio`, `core-mcp`) are stamped from, it is marked
`complete`, and it makes the missing artifacts **optional (evals), absent (injection guard), or
unmeasured (rubrics)**. Clears the bar overwhelmingly: **2 Criticals + ~8 Majors.** Strong where a
knowledge-authoring methodology naturally optimizes (D1/D2/D9/D10 — discoverability, control-mode fit,
progressive context, plan structure); failing on the contract/verification dimensions it propagates.

### Root-cause probe — confirmed (3 of 4 gaps inherited by design)

| Downstream gap | Mandated by the standard? | Evidence |
|---|---|---|
| (a) Trust boundary / injection guard | **NO** | Authoring loop fetches arbitrary web pages + transcribes video transcripts into refs; verification discipline is about *factual accuracy* only. Sole injection mention is 2 lines in the **optional, internal-skip** `publishing-trappings.md` SECURITY.md boilerplate. |
| (b) Calibrated / measured rubrics | **NO** | `maintenance-and-evals.md` ships prose pass/fail criteria with no two-reviewer calibration protocol; Invariant 9 `[hypothesis]` is fact-replication labeling, not rubric calibration. |
| (c) Verify Target | **PARTIAL (the one win)** | Invariant 10 (v1.6.0) requires a `## Verification Posture` *statement* — a self-classification, not a target on external state. |
| (d) Eval / routing corpus | **NO — explicitly downgraded** | `evals/` is "optional but strongly recommended," **public-release-only**; internal skills "Skip." The flagship exemplars (ref-dashboard, ref-typography) are sanctioned to ship with zero evals. |

The downstream expert skills are missing exactly these because the standard never mandates them — **the
gaps are inherited, not incidental.**

## Holistic scorecard

| Dim | Name | Score | Finding |
|---|---|---|---|
| D1 `[review]` | Instructions & Harness | 4 | Minor — strong description/router/mode-menu; **no real §SelfAudit** (the "§SelfAudit equivalent" is Invariant 11's manual eyeball test); 170-line first screen |
| D2 `[review]` | Control Mode | 4 | Pass — mode-appropriate; the fixed "5 waves not optional" is mildly over-specified |
| D3 `[gate][review]` | Rubric Quality | 2 | **Major** — eval criteria are asserted prose, no calibration protocol; standard never tells produced skills to label/calibrate quality criteria |
| D4 `[gate]` | Mechanization | 2 | **Major** — **no `scripts/`**; URL-rot "script" described but never ships; validation checklist is manual mechanize-bait; never wires to the repo's `check-skill-metadata.py` |
| D5 `[gate]` | **Evaluation** | 2 | **Critical** — no corpus/F1/baseline; standard makes evals optional+public-only → every internal expert skill born eval-less. Structurally hides D3 + D8 |
| D6 `[review]` | Extensibility | 3 | Minor — its **own ROADMAP is template-only** while CHANGELOG carries "Known gaps (still deferred)" → fails its own pollution rule; but defines a real refresh path for produced skills |
| D7 `[gate]` | **Security & Trust** | 1 | **Critical** — dispatches agents that WebFetch arbitrary URLs + Write files in one context; **zero injection guard / scope / blast-radius**. AP-H3 "trusted content reader" |
| D8 `[review]` | Observability | 2 | **Major** — success = "all ⬜→✅" (files exist) + a human reading the CHANGELOG; no run report, no per-invocation audit |
| D9 `[review]` | Context Engineering | 4 | Pass — exemplary progressive disclosure + mandatory `date:` freshness + URL audit |
| D10 `[review]` | Plan Anatomy | 4 | Pass — the wave arc has verifiable per-subgoal state (INDEX ⬜→✅), explicit deps, a pre-dispatch gate; completion closes on internal state |

## Verified findings beyond the scorecard

- **[Major · verified · FIXABLE] Hardcoded absolute path propagated into agent prompts.**
  `references/agent-dispatch/agent-brief-template.md:21` hardcodes `/Users/kimba/.claude/skills/[skill-name]/…`
  — copied verbatim into every dispatched agent's prompt. Violates the library's own "No absolute paths
  (`/Users/…`)" hard rule (AGENTS.md), and **the repo metadata gate does not catch it** (reports clean —
  it doesn't scan reference-file bodies for absolute paths). The producer ships the exact anti-pattern it
  forbids the produced skills from containing. *(Reconciled inline this pass.)*
- **[Major · verified] `status: complete` mislabel (Wlaschin).** Declared `complete` while its own
  CHANGELOG lists "Known gaps (still deferred)" incl. "No eval currently checks whether a produced
  decomposition is covering + non-overlapping." `complete` = "all planned prose written," not "validated."
- **[Major · verified] No mechanical detector for its one real production failure (Farley).** The
  fabricated "WebKit Bug 241691" was caught by *manual* audit; the fix was a warning paragraph, not a
  link-checker. The verification lesson never became a gate.
- **[Minor · verified] 56 tags** on a meta-skill invoked by name — ceremony copied from the produced-skill
  convention into the producer (Elon).

## Prioritized fixes (the standard-level changes — the high-leverage ones)
1. **Add an authoring-time trust boundary** to `verification-discipline.md` + the agent-brief boilerplate:
   fetched pages / transcripts are **untrusted data, never instructions** — quote, never execute. *(closes
   the D7 Critical at the standard level → fixes it for every future expert skill)*
2. **Promote `evals/` from optional-public-only to required for any reusable skill**, with a stored
   answer-quality corpus + pass-rate floor as the v1.0.0 gate (replacing "all ⬜→✅"). *(closes D5/D3/D8 +
   Cherny/Karpathy/Huyen)*
3. **Make the four artifacts (trust boundary · calibrated bar · Verify Target · eval corpus) invariants**
   in `## Invariants this skill enforces`, and ship a `scripts/`-backed gate. *(turns the standard from
   asserted to enforced)*
4. **Demote `status: complete` → `stable`** (or add "validated: manual cold-start only") to stop the
   mislabel. **Fix the absolute path** (done inline).

## Disposition
Findings tracked in `meta-expert-author/ROADMAP.md` (Planned) + repo-root `BACKLOG.md`. The absolute-path
violation is reconciled inline. The standard-level mandates (fixes 1–3) are **systemic design changes
deferred for explicit approval** — they would change how every future expert skill is authored.
