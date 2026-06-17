# The two-axis method — INSTRUCTION × ROUTING

A skill's **routing surface** — its frontmatter `description` — is **correct on two independent axes
that walk the same artifact in opposite directions** — the decomposer seam the layout-, mermaid-,
component-, and code-decomposers apply to space, diagrams, components, and code, here applied to the
one string that decides whether a skill triggers.

- **Instruction · whole → part (intent)** grades what the description *claims*: its capability → its
  scope → its triggers → its disambiguation from siblings → its economy. *"Does it say the right
  thing, honestly?"*
- **Routing · part → whole (mechanism)** grades how the description *behaves* as a classifier: it
  fires on on-target requests → holds against off-target ones → routes sibling requests to the
  sibling → survives paraphrase → stays stable across rewordings. *"Does it route the right
  requests, measurably?"*

They **cross at the description itself** — the same string is *both* the human-readable claim (what a
maintainer reads to know what the skill does) and the model's routing input (what the classifier
matches a request against). A description that reads beautifully but names none of the words real
requests use is fiction; one that routes accurately but lies about what the skill does is a trap.

That crossing is the whole technique. A description can be:

- **reads well, mis-routes** — Instruction passes (honest, well-scoped, fenced) but Routing fails:
  the model never triggers it on real requests (**under-trigger / low recall**) or grabs it for the
  wrong ones (**over-trigger / low precision**). The classic failure: prose tuned for a human
  reviewer, not for the classifier. *You cannot see this by reading — you must measure it.*
- **routes accurately but misleads** — Routing passes (fires and holds on the corpus) but Instruction
  fails: the triggers are concrete and land, but the capability/scope claim **overclaims** or is
  dishonest — the skill gets invoked correctly, then does less (or other) than promised.

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged.** An averaged score hides which one you have, and they need opposite work: routing wants
*more / better trigger words* (or a tighter fence); instruction wants *an honest rewrite of the
claim*.

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Instruction** | whole → part | **A1** Capability `[gate]` → **A2** Scope `[gate]` → **A3** Triggers `[review]` → **A4** Disambiguation `[review]` → **A5** Economy `[review]` | "Does it say the *right thing*, honestly?" |
| **B · Routing** | part → whole | **B1** Fires `[gate, code]` → **B2** Holds `[gate, code]` → **B3** Boundary `[gate, code]` → **B4** Robustness `[review]` → **B5** Stability `[review]` | "Does it *route the right requests*, measurably?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it on
that axis. `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable description is **≥4 on every review
with zero gate failures**, reported as two separate axis scores plus the quadrant cell. The B gates
route to `bin/routing-eval.py`; the A gates are *honesty* judgments the eval cannot see (see the
doctrine).

### A · Instruction (whole → part) — the claim

- **A1 Capability `[gate]`** — states WHAT the skill does, *accurately, with no overclaim*. The
  classifier and the human both anchor here. A description that promises a capability the skill
  doesn't have is dishonest at the root and poisons every trigger under it.
- **A2 Scope `[gate]`** — the boundaries: an explicit **NOT-for** that fences the siblings this could
  be confused with. Without a fence, a description bleeds onto a neighbour's territory (the structural
  cause of over-trigger). Wrong scope ⇒ stop and re-scope.
- **A3 Triggers `[review]`** — concrete trigger phrases covering the *real invocation space*, not one
  pet phrasing. The model matches a request against these; one phrasing = one route in.
- **A4 Disambiguation `[review]`** — actively distinguishes from *named* sibling skills it competes
  with (e.g. "NOT for X (sibling), use that"). A fence (A2) draws the line; disambiguation names who's
  on the other side.
- **A5 Economy `[review]`** — ≤1024 chars, no filler, every clause earns routing signal. Vagueness
  words ("powerful", "comprehensive", "various") spend budget and add no signal.

### B · Routing (part → whole) — the behavior

- **B1 Fires `[gate, code]`** — on-target phrases route to it (**recall**). Measured: do the corpus
  positives clear the routing threshold against this description? Misses are recall holes.
- **B2 Holds `[gate, code]`** — off-target / adversarial phrases do NOT route to it (**precision**).
  Measured: do the corpus negatives stay below threshold? Grabs are precision holes.
- **B3 Boundary `[gate, code]`** — phrases that belong to a *sibling* route to the sibling, not here.
  This is precision against the *hardest* negatives: the sibling's own trigger language (run the eval
  with the sibling's description too, and confirm each boundary phrase scores higher there).
- **B4 Robustness `[review]`** — paraphrases and indirect / implied phrasings still route (a request
  that *describes* the problem without naming the skill's verbs).
- **B5 Stability `[review]`** — the route is consistent across rewordings; small changes to the
  request don't flip it in and out.

## The opposite-defect quadrant

```
                 B · ROUTING passes        B · ROUTING fails
A · INSTR    ┌────────────────────────┬────────────────────────┐
  passes     │      SHIPPABLE         │  reads well, mis-routes │
             │                        │  — honest & well-scoped,│
             │                        │  but under-triggers     │
             │                        │  (low recall) or        │
             │                        │  over-triggers (low     │
             │                        │  precision) on real     │
             │                        │  requests               │
             ├────────────────────────┼────────────────────────┤
A · INSTR    │ routes accurately but  │       REBUILD           │
  fails      │ misleads — triggers    │                         │
             │ land, but the          │                         │
             │ capability/scope claim │                         │
             │ overclaims / is        │                         │
             │ dishonest              │                         │
             └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs *wording for the corpus* (trigger words for the
missed positives, a tighter fence for the grabbed negatives) — work the eval can verify. Bottom-left
needs an *honest rewrite of the claim* — work the eval **cannot see**, because the eval reads the
description's surface, not whether the skill actually delivers it.

## The doctrine — measure routing, gate honesty on what the eval can't see

This is why the skill earns its place: **a description is a routing classifier, not prose — you
cannot eyeball its precision and recall.** Two complementary moves:

- **Route B to a deterministic eval.** `bin/routing-eval.py` scores precision / recall / F1 over a
  *labeled corpus* and lists the exact missed positives and grabbed negatives. Trust the
  measurement, not the read-through — a description that "obviously triggers right" routinely misses
  half its real phrasings. The eval is a transparent proxy for a model's routing (content-token
  overlap above a threshold); its job is to make recall/precision *legible and fixable*, phrase by
  phrase.
- **Gate A on honesty the eval can't see.** The eval reads the description's *surface* — it can tell
  you the words match requests, but **not** whether the skill actually does what the words claim.
  Capability overclaim (A1) and a missing scope fence's *truthfulness* (A2) are honesty judgments:
  you confirm them against what the skill actually delivers, not against the corpus. `routes
  accurately but misleads` is exactly the defect a corpus rubber-stamps. `bin/description-lint.py` is
  the cheap static pre-filter for the *structural* ingredients (WHAT/WHEN/NOT, trigger count, voice);
  the honesty call stays human.

**Build the corpus adversarially.** The negatives are the test. A corpus of obvious off-topic
negatives ("write me a poem") proves nothing — every description holds those. The decisive negatives
are the **sibling skills' own trigger phrases** and **near-misses** one word away from a positive.
A description that holds *those* has real precision. (Full corpus discipline in `eval-corpus.md`.)

## Modes

- **SPECIFY** (write / optimize a description) — start from the skill's true capability + a corpus.
  Walk Instruction-down (capability → scope → triggers → disambiguation → economy), draft, then run
  `routing-eval.py` against the corpus and iterate the *wording* until B1/B2/B3 pass — fix misses by
  adding trigger words, fix grabs by tightening scope / adding a NOT-for. Emit the description + the
  scored corpus + a scorecard.
- **DECOMPOSE** (read an existing description) — recover the *claimed* capability and scope (A1/A2),
  build or load the corpus, run the routing eval (B1/B2/B3), score the reviews; emit the scorecard +
  a gap list (e.g. *"reads well, but these 4 real phrasings never route — recall hole"*).
- **GRADE** — score both axes, gates first (run the lint + the eval), place in the quadrant, name one
  corrective per failure.

## Walk order (do not skip)

1. **A1 Capability / A2 Scope** — recover (or write) the honest claim and the NOT-for fence. Overclaim
   or no fence ⇒ fix the *claim* before measuring routing.
2. **Build / load the corpus** — positives across phrasings; negatives from sibling skills + near
   misses (adversarial). The corpus *is* the test; a weak corpus gives a flattering, useless score.
3. **B1/B2/B3 Routing** — run `routing-eval.py`. Below the F1 threshold ⇒ fix the **wording**
   (trigger words for misses, fence for grabs), not the corpus or the score. Re-run until it clears.
4. **B3 Boundary** — for each sibling, confirm the boundary phrases score higher against the
   *sibling's* description than against this one (the sibling owns them).
5. **Reviews** — A3–A5 then B4–B5, 1–5 each. Below 4 ⇒ name the single corrective.
6. **Report** — two axis scores, the quadrant cell, gate failures first; hand a whole-skill rewrite
   (if the skill itself, not just the description, needs work) to `skills-studio`.
