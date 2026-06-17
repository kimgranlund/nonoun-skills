# The MODEL axis — does it model only the legal states?

The Model axis (A1–A5) grades the *state space*, top-down. A compiler is silent on it — a
boolean-blind record type-checks perfectly. This is the axis LLMs get wrong by reaching for the
familiar shape (a bag of optional fields) instead of the domain's actual structure, so it carries an
**adversarial probe**, not just a checklist.

## A1 · Domain `[gate]`

Name the domain concept in one sentence, in the language of the domain, before reading the fields.
Then ask whether the type models *that* — an `Order`, a `Subscription`, a `PaymentMethod` — or an
adjacent thing it drifted to (a database row, a form payload, an API envelope). A type that models
the transport instead of the concept can't make the concept's illegal states unrepresentable.

## A2 · State-space `[gate]` — the heart

A type is a **set of values**. Two questions, both must hold:

- **All legal states representable?** Is there a value of the type for every state the domain
  allows? (Under-modeling: a `status: "active" | "cancelled"` that can't represent `"trialing"`.)
- **No illegal state representable?** Is there NO value of the type for any state the domain
  forbids? (Over-modeling: the classic `{ is_loading, is_error, data, error }` record, where
  `is_loading && is_error` and `data && error` are representable but impossible.)

The cardinality test: count the states the type admits versus the states the domain allows. The gap
in either direction is the defect. Make the **count match** — usually by *shrinking* the type with a
sum, a closed record, or a refinement until the illegal states have no value.

## A3 · Sums vs products `[review]`

The single highest-leverage move in domain modeling:

- **Product type** (record / `all of`) when the domain is "an X has an A *and* a B *and* a C." Its
  cardinality is the *product* of its fields — which is exactly why piling optional fields onto a
  record explodes the state space.
- **Sum type** (tagged union / `one of` / discriminated enum) when the domain is "an X is *either* a
  P *or* a Q." Its cardinality is the *sum* — and each variant carries only the data that variant
  needs, so the cross-variant illegal states (cash with a card number) become unrepresentable.

**Boolean blindness** is the recurring tell: two booleans on a record = four states, and the domain
usually allows two or three of them. Replace `{ is_card: bool, is_cash: bool, card_number? }` with
`oneOf [ Card{card_number}, Cash ]`. Every flag pair that can't all be true at once wants a sum.

## A4 · Invariants `[review]`

Push invariants into the type so they hold **by construction**, not by a runtime check or a comment:

- **Newtypes / branded types** over primitive obsession: `Email`, `UserId`, `Cents` — not `string`,
  `string`, `number`. An `Email` that can only be built through a validating constructor can never
  hold a non-email.
- **Refined / constrained types**: `NonEmpty<T>`, `Positive`, a `pattern`/`format` on a string, a
  `minItems: 1`. The constraint lives in the type, so an invalid value has no representation.
- **Closed records** (`additionalProperties: false`) when the domain is closed — an unexpected field
  is then unrepresentable rather than silently carried.
- **Make the parse the gate** ("parse, don't validate"): convert unstructured input into the precise
  type once, at the boundary; downstream code receives a value that *cannot* be illegal.

## A5 · Evolution `[review]`

A model is read and written for years. Can it change without breaking consumers? Additive changes
(a new optional field, a new sum variant — mind exhaustiveness) over breaking ones; an explicit
optionality and nullability discipline; versioning where the wire format is shared. Does it match
the surrounding system's conventions (the same nullability style, the same id types)?

## The adversarial MODEL probe

A2 is not deterministically gateable from the type alone — so verify it the way the other
decomposers verify their dangerous axis: **in a fresh context, adversarially.**

> *"Here is the type/schema and the domain it claims to model. Construct one value that the type
> ACCEPTS but the domain forbids — an illegal state that is still representable. Default to
> 'one exists' and search for it."*

Every value the probe finds becomes a new entry in the **illegal instance set** (so
`bin/instance-check.py` will fail until the model is tightened) and usually corresponds to a smell
`bin/model-smells.py` can be taught to catch. The output of this axis is the **type-spec card** — the
domain, the legal and illegal instance sets, and the schema — handed to VALIDITY to prove.
