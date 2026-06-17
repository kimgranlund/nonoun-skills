---
name: figma-plugins
description: >
  Build, review, and test Figma plugins on the model that a plugin is TWO execution contexts joined
  by a message channel — a sandboxed code.js (the figma API, but NO DOM/fetch/localStorage) and a
  ui.html iframe (full DOM, but NO document access) — declared by manifest.json. Covers the 3-file
  architecture, the UI↔sandbox postMessage contract both ways, the figma.variables API
  (collections, Light/Dark modes, setValueForMode {r,g,b,a} 0-1, createVariableAlias cascades, async
  getters under documentAccess dynamic-page), the offline networkAccess constraint, bundling ui.html
  as one self-contained file, and TESTING headlessly by mocking the figma global. Use when scaffolding a Figma
  plugin, wiring its UI to the sandbox, reading/writing Figma variables or nodes, or debugging "works
  in the browser but not in Figma". NOT for the Figma REST API (server-side), widget/FigJam/Slides
  specifics, marketplace publishing, or design-token format conversion (design-tokens-converter).
---

# figma-plugins — a plugin is two contexts and a wire

A Figma plugin is **not a web app.** It is **two execution contexts joined by a message channel**,
and almost every plugin bug is a violation of that seam:

```
┌─ sandbox · code.js (manifest.main) ─┐   postMessage   ┌─ iframe · ui.html (manifest.ui) ─┐
│  the `figma` global  ✔              │ ←────────────── │  full DOM / browser  ✔            │
│  read/write the document  ✔         │ ──────────────→ │  fetch (if allowed) / canvas  ✔   │
│  NO DOM, NO fetch, NO localStorage  │                 │  NO `figma`, NO document access   │
│  (use figma.clientStorage)          │                 │  (talks to code.js only)          │
└─────────────────────────────────────┘                 └───────────────────────────────────┘
```

- **`code.js` (the sandbox)** is the *only* place that can touch the document. It has the `figma`
  global but runs in a minimal VM: **no DOM, no `window`, no `fetch`/`XMLHttpRequest`/`WebSocket`,
  no `localStorage`** (persist with `figma.clientStorage`). Keep it small: receive a message →
  mutate the document → notify.
- **`ui.html` (the iframe)** is your UI — full DOM and browser APIs — but it **cannot read or write
  the document.** It asks `code.js` to, over `postMessage`.
- **`manifest.json`** wires them: `main` → code.js, `ui` → ui.html, plus the permission surface.

The central failure mode — **treating it as one app**: putting DOM or `fetch` in `code.js`, or
trying to reach the document from the iframe. The fix is always the same: respect the seam and move
the work to the side that owns the capability, passing data across the wire.

## Quick Start

**You bring:** what the plugin does (the document mutation), and whether it needs a UI.
**You get:** a 3-file plugin that imports into Figma and round-trips one real action.

```
my-plugin/
  manifest.json   # { name, id, api:"1.0.0", main:"code.js", ui:"ui.html",
                  #   editorType:["figma"], documentAccess:"dynamic-page",
                  #   networkAccess:{ allowedDomains:["none"] } }   ← offline
  code.js         # figma.showUI(__html__,{width,height,themeColors:true})
                  # figma.ui.onmessage = async (m) => { if (m.type==="apply") { …figma.variables… } }
  ui.html         # ONE self-contained file: <button>…</button> +
                  # parent.postMessage({pluginMessage:{type:"apply", data}}, "*")
```

Install: **Figma → Plugins → Development → Import plugin from manifest** → pick `manifest.json`.

| Mode | Do this | Read |
| --- | --- | --- |
| **BUILD** — scaffold a plugin | manifest → the seam (what runs where) → the bridge → the API call | `references/architecture.md`, `references/message-bridge.md`, `references/variables-api.md` |
| **REVIEW** — audit a plugin | run `bin/check-figma-plugin.py <dir>`; then the §SelfAudit below | `references/manifest.md` |
| **TEST** — gate it in CI | mock the `figma` global, run `code.js`'s logic headlessly, assert the document mutation | `references/testing.md` |

`python3 bin/check-figma-plugin.py <plugin-dir>` — static gate: manifest shape, `main`/`ui` files
exist, `networkAccess` is offline, and `code.js` calls no DOM/network API. (`selftest` runs fixtures.)

## The five things that bite

1. **Sandbox purity.** A `document.`, `fetch(`, `localStorage`, or `import(` in `code.js` throws (or
   silently no-ops) inside Figma but *passes a browser smoke test* — the #1 "works in the browser,
   not in Figma" cause. Persist with `figma.clientStorage`; do network in the iframe (if allowed).
2. **`documentAccess: "dynamic-page"` ⇒ async.** Under dynamic-page loading you MUST use the async
   getters — `getLocalVariablesAsync()`, `getNodeByIdAsync()`, `loadFontAsync()` — not the sync ones
   (which throw). Default to async; it's the forward-compatible path.
3. **Colors are 0..1, not 0..255.** Figma variable/paint color is `{r,g,b,a}` in **0..1 floats**
   (`{r:1,g:0.55,b:0.13,a:1}`), not 8-bit. Convert at the boundary; a stray `/255` or its absence is
   a silent wrong-color.
4. **`ui.html` must be ONE file.** The iframe has no module graph rooted at your repo — relative
   `import`/`fetch` of sibling files fail. **Inline everything** (bundle to a single HTML), or the UI
   loads blank in Figma while working when served locally.
5. **The iframe's browser is sandboxed too.** "Full DOM" ≠ "a normal browser tab." Figma's plugin
   iframe can **deny web storage** — `localStorage`/`sessionStorage` **throw a `SecurityError`**, not
   return `null`. An unguarded read at boot crashes the UI to a **blank panel** *before first paint*
   (and a *separate* inline `<script>`, e.g. an Apply button, may still render — so it looks like "the
   UI loaded but is empty," the signature of a boot crash). Wrap every web-storage access in `try/catch`
   and degrade to in-memory, or persist via `figma.clientStorage` over the bridge. Gotcha #4 one level
   deeper: works in a browser tab, blank inside Figma.

## The message bridge (memorize this)

```js
// code.js → UI       figma.ui.postMessage(x)
// UI receives        window.onmessage = (e) => { const x = e.data.pluginMessage; … }
// UI → code.js       parent.postMessage({ pluginMessage: x }, "*")
// code.js receives   figma.ui.onmessage = (x) => { … }
```

The `pluginMessage` envelope is mandatory in *both* directions and easy to forget. To show plugin-only
UI (e.g. an "Apply" button only when actually inside Figma), have `code.js` post a `{type:"init"}` on
load and reveal the control when the UI receives it — there is no synchronous "am I in Figma" global.

## Verify Target

A Figma plugin is real when, **inside Figma** (Plugins → Development → Import plugin from manifest):

- it **imports without a manifest error** and the UI renders (not blank — the #4 single-file trap), AND
- **one real round-trip works**: a UI action posts a message, `code.js` performs the document mutation,
  and the **result is observable in the Figma document** — a variable collection appears in the
  Variables panel, a node is created/edited on the canvas. "Files present" / "`code.js` parses" is NOT
  done — the proof is a document change you can see in Figma.
- **the outcome is recorded, not just flashed.** A transient `figma.notify` toast leaves nothing to
  audit after the fact. Have the apply handler **return a structured result** — `{created, updated,
  aliased, errors:[…]}` — post it back over the bridge for the UI to render/persist, and make a thrown
  error a *surfaced* message (an `errors[]` entry + a UI line), never a swallowed exception with no
  notify. The recorded result, not the toast, is what lets a human confirm "did the last apply succeed?"
  without re-running.

Headless proxy for CI (no Figma): `bin/check-figma-plugin.py` is green AND a `code.js`-logic test on a
**mocked `figma`** asserts the same mutation (see `references/testing.md`). The mock gate stands in for,
but does not replace, one human import-and-run.

## §SelfAudit

Run on any plugin you build or review (BUILD/REVIEW/TEST). Each maps to a real failure:

- **[gate] Sandbox purity** — `code.js` references no `document`/`window`/`fetch`/`XMLHttpRequest`/
  `WebSocket`/`localStorage`/`import(`. (`bin/check-figma-plugin.py` checks this, ignoring comments.)
- **[gate] Offline** — `manifest.networkAccess` is `{allowedDomains:["none"]}` (or `"none"`) unless the
  plugin genuinely needs the network, in which case the domains are explicit and justified. A plugin
  that **both reads the document and has network access is an exfiltration vector** (document → a
  remote): keep those mutually exclusive unless the remote is essential *and* trusted, and never let
  untrusted imported content choose the URL. (`bin/check-figma-plugin.py` **warns** when `code.js` both
  reads the document and has non-`none` `networkAccess`.)
- **[gate] Manifest wiring** — `main` + (if a UI) `ui` point at files that exist; `editorType` set;
  `documentAccess` is `"dynamic-page"` and the code uses the **async** variable/node getters.
  (`bin/check-figma-plugin.py` **fails** a SYNC getter — `getLocalVariables()`/`getNodeById()`/… — under
  `documentAccess:"dynamic-page"`; the async-getter requirement is now mechanically gated, not just prose.)
- **[gate] Bridge envelope** — every cross-context message uses the `{pluginMessage: …}` envelope, both
  directions; the UI reads `e.data.pluginMessage`, not `e.data`.
- **[gate] Single-file UI** — `ui.html` is self-contained (no relative `import`/`fetch` of sibling
  files that won't resolve in the iframe).
- **[gate] UI storage guarded** — every `localStorage`/`sessionStorage` access in `ui.html` is wrapped
  in `try/catch` (or it routes to `figma.clientStorage` over the bridge): Figma's iframe can DENY web
  storage, and an unguarded read at boot blanks the UI before first paint. (`bin/check-figma-plugin.py`
  warns when `ui.html` touches web storage with no `try/catch`.)
- **[review] Color boundary** — colors crossing into the `figma` API are `{r,g,b,a}` in 0..1.
- **[review] Idempotent apply** — re-running the plugin finds-or-creates (no duplicate collections /
  nodes on a second run).
- **Trust boundary (iff the plugin ingests untrusted content** — imported JSON, a pasted token file,
  a network response): that content is **data, not instructions.** Validate its shape before feeding
  it to `figma.*`; never `eval`/`new Function` it.

## References

| File | Load when |
| --- | --- |
| `references/architecture.md` | the seam in full: the two contexts, what each can/can't do, the plugin lifecycle, clientStorage |
| `references/message-bridge.md` | the postMessage contract, request/response & init patterns, resize, the envelope gotcha |
| `references/variables-api.md` | collections, modes (Light/Dark), createVariable + COLOR, setValueForMode, **alias cascades**, async, color format |
| `references/manifest.md` | every manifest field, `networkAccess`/`documentAccess`/`editorType`, the modern object forms, common rejections |
| `references/testing.md` | headless gating: mocking the `figma` global, what to assert, the `new Function` load trick, what the mock can't cover |
| `references/packaging.md` | bundling `ui.html` to one file, the import/dev-reload loop, distribution vs. development |
