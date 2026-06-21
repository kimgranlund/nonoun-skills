# A · The AIM axis — are we aiming at the right thing?

The AIM axis grades **intent**, top-down: from the diagnosis of the challenge down to the bounded set of
ranked goals it implies. This is the axis `charter-check.py` **cannot see** — a measurability linter is
silent on *"these are crisply-measured goals aimed at the wrong outcome."* It is also where an LLM fails
silently (a confident, well-written goal set that never faces the actual challenge), so it carries an
**adversarial Goodhart probe**, not just a checklist.

The named canon below is the OUTSIDE-IN counterpart to `architecture-decomposer`'s INSIDE-OUT canon —
the conventions distinguished strategists and product leaders cite. The skill *operationalizes* the
standard vocabulary; it doesn't invent one.

## A1 · Diagnosis `[gate]` — face the challenge

Before any goal, name **the challenge actually being faced** — what is wrong, what is the obstacle, why
now. *(Rumelt, the strategy kernel: **diagnosis → guiding policy → coherent action**.)*

- **Gate failure — `NO_DIAGNOSIS`:** the charter lists aspirations with no diagnosis. This is the first
  of Rumelt's **four hallmarks of bad strategy** — *mistaking goals for strategy*. A goal set with no
  diagnosis gives the architecture nothing to be coherent *against*; you can't tell what the goals are
  even *for*.
- **What good looks like:** a sharp diagnosis ("cart abandonment spikes at peak because checkout p99
  degrades under load and one failure takes the whole flow down") that the goals then *answer*. Every
  characteristic should trace back to it (`UNTRACED_GOAL` warns when one doesn't).

## A2 · Ranked characteristics `[gate]` — a strict priority order

The **architecture characteristics** (the *-ilities*: scalability, resilience, evolvability, security,
operability, cost, …) are the goals an architecture is held to. They must be a **strict priority order**.

- **Gate failure — `UNRANKED`:** ties, especially at the top. *If everything is a priority, nothing is*
  — and the architecture can't make the trade-off the ranking is supposed to force. **Everything is a
  trade-off** (Ford/Richards): the rank is what tells the INSIDE-OUT work which -ility wins when two
  collide. A charter with five rank-1 goals has made no decision.
- **The test:** for the top two characteristics, name the trade-off between them and which wins. If you
  can't, they aren't really ranked.

## A3 · Outcomes, not outputs `[review]`

Each goal must be an **outcome** — a measurable change in user or system behavior — not an **output** (a
feature shipped). *(Perri, *Escaping the Build Trap*; Seiden, outcomes over outputs.)*

- **Weak signal — `OUTPUT_NOT_OUTCOME`:** a goal phrased "ship X / add Y / build Z." Shipping the thing
  isn't the goal; the *change it causes* is. "Launch the new dashboard" is an output; "a PM answers a
  revenue question without filing a data request" is the outcome.
- A charter full of outputs is a feature factory's backlog wearing a strategy's clothes.

## A4 · Coherence & scope `[review]` — non-goals and no contradictions

- **Coherent action** (Rumelt): the goals don't fight each other. Two characteristics that can't both be
  maximized must be *ranked* (A2), not both claimed. A non-goal that excludes something the charter also
  pursues is a `CONTRADICTION`.
- **Explicit non-goals** bound the scope. `NO_NONGOALS` warns when scope is unbounded — *what this is
  NOT* is half of what makes a charter governable. Rumelt's "blue-sky objectives" (a wish list with no
  edges) is a bad-strategy hallmark.

## A5 · Falsifiable success `[review]` — the acceptance criteria

The acceptance criteria are the charter's **definition of done** — each a checkable predicate, each
tracing to a ranked characteristic. (Their *mechanical* well-formedness — does each carry a number — is
graded on the B axis; here, judge whether they actually *capture* the goal.) Borrow **SMART** as the
floor (specific, measurable, achievable, relevant, time-bound) and the **OEC** discipline (Kohavi): one
overall evaluation criterion the work is steered by, with guardrail metrics so you don't win the metric
and lose the business.

## The adversarial Goodhart probe (the dangerous quadrant)

Because *precise but wrong* hides behind a green measurability gate, send the charter's top metrics to a
**skeptic in a fresh context** and have it try to break each one:

- **Surrogate / Goodhart:** could you move this metric *without* delivering the outcome it stands for?
  (A "time on page" metric that goes up because users are *lost*, not engaged.)
- **Output disguised as outcome (A3):** is the "success" actually a feature being live, renamed?
- **Twyman's law / too-good number:** any metric that's trivially already-passing is measuring nothing.
- **Unfaced challenge (A1):** does the whole goal set actually answer the diagnosis, or dodge it?

Any hit is an AIM finding the measurability linter is blind to — the *precise-but-wrong* quadrant.
Default to "the metric is a surrogate" until it survives the probe.
