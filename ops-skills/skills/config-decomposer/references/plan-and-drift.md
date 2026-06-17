# The plan is the contract — why a green parse proves nothing

This is the centerpiece. The whole skill exists because an LLM (and a hurrying human) produces the
**valid-but-wrong** quadrant — config that parses, schema-validates, and has every field typed
correctly, yet provisions the wrong infrastructure, *surprise-destroys* a stateful resource, flips an
environment via a silent default, or churns on every apply because it isn't idempotent. VALIDITY's B3
gate is "plan succeeds **and the diff is the intended change**." This file is the *intended-change*
half — the part the parser and the schema validator are blind to.

## The one principle

> **A config's real behavior is its diff against current state, not its text.** The same HCL is a
> create on an empty state and a destroy-and-replace on a populated one. The plan — not the source —
> is the contract. Grade the diff, not the keys.

Two corollaries:
- **A green parse / validate is evidence of nothing about outcome.** Syntax and schema say the config
  is *well-formed*, never that it does the *right thing*. The question is never "does it validate?"
  but "is the plan diff exactly what I intended — and nothing more?"
- **The proof is the plan, read against the stated desired state (A1).** Run `plan`/`diff`/`dry-run`
  via `bin/config-harness.py`, then read every line of the diff as a claim to verify against what A1
  asked for. An unrun plan is no evidence; an unread plan is the same.

## The four failure shapes (what a green parse hides)

| Shape | Smell in the plan diff | Why it's *valid but wrong* |
|---|---|---|
| **Surprise destroy** | `-/+ destroy and then create replacement` on a stateful resource (db, volume, bucket) | a change to an *immutable* attribute (name, AZ, engine version) silently recreates the resource — data loss, with a perfectly valid config |
| **Silent default** | a field you never set resolves to a value the plan now shows (`publicly_accessible = true`, `replicas = 1`, `deletion_protection = false`) | the wrong outcome came from an *unset* key taking a dangerous default in *this* environment |
| **Wrong scope / wrong target** | the diff touches resources/namespaces/accounts you didn't intend; an empty no-op when you expected a change | the config provisions an adjacent thing, or targets the wrong workspace/state |
| **Non-idempotent churn** | a second `plan` after `apply` *still shows a change* (a timestamp, `random_*` without a seed, a reordered list, a server-defaulted field fought by the controller) | every apply mutates infrastructure; "no-op on re-apply" is the definition of a settled config |

## Idempotency — the property text can't show

A correct config is a **fixed point**: apply it, and applying it again is a no-op (`No changes. Your
infrastructure matches the configuration.` / an empty `kubectl diff`). Non-idempotency is invisible in
the source and obvious in the second plan:

- **The clock / randomness** — a `timestamp()`, a `uuid()`, a `random_password` with no `keepers` —
  regenerates every plan; the resource churns forever.
- **List/map reordering** — an unordered set written as an ordered list shows a diff each run.
- **Server-side defaults & controller fights** — a field the API server (or an operator/HPA) defaults
  or owns, that your config also sets, ping-pongs between the two on every apply.
- **External mutation** — the config reverts a value something else legitimately changed (a scaled
  replica count, a rotated secret), clobbering live state.

The test is mechanical: **plan after apply must be empty.** Where you can't apply, reason about each
field — is its value *stable* across runs, or derived from the clock / randomness / a server default?

## Reading a plan diff (the discipline)

When `config-harness.py` runs the `plan` phase, don't skim the summary line — read the diff against
A1's desired state:

1. **Count by verb.** How many create / update / **destroy** / replace? A destroy or replace you did
   not intend is the headline.
2. **Locate every destroy/replace on a stateful resource.** Database, volume, bucket, stateful set —
   a replace here is data loss. Confirm it was intended; if not, it's a surprise destroy (often an
   immutable-attribute change → use a `create_before_destroy` / migration, not a silent recreate).
3. **Scan the *unexpected* lines.** A change to a resource A1 never mentioned means the config reaches
   further than its desired state — wrong scope.
4. **Check the shown defaults.** Any security-relevant field the plan now sets that you never wrote
   (`public`, `0.0.0.0/0`, `protection = false`, an open policy) is a silent default — pin it
   explicitly.
5. **Confirm the no-op tail.** A correct change-set is *only* the intended diff; everything else
   should read "no changes."

A diff that is exactly the intended change, with no surprise destroy, no unowned default, and an empty
second plan, is the only thing that makes B3 a real pass.

## How this scores

B3 is **plan-succeeds ∧ intended-diff**:
- *succeeds* = the harness's `plan` gate ran and the dry-run did not error;
- *intended-diff* = the diff is exactly A1's desired change — no surprise destroy, no silent
  dangerous default, no out-of-scope resource — **and** a second plan would be a no-op (idempotent).

A config that parses and validates but whose plan surprise-destroys, flips a default, or churns is
**not** B3-passing — it's the *valid-but-wrong* quadrant, and the corrective is the config (pin the
default, add `create_before_destroy`, seed the randomness, scope the target), not the score. And a
config whose plan was **skipped** (tool absent, or a format with no dry-run) has *no B3 evidence* — it
cannot be SHIPPABLE on a guess; report B3 as no/partial evidence, gate failures first.
