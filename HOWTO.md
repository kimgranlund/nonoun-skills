# HOWTO — author a decomposer skill

How to add a skill to `nonoun-skills`. Most skills here are **decomposers**; this guide is the
recipe for one, plus the contract every skill (decomposer or not) must satisfy. Read two existing
decomposers first as your template — they are the reference implementation:

- `design-skills/skills/component-decomposer/` — a rich geometry gate (`bin/geometry-check.py`).
- `code-skills/skills/code-decomposer/` — a toolchain harness + a static linter (two `bin/` tools).

The one gate that proves your skill ships: `python3 bin/check-skills.py`.

## 1. Design the two axes

A decomposer grades an artifact on **two independent axes that walk the same hierarchy in opposite
directions**, crossing at one seam. Before writing anything, name them:

- **Intent axis (A · whole → part)** — *"is it the right thing?"* The claim, the structure, the
  naming. Walk top-down: the biggest decision first (it cascades), the details last.
- **Mechanism axis (B · part → whole)** — *"does it actually work / hold / render, here?"* The thing
  that compiles, validates, renders, executes. Walk bottom-up: does the smallest piece even parse,
  up to does the whole behave.
- **The crossing seam** — the one artifact that is *both* the claim and the mechanism (a component
  contract, a diagram type, a query-against-a-schema, a type's state space). The whole technique
  lives here.
- **The opposite-defect quadrant** — name both failures. A passes / B fails = *"right idea, doesn't
  work"*; B passes / A fails = *"works, but wrong / won't compose / unsafe"*. They need **opposite
  fixes**, which is why you **score the two axes separately and never average them**.

Then lay out **5 levels per axis** (A1–A5, B1–B5). The first two of each axis are usually **gates**
(`[gate]`); the rest are **reviews** (`[review]`, 1–5). Gates **cascade** — a failed gate blocks the
reviews below it on that axis (you can't grade the legibility of something that won't render). A
shippable artifact is **≥4 on every review with zero gate failures**, reported as two scores + the
quadrant cell.

Every decomposer runs three modes: **DECOMPOSE** (read & grade), **CREATE/DESIGN** (author), **GRADE**
(score against the rubric).

## 2. Route the mechanism axis to code — gate where you can, verify where you can't

This is the repo's core principle: **computation routes to code, never inference.** An LLM grades the
intent axis well but fails the mechanism axis *silently* (it hallucinates that code compiles, that a
test passes, that a value is grounded). So:

- **Mechanize the mechanism gates** in a `bin/*.py` tool — a renderer, a compiler harness, a
  validator, a static linter. Deterministic, stdlib-only, self-tested.
- **For the dangerous axis a gate can't see** (a hallucinated value, an illegal state, a circular
  proof, a misleading description), pair the gate with a **fresh-context adversarial check**: a
  skeptic prompted to *find the counterexample*, separate from the author's context. A verifier that
  shares the author's context rubber-stamps it.
- **Be honest about the gate's reach.** A static linter (regex ReDoS, SQL smells, secret detection)
  is a *lossy pre-filter*, not a complete oracle — say so in the skill, don't overclaim a clean run
  as proof. (See §7: the review pass exists because shallow gates lie.)

## 3. The files

```
<plugin>/skills/<skill-name>/
  SKILL.md            # the routing surface + table-of-contents over references/
  skill.json          # name (== dir), version, the files[] manifest
  CHANGELOG.md
  ROADMAP.md
  references/
    decomposition-method.md   # ALWAYS FIRST — the two axes, the gated walk, the quadrant, the modes
    <axis-a>.md               # the intent-axis playbook (+ the adversarial probe)
    <axis-b>.md               # the mechanism-axis playbook (+ how to read the gate)
    <centerpiece>.md          # the skill's signature reference (the toolkit / catalogue)
    <domain>.md               # dialects, families, type systems — whatever the domain needs
    policy.md                 # definition-of-done, the artifact "card" shape, handoff seams
  bin/
    <mechanism-gate>.py       # stdlib, a `selftest` subcommand, exit 0
```

**SKILL.md sections, in order** (match the exemplars): frontmatter → H1 + intro (the two axes, the
crossing seam, the opposite-defect pair, one line on why it's outsized for an LLM) → `## Quick Start`
(You bring / You get + a worked walkthrough using `[gate]`/`[review]` markers + a `**Modes:**` line)
→ `## The two axes (the method)` table → a doctrine/centerpiece callout → `## §SelfAudit` (5–6
guardrail bullets) → `## Verify Target` (done when… / NOT done when…) → `## References` (load-when
table; `decomposition-method.md` is "always, first").

**The frontmatter `description` is the routing surface** — ≤ **1024 chars**, WHAT + WHEN + NOT.
Include concrete (quoted) trigger phrases and a `NOT for …` fence naming the siblings it could be
confused with. Verify the length:

```sh
python3 - <<'PY'
import re; t=open('SKILL.md').read()
fm=re.search(r'(?ms)^---\n(.*?)\n---',t).group(1)
b=re.search(r'(?ms)^description:\s*>\s*\n((?:[ \t]+.*\n?)+)',fm).group(1)
print(len(' '.join(l.strip() for l in b.splitlines() if l.strip())))
PY
```

## 4. The `bin/` contract

Each `bin/*.py`:

- is **stdlib-only** (no third-party imports) — the repo is clean-checkout-true.
- answers a **`selftest`** subcommand that exits **0** on pass, non-zero on fail. The gate runs it.
- mechanizes a real check, and proves it on **good *and* bad fixtures** in `selftest`.
- when it shells out to an external tool that may be absent (a renderer, a compiler), treats a
  **missing tool as a SKIP / INCOMPLETE — never a pass** (a skipped gate is no evidence). The static
  half still runs (and is self-tested) everywhere; the live half fires where the tool exists.

## 5. The hard contract (what `check-skills.py` FAILs on)

The gate discovers any `*/skills/*/` containing `skill.json` and **FAILs** if: `skill.json` doesn't
parse or its `name` ≠ the dir name; the SKILL.md `description` > 1024 chars; any `files[]` path is
missing on disk; a relative `.md` link *inside the skill* doesn't resolve; a `bin/*.py selftest`
exits non-zero; or the Mermaid keyword gate trips on a `references/` doc. It only **WARNs** on the
skills-studio structural floor (`## Quick Start` · `§SelfAudit` · `## Verify Target`) and on
cross-skill links. Keep `files[]` in sync with disk — a stray or missing file FAILs.

## 6. Register it

- **New skill in an existing plugin** — just create the `<plugin>/skills/<name>/` folder. The gate
  discovers it; no central registry. Optionally refresh the plugin's `plugin.json` description.
- **New plugin** — create `<plugin>/.claude-plugin/plugin.json` (copy an existing one: `name`,
  `version`, `description`, `author`, `homepage`, `license`, `keywords`) and add a `{name, source,
  description, category, tags}` entry to `.claude-plugin/marketplace.json`. The gate validates skills
  independently of plugin manifests, so a skill passes even before the plugin entry exists — but ship
  both.

## 7. Build order & the quality bar

1. **Write the `bin/` gate first** and get its `selftest` green — it's the deterministic core and the
   riskiest part. Author the `decomposition-method.md` doc to match exactly what the code computes.
2. **Write the references**, then **SKILL.md** (verify the ≤1024 description).
3. **`python3 bin/check-skills.py`** until green.
4. **Adversarially verify — a green selftest is necessary, not sufficient.** This repo learned the
   hard way: every decomposer passed the structural gate, but an adversarial review (running each
   tool with *hostile* inputs) found tools that certified the very thing they exist to catch as safe
   — a ReDoS bomb reported "clean", an invented value "grounded", `true` accepted for an int enum.
   The selftests were one-fixture-deep, so the false-negatives hid. Before you trust a gate:
   - craft inputs that **should** be caught and inputs that should **not**, and find the false
     positives *and* false negatives;
   - **lock every fix with the adversarial input as a new selftest fixture** so it can't regress;
   - document what the gate **can't** see in the skill, rather than overclaiming.
5. Commit (branch off `main` first), and update `CHANGELOG.md` for a marketplace-level change.

## Not a decomposer?

Two other vintages live here and are equally valid — the gate enforces the hard contract on all
skills and only *advises* on the decomposer template:

- **Reference skill** (e.g. `color-science`, `typography-lettering`) — *answers and points at a peer
  for output*; it doesn't generate. Uses `## Invocation` + domain sections + a tiered `references/`
  corpus instead of the two-axis template.
- **Domain build skill** (e.g. `figma-plugins`) — teaches how to build something specific, with its
  own `bin/` check. Follows the SKILL.md + references + bin shape but isn't a two-axis grader.

Either way: self-contained, `files[]` in sync, a self-tested `bin/`, and computation routed to code.
