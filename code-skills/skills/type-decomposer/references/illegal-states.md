# Make illegal states unrepresentable — the toolkit

The centerpiece. Every entry is a *widener* of the state space (a shape that lets impossible states
exist) and the *collapse* that removes them. Each collapse is provable: after it, the illegal
instance has no value, so `bin/instance-check.py` rejects it. `bin/model-smells.py` catches the
wideners statically; this file is the catalogue of fixes.

## The principle

A type is a set of values; its cardinality is its state count. Domain modeling is making that count
**equal** the domain's legal-state count — almost always by *shrinking* the type. The four wideners
below cover the great majority of representable-but-illegal bugs.

## 1. Boolean blindness → sum type

Two booleans are four states; the domain rarely allows four. The illegal combinations are
representable and someone will eventually construct them.

Widener (representable: `loading && error`, `data && error`):
```
{ is_loading: bool, is_error: bool, data?: T, error?: string }
```
Collapse — a tagged union where each state carries exactly its data:
```
oneOf [ { tag: "loading" },
        { tag: "ready",  data: T },
        { tag: "failed", error: string } ]
```
Now `loading` cannot carry `data`, `failed` cannot carry `data`, and `ready && failed` has no value.
Rule of thumb: **every set of booleans that can't all be true at once is a sum type wearing a
disguise.**

## 2. Optional soup → required + variants

A record of all-optional fields admits `2^n` field combinations; the domain allows a handful. The
illegal combinations (a `cancelled` order with a `shipped_at`, a `draft` with a `published_url`) are
representable.

Widener:
```
{ state?: string, published_url?: string, cancelled_reason?: string, shipped_at?: string }
```
Collapse — discriminate on the state, and attach each field to the variant that owns it:
```
oneOf [ { state: "draft" },
        { state: "published", published_url: Url },
        { state: "cancelled", cancelled_reason: string } ]
```
What was optional becomes *required within its variant* and *absent from the others* — the
cross-state mixes lose their representation.

## 3. Primitive obsession → newtype / refined type

`string` and `number` are enormous sets; the domain field is a tiny subset. A bare `string` for an
email admits every non-email; a bare `number` for an age admits negatives and 10⁹.

Widener: `{ email: string, age: number, id: string }`
Collapse: a constrained/branded type per field —
```
email: { type: "string", format: "email" }
age:   { type: "integer", minimum: 0, maximum: 130 }
id:    { type: "string", pattern: "^usr_[a-z0-9]{12}$" }
```
…and in a real type system, a *newtype* (`UserId`, `Email`, `Age`) buildable only through a
validating constructor, so the invalid value has no inhabitant downstream. **An `Email` is not a
`String`.**

> `bin/instance-check.py` **asserts** `format` for `email`, `uri`, `url`, `uuid`, `date`, and
> `date-time` (a non-email is rejected against `format:email`) — even though the JSON Schema spec
> makes `format` non-asserting by default. For any *other* semantic constraint, express it as a
> `pattern` (as the `id` field above does), or the instance check won't enforce it.

## 4. Open record → closed record

An object without `additionalProperties:false` admits arbitrary extra fields — typos, stale keys,
smuggled data — all representable and silently carried through round-trips.

Widener: `{ type: "object", properties: { id, name } }`
Collapse: `{ type: "object", additionalProperties: false, properties: { id, name } }`
Close the record whenever the domain is closed (which is most of the time); leave it open only for a
deliberately extensible bag, and then type the bag's values.

## Two more, briefly

- **Stringly-typed enum → enum.** A `string` whose comment says "one of open/closed/pending" admits
  every other string. Use `enum`/`const`; the typo `"opn"` becomes unrepresentable.
- **Nullable + optional confusion.** "absent", "present-but-null", and "present-with-value" are three
  states; if the domain has two, collapse them (forbid one via the schema) so the third illegal state
  can't appear.

## Proving the collapse

For each widener you remove, add the illegal instance it used to allow to the **illegal set** and
re-run `bin/instance-check.py`. Before the collapse it validated (illegal state representable —
FAIL); after, it is rejected. That red→green transition is the mechanized proof that A2 ("no illegal
state representable") now holds — not a claim, a test.

## When NOT to collapse

Tightening has a cost: an over-modeled type can forbid a *legal* state (a real future status you
didn't foresee, a field the domain does allow to vary). Keep the **legal instance set** as the
counterweight — every legal state must still validate. The target is the exact state space, not the
smallest one. A model that rejects a legal instance is as wrong as one that accepts an illegal one;
the two scores, never averaged, keep both honest.
