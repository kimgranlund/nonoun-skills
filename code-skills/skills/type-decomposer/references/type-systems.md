# Type systems & schema dialects — what each can make unrepresentable

The method is dialect-agnostic, but the *tools* for collapsing the state space differ by system, and
so does how far B3 (instance checking) can be mechanized. Match the model to what the target can
actually enforce — an invariant the type system can't express becomes a runtime check, which is a
weaker gate.

| System | Sum types | Closed records | Refinements | Notes for the state-space gate |
|---|---|---|---|---|
| **TypeScript** | discriminated unions (`{tag:'a'}|{tag:'b'}`) — strong | exact object types are awkward (structural; excess-property checks only on literals) | template-literal & branded types; no native refinements | great at sums, weak at "no extra fields"; brand primitives by hand (`type Email = string & {__brand}`) |
| **Rust** | `enum` with data — excellent | structs are closed by default | newtypes (`struct Cents(u64)`), `NonZeroU32` | the gold standard for unrepresentable illegal states; exhaustive `match` enforces coverage |
| **Haskell / F# / OCaml** | algebraic data types — excellent | records closed | newtypes, smart constructors, GADTs/refinements | "make illegal states unrepresentable" originates here; the compiler is the gate |
| **JSON Schema** | `oneOf` + `const` discriminant | `additionalProperties:false` | `enum`,`pattern`,`format`,`minimum`,`minItems` | fully mechanizable by `bin/instance-check.py`; the lingua franca for the instance-set proof |
| **Protobuf** | `oneof` (no payload-less variants pre-edition) | fields are open by spec (unknown fields preserved) | none native; validate-rules via buf/protovalidate | sums weaker than ADTs; openness is a wire feature — close it in code, not the schema |
| **SQL DDL** | none native (emulate via CHECK + nullable columns, or sibling tables) | columns are fixed; rows are closed | `CHECK`, `NOT NULL`, `UNIQUE`, FK, domains/enums | sum types are the pain point — the "one nullable column per variant" anti-pattern is optional-soup in disguise; prefer a table-per-variant or a tagged table with a CHECK |
| **GraphQL** | unions & interfaces (no input unions) | inputs are fixed sets | enums, custom scalars, `!` non-null | input types can't be sums — a known hole that pushes illegal states into resolvers |

## Cross-cutting hazards

- **Nullability is three states.** "absent", "null", "value" — most systems conflate two of them
  differently (TS `?` vs `| null`, SQL `NULL`, protobuf presence). Decide which states are legal and
  forbid the rest; a sloppy nullable is the most common silent widener.
- **Structural vs nominal.** Structural systems (TS, Go interfaces) accept any value of the right
  shape — two domain concepts with the same fields are interchangeable. Brand/newtype to regain
  nominal distinctions where the domain needs them.
- **Open-by-default wire formats** (protobuf, JSON without `additionalProperties:false`, Avro
  unions) preserve unknown fields — convenient for evolution, but it means the *closed* version of
  your record lives in code, and the schema alone doesn't make extra fields unrepresentable. Gate it
  at the parse boundary.
- **Exhaustiveness is half the value of a sum.** A union you don't match exhaustively (no `match`/
  `switch` totality, no discriminated narrowing) leaks the "forgot a variant" bug. The type system
  that *forces* exhaustiveness (Rust, ML-family) gives you a second gate for free.

## Choosing the target for the instance-set proof

When you want a mechanized B3, model the contract in **JSON Schema** (even if the runtime type lives
in TS/Rust/SQL) and run `bin/instance-check.py` over the legal/illegal sets — `oneOf` +
`additionalProperties:false` + `const`/`enum` express the four collapses from `illegal-states.md`
directly. Then mirror the schema into the host type system, preferring whichever construct that
system makes *unrepresentable* over whichever it merely *validates at runtime*.
