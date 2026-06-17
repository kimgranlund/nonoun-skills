# Architecture — the two contexts and the lifecycle

## The seam

A Figma plugin runs as **two isolated JS realms** that share no scope and no globals:

| | `code.js` — the **sandbox** (`manifest.main`) | `ui.html` — the **iframe** (`manifest.ui`) |
| --- | --- | --- |
| Globals | `figma`, `console`, standard JS | `window`, `document`, DOM, `console`, standard JS |
| Can touch the document | **yes** (the only place) | **no** |
| DOM / rendering | **no** | yes |
| Network | **no** by default (and discouraged) | `fetch`/etc. **iff** `manifest.networkAccess` allows the domain |
| Persistence | `figma.clientStorage` (async, plugin-scoped) | `localStorage` works but is iframe-scoped & cleared aggressively — prefer routing to clientStorage |
| Module system | a single file; no `import` of siblings at runtime | a single file; the iframe has no repo-rooted module graph |

They communicate **only** by message passing (see `message-bridge.md`). Treating them as one app is
the master failure: DOM/`fetch` in the sandbox, or document access from the iframe.

## When you need each

- **No UI** (a command that just acts): ship `code.js` only — omit `ui` from the manifest. `code.js`
  does its work and calls `figma.closePlugin()`. Example: a one-shot "rename selected layers."
- **With UI** (controls, a generator, a preview): `code.js` calls `figma.showUI(__html__, opts)` to
  open `ui.html`; the UI drives the work by posting messages back.

`__html__` is a magic global in `code.js` — the bundled contents of `manifest.ui`, injected by Figma.

## Lifecycle

```
load manifest → run code.js (top level)
            → (optional) figma.showUI(__html__, { width, height, themeColors:true })
            → figma.ui.onmessage handles UI → sandbox messages
            → mutate the document via figma.* (async getters under dynamic-page)
            → figma.notify("done")  and/or  figma.closePlugin()
```

`code.js` top level runs **once** on launch. Register `figma.ui.onmessage` there; don't do heavy work
at top level — wait for the UI (or, no-UI, do it then `closePlugin`).

## Capability boundaries to respect

- **Read selection / nodes / variables** → sandbox (`figma.currentPage.selection`, `figma.variables.*`).
- **Render a chart, run a color engine, build complex UI** → iframe (it has the DOM/canvas), then
  post the *result* (data, not DOM) to the sandbox to write.
- **Fetch remote data** → iframe (with `networkAccess` domains), post the result to the sandbox.
- **Persist plugin state across runs** → `await figma.clientStorage.setAsync(key, value)` /
  `getAsync(key)` in the sandbox. (Not `localStorage`.)

## Worked shape (a generator plugin)

The HCT generator this skill was distilled from runs its whole UI (a web component) in `ui.html`, and
`code.js` is a thin sandbox: on an "apply" message it walks a posted token bundle into Figma variable
collections. The UI never touches the document; the sandbox never touches the DOM. That division is
the template for any "rich UI that writes to the document" plugin.
