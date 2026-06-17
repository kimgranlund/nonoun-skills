# Description craft — before/after rewrites that move precision or recall

The A and B axes tell you *what* is wrong (a recall hole, a precision hole, an overclaim); this is the
*how* — concrete edits that move the metric, and the trigger-phrase patterns that make a description
routable. Every rewrite below names which gate it fixes and which way the metric moves.

## The shape a routable description has

Front-loaded WHAT, an enumerated WHEN, a named NOT-for:

```
<capability verb> + <object>, <how/axes>. Triggers on: "<phrase>", "<phrase>", "<phrase>", … .
NOT for <sibling territory> (<named sibling>).
```

The WHAT is what the human anchors on and the classifier's strongest signal; the quoted triggers are
the concrete landing points for varied phrasings; the NOT-for is the precision fence.

## Fixing a RECALL hole (under-trigger) — add trigger words

**Symptom:** the eval lists *missed positives*; the skill never fires on real requests.
**Move:** add the vocabulary the missed phrasings use — usually a whole *family* (diagnostic, symptom)
the description skipped. Recall ↑.

> **Before** (one phrasing — imperative only):
> `Grades a skill's frontmatter description for routing quality. Triggers on: "grade this description".`
> The eval misses "why doesn't my skill fire", "it triggers on everything", "score the precision of
> my routing" — three families, none covered. Recall ~0.3.
>
> **After** (families covered):
> `Grade and decompose a skill's frontmatter description — the routing surface that decides when it
> triggers. Triggers on: "grade this description", "why doesn't my skill fire", "why does it
> over-trigger", "score the precision and recall of my routing", "build a routing corpus". `
> The added diagnostic ("why doesn't my skill fire") and symptom ("over-trigger") words land the
> missed positives. Recall → ~1.0, F1 up.

**Rule:** every missed positive points at one or two words to add. Add the *word the request uses*,
not a synonym you prefer.

## Fixing a PRECISION hole (over-trigger) — fence the scope

**Symptom:** the eval lists *grabbed negatives*, especially a sibling's phrases; the skill steals
requests. **Move:** add a NOT-for that names the sibling and/or drop the over-general clause that
overlaps the negative. Precision ↑.

> **Before** (no fence, over-general WHAT):
> `Improve, grade, score, audit, and optimize skills and descriptions for quality and correctness.`
> Grabs "author a new skill" (→ skills-studio), "grade this code" (→ code-decomposer), "audit my
> tokens" (→ maintain-tokens). Precision ~0.4.
>
> **After** (narrowed WHAT + named fence):
> `Grade the routing surface of a skill — its frontmatter description's precision and recall.
> Triggers on: "grade this description", "is my description routing right". NOT for authoring or
> optimizing a whole skill end to end (skills-studio); NOT for grading code (code-decomposer) or
> tokens (maintain-tokens).`
> The narrowed object ("the *description's* precision/recall", not "skills") plus the three named
> NOT-fors repel the negatives. Precision → ~1.0, F1 up.

**Rule:** every grabbed negative points at a fence to add (name the sibling) or an over-general clause
to cut. Do **not** raise the eval threshold — that drops positives with the negatives.

## Fixing an OVERCLAIM (A1, the `routes accurately but misleads` quadrant)

**Symptom:** the eval is *green* (triggers land), but the capability claim promises more than the
skill does — the corpus can't see this. **Move:** rewrite the WHAT to match what the skill actually
delivers. Metrics unchanged; honesty restored.

> **Before** (overclaim): `Automatically optimizes any skill description for perfect routing.`
> The skill only *measures and reports*; it doesn't auto-optimize. A user invokes it expecting a
> rewrite and gets a scorecard.
>
> **After** (honest): `Measure and grade a skill description's routing (precision/recall against a
> corpus) and report the wording to fix.`

This edit is invisible to `routing-eval.py` by design — it's the honesty gate (A1) you verify against
the skill's real behavior, not the corpus.

## Trigger-phrase patterns (the A3 toolkit)

Cover these families; each is a distinct region of the invocation space that shares few words with the
others:

| Family | Pattern | Example for a "grade X" skill |
|---|---|---|
| **Imperative** | `<verb> this <object>` | "grade this description" |
| **Diagnostic** | `why does/doesn't <symptom>` | "why doesn't my skill fire" |
| **Symptom** | `<bad behavior> phrasing` | "it triggers on everything" |
| **Quality-question** | `is this <object> <good>?` | "is this description routing right" |
| **Object-first** | `this <object> — <ask>` | "this description — does it over-trigger" |
| **Indirect** | symptom without the verb | "my new skill never gets used" |

A description that quotes one phrase from each family is robust (B4) and stable (B5); one that quotes
six imperatives is brittle.

## Anti-patterns the lint flags (and the fix)

- **First-person / author voice** — "I will help you…", "my skill enables you to…". The classifier
  matches the *request*, not the author. → Third-person imperative: "Grade…", "Use when…".
- **Vagueness words** — "powerful", "comprehensive", "various", "and more", "leverage". Zero routing
  signal, spent budget. → Replace each with a capability verb or a quoted trigger.
- **Category instead of phrase** — "handles routing tasks". A category is not a landing point. →
  Quote the actual requests: "grade this description", "score the routing".
- **No NOT-for** — guarantees precision leakage onto neighbours. → Add the named fence.
- **Over-budget (>1024)** — a hard FAIL. → Cut the filler first (it's usually the vagueness words and
  a restated WHAT); every clause must earn routing signal.

## The loop

Edit the wording → `bin/description-lint.py` (structural floor) → `bin/routing-eval.py` (coverage) →
read the named misses/grabs → edit again. Two or three passes turns a `reads well, mis-routes`
description into a SHIPPABLE one, with the metric movement to prove it.
