# The INTEGRITY axis — the dependency policy, the card, the stress catalogue, the handoff

The Integrity axis (B1–B5) grades *mechanism*, bottom-up: from "does this graph even resolve" to
"does the whole thing deploy as decomposed." B1–B3 are the **mechanizable** levels — route them to
`bin/dependency-check.py` and **trust the tool, not the read-through**. An LLM cannot reliably tell by
eye whether a graph is acyclic or every edge respects layering; the tool can, every time.

## The ladder

| Level | Gate | What proves it | The signal |
|---|---|---|---|
| **B1 Graph well-formed** | `[gate, code]` | card parse (`dependency-check.py`) | every node/edge resolves; no edge to a nonexistent module |
| **B2 Acyclic** | `[gate, code]` | Tarjan SCC (`dependency-check.py`) | **no cycle** — modules build/test/reason/replace independently |
| **B3 Layering respected** | `[gate, code]` | layer-index compare (`dependency-check.py`) | every edge points DOWN; no module depends UP a layer |
| **B4 Coupling bounded** | review | the bin's `HIGH_COUPLING` advisory + judgment | fan-in / fan-out within reason; no god-module hub |
| **B5 Deployability** | review | the build/CI itself + judgment | builds, packages, deploys as decomposed; independent lifecycles hold |

The gates cascade: don't grade coupling (B4) for a graph with a cycle (B2). A gate flag stops the
axis — fix the graph before reviewing.

## The contract card — the artifact the bin reads

The dependency graph, declared once as JSON (`dependency-check.py template` prints a starter):

```json
{
  "components": ["ui", "api", "domain", "db"],
  "layers": ["ui", "api", "domain", "db"],
  "layer_of": {"ui": "ui", "api": "api", "domain": "domain", "db": "db"},
  "edges": [["ui", "api"], ["api", "domain"], ["domain", "db"]]
}
```

- `components` — the nodes: the modules / containers / services from A2.
- `layers` — **ordered top → bottom**. A component in a higher layer may depend DOWN, never UP.
- `layer_of` — optional `component → layer`. When a component *is* its own layer, omit it (the
  component name is used). A real system usually has more components than layers
  (e.g. several modules in the "domain" layer), so `layer_of` is where you group them.
- `edges` — `[from, to]` means **from depends on to**. Recover these from imports, build config, or
  call sites for an existing system; declare them for a proposed one.

**Build the card before grading.** For DECOMPOSE, extract the real edges (don't trust the design
doc's arrows — those are the STRUCTURE claim; the card is the INTEGRITY reality). For DESIGN, declare
the proposed graph and run the bin to prove it *can* be acyclic + layered before committing.

## The flags and how to read them

| Flag | Level | Severity | What it means / the fix |
|---|---|---|---|
| **CYCLE** | B2 | **GATE** (FAIL) | A transitive `a → … → a`. Two+ modules can't be built/tested/replaced independently. Break it: introduce an intermediary, invert a dependency (depend on an abstraction), or merge the two if they're truly one. |
| **LAYER_VIOLATION** | B3 | **GATE** (FAIL) | A lower layer depends UP on a higher one. Reverse the edge (the higher layer should depend on the lower), or extract the shared concept into a lower layer both can depend on. |
| **HIGH_COUPLING** | B4 | advisory | A hub: fan-in or fan-out over threshold (default 5). High fan-in = a god-module everything reaches into (a change risk); high fan-out = a module that reaches into everything (a fragility risk). Confirm — sometimes a façade legitimately has high fan-in. |
| **ORPHAN** | — | advisory | A module with no edges in or out. Dead code, a missing edge you forgot to declare, or a genuinely standalone utility. Confirm which. |

**A clean run is necessary, NOT sufficient.** A green `dependency-check.py` proves the graph is
well-formed, acyclic, and layered. It is **silent** on whether the boundaries are *right* — a perfect
DAG over the wrong decomposition (a split responsibility, a contested-ownership concept, a leaky
interface) passes every check and still belongs in the bottom-left quadrant. The tool is a lossy
pre-filter for the INTEGRITY axis, not an oracle for the architecture. Confirm the STRUCTURE side
adversarially (see `references/architecture-knowledge.md`).

## B5 Deployability — the level the bin can't reach

The graph can be perfect and the thing still won't ship as decomposed. Judgment, informed by the real
build:

- Do the units the design claims are independent actually build/deploy independently, or does one
  pull in the others at link/package time (a *hidden* edge the card missed)?
- Is the deploy unit the same as the dependency unit? (A "microservice" that can't deploy without
  three others is a distributed monolith.)
- Independent lifecycles: can each unit be versioned and rolled back on its own?

A hidden coupling found here is also a missing edge — add it to the card and re-run the gates.

## The stress catalogue — for A5 fitness and B5 deployability

Walk these scenarios against the architecture; friction the boxes-and-arrows hid is a finding.
Prioritize by likelihood × impact, weighted by the user's stated constraints.

- **Scale** — traffic grows 10×: first bottleneck? one hot path takes 80% of load: scales
  independently? a table grows from 1K to 1M rows: query pattern still holds?
- **Change** — the most likely new feature: how many modules change? a key dependency is swapped:
  how contained? a "permanent" feature is removed: how cleanly extracted?
- **Failure** — a component is unreachable 30s: in-flight requests? a downstream errors 10% of the
  time: graceful degrade? cascading: A's failure queues B which times out C — circuit breakers /
  backpressure / bulkheads?
- **Misuse** — business logic placed in the wrong layer: anything prevents it? (This is exactly the
  `LAYER_VIOLATION` the bin catches mechanically — the structural intent behind the gate.) an endpoint
  added that bypasses auth: how is it caught?

Classify each: `RESILIENT | DEGRADES | BREAKS`, with severity and the architectural fix.

## Handoff — what this skill does NOT do

`architecture-decomposer` is the **system-level design + grade** stage; it feeds the rest of the
code-tooling fleet and does not overlap it:

- **→ `code-decomposer`** (per module): receives the locked contract card + the module's interface
  contract and grades that *unit* on SPEC × EXECUTION. This skill grades the **graph between**
  modules; `code-decomposer` grades the code **inside** one. Different altitude — don't re-grade a
  unit's tests here.
- **→ a code author / `ui-build-components`**: receives the verified boundaries + contracts and
  implements them. This skill grades the structure, it does not write the implementation.
- **→ `/code-review`**: receives the contract card and audits the *finished diff* for bugs.
  Architecture is design-time and graph-scoped; `/code-review` is diff-time and change-scoped.
- **→ `/verify`**: runs the whole app to confirm end-to-end behavior. This skill proves the *structure*
  holds; `/verify` proves the *system* behaves.
- **not `/simplify`**: that's reuse/efficiency cleanup (quality). This skill is correctness of
  structure (right boundaries + a graph that holds).

## Governance

- **The contract card is checked in** next to the architecture doc as the dependency graph of record;
  it versions with the system and is the diff a reviewer reads first. Re-run `dependency-check.py` in
  CI so a new cycle or layer violation fails the build, not a code review.
- **Keep the card in sync with reality** — when a new module or edge lands, update the card. A card
  that drifts from the real import graph turns the gate into theater.
- **Threshold the coupling, don't hard-gate it** — fan-in/fan-out limits are advisory; a façade can
  legitimately exceed them. The gates are cycles and layering (mechanical, unambiguous); coupling is a
  review with a number attached.
