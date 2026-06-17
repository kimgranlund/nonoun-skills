# Worked example — illegal states on MODEL × VALIDITY

A complete DECOMPOSE → fix → GRADE for a `RequestState` type, showing the **B3 instance gate**
proving an illegal state is representable, then the red→green collapse to a tagged union. The two
specs here are checked in and the validator actually rejects / accepts the instances.

## The artifact

A request's state, modelled as a record of optional fields:

```
{ loading: boolean, error?: string, data?: string }
```

It compiles and type-checks. But the domain says a request is **exactly one of** loading / ready /
failed — so `loading && error`, and `data && error`, are impossible. Are they representable?

## DECOMPOSE

**A · Model** (whole → part)
- **A1 Domain** `[gate]` — "a request is one of loading / ready / failed." ✓
- **A2 State-space** `[gate]` — the cardinality test. The record admits the cross-field combinations
  the domain forbids. *Claim:* those illegal states are unrepresentable. Prove it (B3).

**B · Validity** (part → whole)
- B1 Well-formed / B2 Sound `[gate]` — the schema parses. ✓
- **B3 Instances** `[gate, code]` — feed a LEGAL set (must all validate) **and an ILLEGAL set (must
  all be rejected)** through the validator (`examples/request-state.red.json`):

```
$ python3 bin/instance-check.py examples/request-state.red.json
instance-check: FAIL (2 finding(s); 3 legal / 2 illegal instances)
  ILLEGAL_REPRESENTABLE  illegal[0] validates — an illegal state IS representable: {'loading': True, 'error': 'timed out'}
  ILLEGAL_REPRESENTABLE  illegal[1] validates — an illegal state IS representable: {'data': 'ok', 'error': 'timed out'}
```

**A2 has actually failed, proven mechanically.** "Make illegal states unrepresentable" was a claim;
the illegal instance set turns it into a test, and the test is red — the optional-soup/boolean-blind
record admits `loading + error` and `data + error`.

## Fix — collapse to a sum type

Discriminate on a `tag` and attach each field to the variant that owns it
(`examples/request-state.green.json`): `oneOf [ {tag:"loading"}, {tag:"ready", data},
{tag:"failed", error} ]`, each a closed record. The cross-state mixes now have no value.

```
$ python3 bin/instance-check.py examples/request-state.green.json
instance-check: OK — 3 legal validate, 3 illegal rejected (illegal states unrepresentable)
```

The illegal set grew (added `loading + data`) and every member is now rejected — the red→green
transition is the proof that A2 holds.

## GRADE — two scores, never averaged

- **Model: A2 gate-fail → (after collapse) 5/5** — domain right; state-space now matches it (sum,
  not product); invariants by construction (closed records, `const` discriminant).
- **Validity: 5/5** — parses, sound, and the instance gate is green.

**Quadrant:** the red schema sat in **"valid, admits illegal states"** (Validity passed — it's a
fine schema — but Model's state space was too wide) — *built right, designed wrong*. The fix is a
sum type, not schema machinery. After it: **SHIPPABLE**.

The lesson: a type's meaning is the **set of values it admits**, not its field names — and you can't
eyeball whether the illegal ones are reachable; you feed them in and watch the gate reject.
