---
date: 2026-05-06
---

# Reverse-engineering an existing app

Mandatory protocol for scaffolding `apps/<name>/` over an existing
implementation. Read in full BEFORE drafting any spec content. Do not skim.

## Why this protocol exists

On 2026-05-06 the first reverse-engineering pass on `apps/chat/` was audited
against the actual code and found:

- **10 fabrications** — claims of attributes/methods/events/file paths that
  don't exist in the code.
- **6 misrepresentations** — claims partially true but inverted or misleading.
- **7 omissions** — public surfaces in the implementation that the spec
  didn't mention at all.

Every error traced to **inferred-not-verified** content: the author read the
playground, inferred what the underlying composite "probably does," and
authored spec content from inference rather than from source. This protocol
makes that failure mode mechanical to prevent.

## Operating principle

**Read the code, not the playground.** The playground exercises a SUBSET of
the underlying surface. A spec that describes only what the playground
exercises is not a spec — it's a tutorial. Specs describe the full
composite/module surface. Source the surface from:

1. The component/module's `<name>.yaml` (authoritative public-API contract).
2. The component/module's `<name>.js` (full file, not excerpts).
3. The repo's adapter / utility / middleware code where applicable.

## Pre-pass — verified-surface inventory

Build this BEFORE writing any spec content. Without it, spec content is
guesswork.

### Step A — Inventory the components used

```bash
# Grep imports from the playground
grep -rh "import.*packages" apps/<name>/app/ | sort -u
grep -rh "<\([a-z]\+-ui\|[a-z]\+-shell\|[a-z]\+-thread\)" apps/<name>/app/*.html | sort -u
```

Build a list of every web component / module / utility the app pulls in.
Name each one. For composites (anything that contains other components),
flag with `[composite]`.

### Step B — Read every yaml

For each component / module in the inventory:

```bash
find packages -name "<component-name>.yaml" -exec head -200 {} \;
```

The yaml documents:
- Tag name
- Attribute/property table (with types, defaults, reflection)
- Slots (named + default + auto-stamped)
- Methods (public + signatures)
- Events (with detail shapes)
- States (CSS-targetable attributes)
- Variants

**Trust the yaml.** It is mechanically validated against the source via
`npm run components:verify` (or the project's equivalent). If the yaml says
event X exists with detail `{a, b, c}`, that's the contract.

If a component has NO yaml: that's a yellow flag. Read the source twice.

### Step C — Read every composite source end-to-end

Composites carry the architectural weight. For each `[composite]` flagged
in Step A, read the full `.js` file:

```bash
wc -l packages/web-modules/<cluster>/<name>/<name>.js
# Then Read it in full, not excerpts
```

Enumerate as you read:
- Every `static properties = { ... }` entry (these are attributes).
- Every `#emit("event-name", detail)` call (these are events).
- Every public method (no leading `#`, no leading `_`).
- Every public getter/setter (`get foo()` / `set foo(v)`).
- Every `connectedCallback`/`render`/`update` that mutates DOM (these inform
  the lifecycle).

For composites that compose internal primitives (e.g., `chat-shell`
internally uses `chat-thread` + `chat-input-ui`), also read the internal
primitives' yamls — the public-facing API of the composite often delegates
to these.

### Step D — Verify server-side / proxy code paths

Don't assume file locations. Run:

```bash
find . -name "server.js" -not -path "*/node_modules/*"
find . -name "*adapter*" -not -path "*/node_modules/*" | head
find packages -name "*.js" -path "*adapters*"
```

Read the actual proxy / server source. Verify:
- The endpoint path(s).
- The request body shape (which fields, which are required).
- The response shape (and any provider-specific terminators).
- The actual export shape of any adapters (not the inferred shape).

### Step E — Build the verified-surface table

Write this to a scratch buffer before drafting spec content. Format:

```markdown
## Verified surface for <component/module>

| Surface | Source | Actual shape |
|---|---|---|
| Attribute `proxy-url` | `chat-shell.js:42` (yaml line 18) | string, no default |
| Method `send(text, opts)` | `chat-shell.js:213` | `(text: string, opts?: { model?, system?, attachments? }) => void` |
| Event `chunk` | `chat-shell.js:239` (`#emit('chunk', { text, snapshot })`) | detail = `{ text: string, snapshot: string }` |
| ... | ... | ... |
```

Every spec claim about this component must trace back to a row in this
table. If a claim doesn't have a row, don't make the claim — extend the
table first by reading more code.

### Step F — Identify "exercised by playground" vs "full surface"

Mark each row with E (Exercised) or U (Unexercised) by the playground:

| Surface | Source | Actual shape | Used by `apps/<name>/`? |
|---|---|---|---|
| Method `send(text, opts)` | `chat-shell.js:213` | ... | E (proxy path) |
| Method `export()` | `chat-shell.js:262` | ... | U |
| Event `clear` | `chat-shell.js:169` | ... | U |

The spec describes both — but `BRIEF.md` and `SPEC.md` should distinguish
"the playground uses these N surfaces" from "the underlying composite
exposes these M surfaces." Don't conflate them.

## During-authoring protocol

Once the verified-surface table is complete, draft spec content with these
rules:

### Rule 1 — Every API claim cites file:line

Wrong: "chat-shell emits a `submit` event."
Right: "chat-shell emits a `submit` event (`chat-shell.js:106`) with detail
`{ text, model }`."

When you can't cite, you can't claim. Don't paraphrase from memory. Don't
invent plausible-sounding details.

### Rule 2 — Quote the source verbatim (or don't quote at all)

Wrong: "The fallback is OPTIONS-based and looks like:
```js
fetch('/api/chat', { method: 'OPTIONS' }).catch(() => { ... });
```"

If the actual code differs (e.g., includes additional args or a different
catch clause), this misleads readers who copy-paste. Either:
- Quote the EXACT source from the file (with line numbers), OR
- Describe in prose without code blocks.

### Rule 3 — Architectural narratives require documented sources

Sentences like "WebSocket was rejected because..." are not safe to write
unless you can cite a commit message, journal entry, ADR, postmortem, or
yaml comment. If no documented source exists, either:

- Omit the narrative entirely, OR
- Label it: "Inferred reasoning (not historically documented): ..."

Retroactive justification reads as authoritative even when invented. The
2026-05-06 audit specifically flagged ARCHITECTURE.md §4 as inverted-from-
fact reasoning that sounded like decision history.

### Rule 4 — Distinguish "what the playground does" from "what the composite does"

In `BRIEF.md`, the playground is the subject. Describe what `apps/<name>/`
does.

In `SPEC.md`, the composite is the subject. Describe the full public API,
then note which subset the playground exercises.

Conflating them produces F-08-class errors ("the spec says only 4 methods
exist because the playground uses 4").

### Rule 5 — Open decisions require evidence of openness

A `⚠️` open-decision claim implies "this has been considered and not
resolved." That requires evidence. If you can't point to a code TODO,
yaml comment, journal entry, or surface that's clearly a placeholder, then
it's a "feature gap" rather than an "open decision."

Distinguish:
- **Feature gaps**: "There's no persistence" — fact.
- **Open decisions**: "Persistence approach is undecided between
  localStorage and IndexedDB" — requires evidence that someone considered
  this.

When in doubt, prefer "feature gap" framing.

### Rule 6 — Surface yaml-vs-code drift as a first-class spec item

If the component has a `<name>.yaml` AND a `<name>.js`, diff the two as
part of the verified-surface inventory:

- Every `props:` entry in yaml → grep for the property name in the
  source. Verify type, default, reflection match.
- Every `events:` entry in yaml → grep for `#emit('<name>'` or
  `dispatchEvent(new CustomEvent('<name>'`. Verify detail shape.
- Every `states:` entry that declares an `attribute:` → grep for
  `setAttribute('<attr>'` in the source. **If the .js never sets it,
  the state is aspirational.** Document as drift.
- Every `slots:` entry → check whether the .js queries `[slot="..."]`
  or just relies on light-DOM children. Distinguish "real named slot"
  from "yaml-declared but light-DOM."

The drift items belong in their own SPEC.md section (e.g. §7 in the
`apps/app-shell` spec). Don't bury them — they're often the most
load-bearing spec content for someone re-implementing or migrating.

Drifts surfaced so far (as of 2026-05-06):
- admin-shell: `data-sidebar-{leading,trailing}-collapsed` declared,
  never set. Detection is width-based.
- admin-shell: `mode` enum `[\"\", rounded, borderless]` declared, but
  playground composes them as space-tokens (`mode="rounded borderless"`).

## Sweeping for known propagation patterns

Once one error is found, look for these propagation patterns — they tend to
spread across BRIEF, ARCHITECTURE, SPEC, and PATTERNS together:

- **Slot-vs-attribute conflation** — composites that use light-DOM
  attribute selectors (`[data-foo]`) are NOT using named slots. Don't
  describe them as "slots" with named-slot semantics.
- **Auto-stamped vs slot-mounted** — internal primitives stamped by a
  composite at `connected()` are NOT slot-mounted by the consumer. The
  consumer never inserts them.
- **Icon-as-current vs icon-as-target** — icon swap logic for theme
  toggles needs careful reading. Most patterns are "icon = current state"
  not "icon = state to switch to."
- **Server-side vs client-side routing** — provider routing in modern LLM
  clients is usually client-side detection + a `provider` field in the
  request, not server-side string-matching on `model`.
- **`data-*` attributes** — these are generic HTML, not part of any
  component's API contract. Don't list them in attribute API tables; put
  them in a "Cross-cutting attributes" section instead.
- **Yaml `enum` vs runtime token-list** — a yaml may declare a property
  as `enum: ["", "rounded", "borderless"]` while the playground actually
  uses `mode="rounded borderless"` (a space-token list). The yaml is
  declarative; the runtime is permissive. Flag this as a yaml-vs-runtime
  drift; describe the property as "treated as a token list" in the spec.
  Surfaced 2026-05-06 on `apps/app-shell/admin-shell`.
- **Direct child vs descendant selectors** — `${PARENT_SEL} > [data-X]`
  (direct child only) and `[data-X]` (any descendant) have very
  different author DOM constraints. When citing a selector, copy the
  combinator (`>`, ` `, `~`) from the source verbatim and call it out
  explicitly. The selector pickiness is a hard contract. Surfaced
  2026-05-06 on `[data-resize]` (must be direct child of sidebar).
- **Object-flow language: forwarded ≠ spread ≠ cloned** — when a handler
  does `dispatchEvent(new CustomEvent('x', { detail: e.detail }))`, the
  detail is **forwarded** (same object reference). Don't say "spread"
  (which means `{...e.detail}`, a copy) or "cloned" (deep copy). Subtle
  but matters when consumers hold the reference. Surfaced 2026-05-06 on
  admin-shell's command-select forwarding.
- **Internal-constant call-site count** — when documenting a constant
  like `SNAP_THRESHOLD = 96`, grep ALL uses (`grep -n SNAP_THRESHOLD`)
  and enumerate each call site in the spec. The constant is often used
  in 3-5 places, not just where it was first introduced. Surfaced
  2026-05-06 on admin-shell's SNAP_THRESHOLD (used in 4 places, spec
  initially cited 1).
- **Conditional setup ≠ unconditional setup** — when a trait or
  composite's `setup()` says "creates the X singleton" but the
  creation is gated on a condition (host attribute, priority value,
  config flag), the spec must state the gate. "Creates BOTH X and Y"
  is a misrepresentation when only X is unconditional and Y is lazy.
  Surfaced 2026-05-06 on announcer trait — `announcer.js:137-138`
  pre-warms only the polite region; assertive is lazy. Three docs
  initially said "both regions are created."
- **Helper bypass + lazy stage = silent no-op** — when a playground
  has a helper (e.g., `announceAssertive`) that calls
  `document.getElementById(<id>)` and silently returns on `null`, AND
  the underlying trait/component creates that element lazily, AND the
  playground bypasses the trait's API for triggering creation, the
  helper silently no-ops at runtime. This compound failure is invisible
  in code review but obvious in the spec — flag both halves (the
  bypass + the lazy stage) and trace whether the runtime path actually
  works. Surfaced 2026-05-06 on composed-flow's announceAssertive +
  bypassed announcer trait + lazy assertive region.
- **Defensive code that's redundant in v1.0** — patterns like
  `void [trait1, trait2, …]` (tree-shake guard) or `if (!host) return`
  on already-validated parameters can read as "important" when they're
  just defensive idioms. Verify the necessity by checking whether the
  guarded condition can occur in v1.0; if it can't, document the code
  as redundant or recommend removal. Surfaced 2026-05-06 on composed-
  flow's `void [...]` line — every trait was used downstream, so the
  tree-shake guard was redundant defensive code, not "side-effect-
  import preservation" as initially described.
- **`<title>` ≠ `<h1>` content** — when reverse-engineering a
  rollup of similar pages, the page `<title>` (in `<head>`) is often
  different from the heading visible in the body. Don't infer the
  title from the heading text. ALWAYS Read the shell file to extract
  the verbatim `<title>` content. Surfaced 2026-05-06 on apps/errors:
  spec inferred 500's title as "AdiaUI — Server error" but actual is
  "AdiaUI — Something went wrong"; inferred maintenance's as "AdiaUI
  — Maintenance" but actual is "AdiaUI — Down for maintenance."
- **Sub-shell drift in rollups** — when sub-pages share a shell
  template, "only X differs" claims need diff verification. Title
  differs, fetch URL differs, AND any filename-keyed strings inside
  inline scripts (e.g., catch-block error messages, console.error
  tags) differ. The actual diff is usually 3-5 lines per pair, not 1-2.
  Surfaced 2026-05-06 on apps/errors: spec said "only title and fetch
  URL differ" but the diff also included two filename-keyed strings
  in the catch block (4 lines per pair).
- **Memory-quote staleness** — when citing a memory entry in a spec,
  the quoted text snapshots a value from when the memory was written.
  If the cited value (like "auth.css is now ~33 lines") drifts before
  the spec is authored, the spec ends up self-contradicting (one
  paragraph quotes "33 lines"; another paragraph states the current
  "40 lines"). Either trim the quote to non-quantitative content or
  parenthetically note the drift. Surfaced 2026-05-06 on apps/errors.
- **Nested `<main>` from fragment-into-shell injection** — when a
  shell has `<main id="demo-root">` and the contents fragment also
  starts with `<main>`, the runtime DOM has a nested `<main>`. Calling
  the fragment's `<main>` "the body wrapper" is misleading — it's the
  fragment's outer element, injected INTO the shell's body wrapper.
  HTML5 allows multiple `<main>` when only one is rendered visible at
  a time (browser-rendering rules), but the spec must describe the
  nesting accurately. Surfaced 2026-05-06 on apps/errors.
- **Top-layer escape changes the `@scope` boundary** — when a
  component uses `popover="manual"` + `document.body.appendChild(panel)`
  for top-layer rendering (or any subtree mount outside the host),
  tokens declared inside `@scope (component-tag) { :where(:scope)
  { ... } }` are NOT visible to the mounted subtree. Selectors styling
  the body-mounted panel must use raw global tokens (`--a-*`).
  Tokens that LOOK intended for the panel (e.g.
  `--<component>-popover-row-bg-hover` declared in `@scope`) but are
  consumed only by `[data-popover-row]` selectors styling a body-
  mounted panel are DEAD CODE — declared, never reached, never
  applied. Verify consumption with
  `grep -oE "var\(--<prefix>-[a-z-]+\)"` against the css; tokens that
  appear in declarations but not in any `var()` call are dead.
  Surfaced 2026-05-06 on apps/table-toolbar — initial spec said
  "~12 dead-code popover tokens"; the verified count was 22 (every
  single `--table-toolbar-popover-*` declaration, including 8
  documented in yaml).
- **Token counts must come from grep, not from eyeball** — when
  enumerating CSS custom-property declarations or consumptions in a
  spec, use:
  ```bash
  # declared (unique by name, ignoring values)
  grep -E "^\s*--<prefix>-" <file>.css | \
    sed -E 's/:.*$//; s/^\s*//' | sort -u | wc -l
  # consumed (unique consumers via var())
  grep -oE "var\(--<prefix>-[a-z-]+\)" <file>.css | sort -u | wc -l
  ```
  Eyeball counts ("17 yaml / 28+ CSS / ~12 dead") routinely drift by
  a factor of 2 because declaration-blocks visually run together and
  the dead/live distinction needs cross-referencing. Surfaced
  2026-05-06 on apps/table-toolbar — eyeball "28+/~12" was actually
  "36/22" by grep.
- **Examples.html threshold prose drifts from source** — when a
  component ships per-component `<name>.examples.html` documenting
  thresholds (e.g. "13–50 distinct values → multi-select with
  searchable input"), AND the source uses an inequality
  (`if (uniqueValues.length >= 12)`), there's almost always an
  off-by-one between the human-summarized prose and the source
  inequality. The source is authoritative; prose is descriptive.
  When citing thresholds in the spec, quote the source inequality
  verbatim and note any drift in `examples.html`. Surfaced
  2026-05-06 on apps/table-toolbar — spec inherited "13-50" from
  examples.html; actual source uses `>=12` so 12 unique values is
  searchable.
- **Multi-module synthesis introduces drift the audit MUST catch** —
  when an app exceeds ~3000 lines, the verified-surface protocol
  parallelizes inventory across 4-5 sub-agents (one per module
  cluster). The synthesizer integrates agent reports into the spec.
  This indirection introduces a class of drift that doesn't appear
  in single-module passes: integration-error fabrications. Surfaced
  2026-05-06 on apps/construct-canvas (~5,700 LoC) — single-module
  table-toolbar pass landed 0 fabrications; multi-module construct-
  canvas pass landed 6 fabrications, all clustered at integration
  points (event-detail shapes, DOM class names, import paths). The
  faithfulness audit step is therefore MANDATORY for multi-module
  passes — not optional. Budget audit + fix as a discrete phase.
- **Event-detail shapes — read the dispatch site, don't infer** —
  when documenting an event's `detail: {...}` object, READ the
  `dispatchEvent(new CustomEvent('x', { detail }))` call site in
  source. The field names in `detail` are NOT always the same as
  the parameter names of the public method that fires the event.
  Surfaced 2026-05-06 on construct-canvas: spec asserted
  `{op: 'insert', id, parentId, spec}` (inferred from `insert(parentId,
  spec)` signature), actual is `{op: 'insert', id, parent, kind}`.
  Fields renamed in the dispatch (`parentId → parent`, `spec → kind`).
- **CSS class names in DOM-stamp diagrams must match `setAttribute`
  calls** — when documenting the post-stamp DOM tree, every `class=`
  in the diagram must trace to a `setAttribute('class', ...)` or a
  `.className =` assignment in source. Inventing a plausible-
  sounding class (`cc-pin-btn` vs actual `construct-card__pin`) is
  easy and read-plausible. Verify each via grep. Surfaced
  2026-05-06 on construct-canvas DOM-stamp diagram.
- **"Verbatim comment" framing requires verbatim quote** — when
  saying "verbatim comment from source", the quote MUST be byte-
  for-byte from source. Paraphrasing into a `// comment` block
  while labeling it verbatim is a fabrication class — the spec
  reads as authoritative when it's actually a paraphrase. Either
  quote exactly (with line range citation) OR drop the verbatim
  framing and describe what the comment says. Surfaced 2026-05-06
  on construct-canvas — two "verbatim" quotes were close
  paraphrases.
- **Import paths must be quoted as-written** — bare specifiers
  (`import 'icon-ui'`) and absolute paths (`/packages/web-components/
  components/icon/icon.js`) carry different module-resolution
  semantics. Simplifying or paraphrasing import paths in the spec
  loses load-bearing information about how the project's bundler
  resolves dependencies. Quote them verbatim from source.
  Surfaced 2026-05-06 on construct-canvas — spec listed bare
  specifiers that don't appear anywhere in source.
- **Directory name ≠ chunk name** — when reverse-engineering a
  corpus-source rollup, ALWAYS verify the chunk's `name` against
  the `data-chunk` attribute, not against the directory name.
  Authors sometimes use a suffix (e.g. `-grouped`, `-flat`,
  `-detailed`) on the chunk name without renaming the directory,
  signalling a variant family that may or may not be intentional.
  Surfaced 2026-05-06 on apps/patterns — `command-palette/`
  directory produces chunk `command-palette-grouped`. Cross-check:
  `grep "data-chunk=" <fragment>` AND `grep "name" <chunk-json>`,
  compare against directory name. Mismatches go in the spec as
  open decisions — don't silently rename to match.
- **Counts in narrative require source-grep verification** — when
  asserting "N rows", "N tasks", "N badges", etc., grep the source
  for the actual count. Eyeball-counting tabular content (e.g.
  3 columns × N tasks each in a kanban) is error-prone in either
  direction; the spec then ships a fabrication. Surfaced
  2026-05-06 on apps/patterns — initial spec said kanban has "8
  task cards across columns"; actual count is 7 (3+2+2). Self-
  audit caught it. Pattern for next time: write the count, then
  verify with grep before committing.

## Verification gate before commit

Before committing reverse-engineered specs, run a self-audit:

1. **Mechanical verification**: For each claim in the spec that names a
   file/method/event/attribute, verify with grep:
   ```bash
   grep -n "<thing>" packages/<path>/<file>.js
   ```
   At least 80% of named entities should grep-verify; investigate the rest.
2. **Yaml cross-check**: Diff the spec's component-API table against the
   yaml's attribute/method/event sections. Discrepancies = errors.
3. **Coverage check**: Every component in the Step A inventory should be
   mentioned in SPEC.md. Every public surface in the verified-surface table
   should be either documented OR explicitly out-of-scope-noted.
4. **Adversarial spot-check**: Pick 3 random claims from ARCHITECTURE.md's
   "Why X was chosen / rejected" sections. Can you trace each to a
   documented source? If not, rewrite or remove.

If any of (1)-(4) fails materially, the spec needs another pass before
committing.

## Optional: dispatch a faithfulness audit

For high-stakes apps, dispatch a sub-agent to re-verify after authoring.
Reference prompt:

```
Audit the reverse-engineered spec for `apps/<name>/` against the actual
code. Find fabrications, omissions, and misrepresentations.

Inputs: apps/<name>/spec/{BRIEF,ARCHITECTURE,SPEC}.md + apps/<name>/PATTERNS.md.
Source of truth: apps/<name>/app/* + every component yaml + every component
.js + the proxy/adapters.

For every concrete claim, classify as VERIFIED / FABRICATED /
MISREPRESENTED / OMITTED. Stop if you find > 10 fabrications and flag
the spec as needing major rework rather than a punch list.

Output: punch list with file:line evidence.
```

The 2026-05-06 chat audit ran this protocol and surfaced the 10
fabrications + 6 misrepresentations + 7 omissions that triggered this
reference file's existence.

## Shell-template-varies-per-rollup discipline (v1.10)

DO NOT paste a canonical shell template into SKILL.md / SPEC.md.
Different rollups load shells differently:

- **apps/saas + apps/tasks** — single inline `<style>` block in the
  shell `<head>`; bulk `/packages/web-components/index.js` import;
  page-DUO loader includes inner `try { import(...) } catch` block.
- **apps/user-flow** — 5 stylesheet `<link>` tags (tokens, components,
  resets, prose, sub-flow stylesheet); per-component
  `<script type="module" src=".../components/<name>/<name>.js">`
  imports; page-DUO loader DROPS the inner import block.

**Both are valid.** Neither is "the canonical pattern." Before authoring
shell templates in spec/skill files, READ the actual shell of the rollup
you're documenting (`Read apps/<name>/app/<sub>/<sub>.html`). Don't
generalize from a sibling rollup. The shell head is rollup-specific
load-order discipline that future authors must mirror, not a default
to assume.

Verification commands during the inventory pass:

```bash
# Count stylesheet <link> per shell (should be uniform across the rollup)
grep -c "stylesheet" apps/<name>/app/<some-page>/<some-page>.html

# Check for inner-import block (page-DUO with vs without)
grep -c "import(" apps/<name>/app/<some-DUO-page>/<some-DUO-page>.html
# 0 = leaner DUO loader (user-flow style)
# 1 = silent-catch DUO loader (saas/tasks style)

# Check stylesheet path style (relative vs absolute)
grep "stylesheet" apps/<name>/app/<some-page>/<some-page>.html | grep -E "^.*href=\"(\.\.|/)"
```

Document the result in PATTERNS as "shell template uniformity within
this rollup" + cite the exact pattern. Don't paste a template that
doesn't match the source.

## Cross-app stylesheet dependency: bilateral documentation rule (v1.10)

When one rollup's stylesheet is reused by another rollup (verified
2026-05-06: apps/errors → apps/user-flow/app/auth/auth.css for 3
error pages), the dependency creates a coupling that future authors
must discover from EITHER side.

The rule:

1. The **owner rollup** (where the stylesheet lives) documents the
   external consumers in PATTERNS + CHANGELOG ("Cross-app dependency
   from apps/X").
2. The **consumer rollup** documents the upstream link in PATTERNS
   + CHANGELOG + plan/ROADMAP ("Cross-app stylesheet dep on apps/Y/.../foo.css")
   AND in plan/MILESTONES if the dep is shipped.
3. Both rollups carry a matching OD ("Promote `<file.css>` to
   `apps/_shared/<sub>/<file.css>`?").

Verification at audit time:

```bash
# From the owner rollup, find external consumers
grep -rn "<owner-stylesheet>" apps/ | grep -v "<owner-rollup>/"

# From the consumer rollup, find upstream deps
grep -rn "apps/<other-rollup>/" apps/<this-rollup>/
```

If the bilateral documentation is missing on either side, the
foundation pass must add it before committing.

## Two-or-more parallel `total=` narratives in one sub-flow (v1.10)

When `<step-progress-ui>` markers in the same directory carry
different `total=` values (verified 2026-05-06: apps/user-flow/
registration uses both `total="10"` and `total="8"` across 18 sub-pages),
this is an **OD class**, not drift to silently document.

Detect with:

```bash
grep -rh "step-progress-ui" apps/<name>/app/<sub-flow>/ | \
  grep -oE 'total="[0-9]+"' | sort -u
```

If the result has > 1 line, surface as OD with three options:

1. **Intentional dual flows** (e.g., consumer/quick + B2B/enterprise)
   — preferred default; minimal churn; document each.
2. **Drift** (historical refactor left un-renamed pages)
   — heavy refactor; touches all sub-pages.
3. **Deploy-target variants** (one app uses one funnel,
   another uses the other) — needs deploy-target spec.

Resolution requires product owner input — don't pick on behalf of
the team.

## Triple-fire timing pattern (v1.10)

When a controller reads `.value` from a custom-element select on
mount (verified 2026-05-06 at apps/user-flow/registration/address/
address.contents.js:39-41), the standard fix is:

```js
sync();                  // 1. element already upgraded
queueMicrotask(sync);    // 2. upgrade resolves on next microtask
setTimeout(sync, 0);     // 3. upgrade defers behind macrotask
```

This is load-bearing — removing any one of the three fires regresses
on at least one upgrade-timing path. Document at PATTERNS-level (the
pattern + the why) and cite file:line in SKILL.

This is a workaround for upgrade-timing nondeterminism, not a
generic pattern. The cleaner fix would be a `whenUpgraded()` promise
on the element, but no such API exists in 2026-05.

## Quantitative-claim verification discipline (v1.10)

Pair every "N LoC", "N selectors", "N occurrences" claim with the
exact verification command. The 2026-05-06 user-flow audit caught:

- A 359 vs 358 LoC miscount in README — fix: `wc -l <file>`
- "16 selectors" vs 18 distinct vs 43 total occurrences — fix:
  `grep -oE "data-X-[a-z-]+" <file> | sort -u | wc -l`

Distinguish in claims:

| Claim form | Verification |
|---|---|
| "X LoC" | `wc -l <file>` |
| "N distinct attribute names" | `grep -oE "data-X-[a-z-]+" <file> \| sort -u \| wc -l` |
| "N total occurrences" | `grep -c "data-X-" <file>` |
| "N files" | `find <dir> -type f \| wc -l` |
| "N sub-pages" | `find <dir> -name "*.contents.html" \| wc -l` |

Don't conflate distinct-attr-names with total-occurrences. Don't
estimate ("~36" / "16-18") when verification is one grep away.

## Composition note: prefer chained `/plan-spec`

The cleanest reverse-engineering path is:

1. `/meta-app-scaffold` lays the layout (mechanical).
2. `/plan-spec` authors substantive spec content with the implementation
   files passed as the **research-survey basis** (not external research-survey).

`/plan-spec`'s research-protocol step grounds every claim in source. This
skill's manual reverse-engineering path is the fallback when `/plan-spec`
isn't available — but it's strictly worse for accuracy. Prefer the chained
flow when you can.
