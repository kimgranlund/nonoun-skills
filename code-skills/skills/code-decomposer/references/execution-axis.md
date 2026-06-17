# The EXECUTION axis — does it provably run, here?

The Execution axis (B1–B5) grades *mechanism*, bottom-up: from "does this token even parse" to "does
the whole unit behave under adversarial input." It is the **mechanizable** axis — route it to the
real toolchain via `bin/execution-harness.py` and **trust the tool, not the read-through**. An LLM
cannot reliably tell by reading whether code compiles, type-checks, or a test passes; running it is
the only evidence.

## The ladder

| Level | Gate | The tool that proves it | The signal |
|---|---|---|---|
| **B1 Compile** | `[gate]` | compiler / `import` / `compileall` / bundler | parses, loads, **no nonexistent symbol or API** (the #1 hallucination) |
| **B2 Types/Lint** | `[gate]` | type-checker (`mypy`/`tsc`) + linter | types are consistent with the contract; no static defects |
| **B3 Test** | `[gate]` | test runner **+ mutation** | tests pass *and are real* (see `test-integrity.md`) |
| **B4 Robustness** | review | property tests / fuzz / stress | holds on edge & adversarial input; deterministic; bounded resources |
| **B5 Observability** | review | the code itself + tests | failures are diagnosable; effects contained; the unit is testable |

The gates cascade: don't grade robustness (B4) for code that won't compile (B1). A red gate stops the
axis — fix it before reviewing.

## The live-gate protocol (the harness)

`bin/execution-harness.py` is a thin adapter, not a bundled toolchain. You declare the project's
commands once; it runs each phase whose tool is on PATH and normalizes the verdicts. A missing tool
is a **SKIP** (evidence incomplete), never a pass — like the mermaid render-check, the static logic
is self-tested with no deps, the live run fires where the tools exist.

```json
{
  "language": "python",
  "gates": {
    "compile":   { "cmd": "python3 -m compileall -q src" },
    "typecheck": { "cmd": "mypy src" },
    "lint":      { "cmd": "ruff check src", "gate": false },
    "test":      { "cmd": "pytest -q" },
    "mutation":  { "cmd": "mutmut run", "gate": false }
  }
}
```

`gate` defaults: compile / typecheck / test gate; lint / mutation are advisory. Run it:

```sh
python3 bin/execution-harness.py template          # print a starter manifest
python3 bin/execution-harness.py manifest.json     # run present gates; report card; nonzero on gate fail
```

Read the card honestly: a **skipped** gate means you have *no evidence* for that level, not a pass.
A SHIPPABLE verdict requires the gates to have actually **run green**, not merely "not failed."

## Reading each tool's signal

- **Compile / import** — the cheapest, highest-value gate: it catches the hallucinated function,
  the wrong import path, the renamed API. Run it first, always.
- **Type-checker** — confirms the implementation matches the *contract* (A2). A type error is often a
  contract mismatch in disguise. Treat `# type: ignore` and `any` as un-checked surface.
- **Linter** — advisory by default, but a linter rule firing on real-bug categories (unused result,
  shadowed name, unreachable code) is signal, not noise.
- **Test runner** — green is necessary, not sufficient. Pair every run with `test-vacuity-check.py`
  and a mutation pass (see `test-integrity.md`) — a green suite of vacuous tests is the *green but
  wrong* quadrant.
- **Mutation** — the proof that the tests pin the contract: it breaks the implementation and checks
  the suite notices. Surviving mutants are untested behavior. Advisory in CI cost, decisive in
  judgment.

## B4 Robustness & B5 Observability (reviews)

- **B4** — beyond "passes the tests it has": determinism (no hidden clock/RNG/order dependence),
  idempotency where the contract implies it, resource bounds (no quadratic blowup, no unbounded
  buffer/leak), behavior under malformed and adversarial input.
- **B5** — when it fails in production, can you tell *why*? Are errors specific, are effects
  contained and reversible, is the unit shaped so a test can observe its behavior without elaborate
  mocking (a unit that's hard to test is usually telling you about a contract problem).

The output of this axis is the **execution report card** — which gates ran, their verdicts, and the
vacuity/mutation findings — handed alongside the spec card to `/code-review` and `/verify`.
