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
| **JSON Schema** | `oneOf` + `const` discriminant | `additionalProperties:false` | `enum`,`pattern`,`format`,`minimum`,`minItems` | mechanizable for the supported subset by `bin/instance-check.py` (see its unsupported-keyword list below); the lingua franca for the instance-set proof |
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

## Model-smell pre-filter: JSON Schema, TypeScript, and Python

The mechanized B3 proof (`instance-check.py`) runs over JSON Schema, but the **MODEL-axis
pre-filter** `bin/model-smells.py` reads the host type system directly — you don't have to mirror a
type into JSON Schema just to smell-test it. It dispatches on file extension:

- **`.json`** — walked as a JSON Schema tree (the original path, unchanged).
- **`.ts` / `.tsx`** — each `type Name = { … }` / `interface Name { … }` block is brace-matched and
  its field lines parsed (no stdlib TS parser). It reads the language's own collapse tools as the
  *clean* form: a branded primitive (`string & { __brand }`) clears PRIMITIVE_OBSESSION, a
  string-literal union (`'a' | 'b'`) clears STRINGLY_TYPED_ENUM, a literal `tag`/`kind` discriminant
  suppresses OPTIONAL_SOUP, and an index signature (`[k: string]: …`) raises OPEN_RECORD.
- **`.py` / `.pyi`** — `TypedDict` subclasses and `@dataclass`-decorated classes are parsed with the
  stdlib `ast` module (precise, not regex); a `Literal[…]`/`NewType` brand or a `Literal`-typed
  discriminant is the clean form. A fragment that won't `ast.parse` falls back to a regex pass for
  the primitive-obsession smell rather than crashing.

A directory scan picks up all three at once. The five finding KINDS and message style are shared —
the smells (boolean-blindness / optional-soup / primitive-obsession / open-record /
stringly-typed-enum) are language-agnostic. This is a pre-filter only; the *proof* still routes a
JSON-Schema model through `instance-check.py`.

## Choosing the target for the instance-set proof

When you want a mechanized B3, model the contract in **JSON Schema** (even if the runtime type lives
in TS/Rust/SQL) and run `bin/instance-check.py` over the legal/illegal sets — `oneOf` +
`additionalProperties:false` + `const`/`enum` express the four collapses from `illegal-states.md`
directly. Then mirror the schema into the host type system, preferring whichever construct that
system makes *unrepresentable* over whichever it merely *validates at runtime*.

### What `bin/instance-check.py` is a SUBSET of (read before trusting a green)

The validator covers a deliberate subset and is **default-deny**: a schema using any keyword it does
not understand FAILS LOUD as an `UNSUPPORTED_SCHEMA` finding rather than silently passing (a silent
pass would drop the constraint and false-green an illegal instance).

- **Supported:** `type` (incl. `5.0 ⊨ integer`, `bool` distinct from int), `const`/`enum`
  (type-aware: `true ≠ 1`, `1 = 1.0`), `required`, `additionalProperties:false` and schema-form,
  `properties`, object-form `items`, `minimum`/`maximum`/`exclusive*`, `multipleOf` (tolerant),
  `minLength`/`maxLength`, `pattern` (trailing `$` → end-of-string), `minItems`/`maxItems`,
  `uniqueItems` (`1` and `1.0` collide), `allOf`/`anyOf`/`oneOf`/`not`, **asserting** `format`
  (`email`, `uri`, `url`, `uuid`, `date`, `date-time`), and **local `$ref`** into `#/$defs` /
  `#/definitions`.
- **Unsupported (flagged loudly, never silently ignored):** `if`/`then`/`else`, `patternProperties`,
  `propertyNames`, `dependentRequired`/`dependentSchemas`, `contains`/`minContains`,
  `prefixItems` and tuple-form (array) `items`, remote/non-local `$ref`, `$dynamicRef`, and any
  unrecognized keyword. Express the constraint with a supported keyword, or extend the tool.

Note on `format`: the JSON Schema spec makes `format` **non-asserting by default**, but this tool
asserts the formats above (an `email` that isn't one is rejected) precisely because the
primitive-obsession collapse depends on it. For any format *outside* that set, fall back to
`pattern` — an unasserted format is not enforced.
