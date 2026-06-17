# manifest.json — the wiring + the permission surface

The manifest declares the two files and the plugin's capabilities. Figma rejects an invalid manifest
at import time (before any code runs), so shape errors here are the first thing to get right.

```json
{
  "name": "My Plugin",
  "id": "my-plugin",
  "api": "1.0.0",
  "main": "code.js",
  "ui": "ui.html",
  "editorType": ["figma"],
  "documentAccess": "dynamic-page",
  "networkAccess": { "allowedDomains": ["none"] }
}
```

## Fields

| Field | Notes |
| --- | --- |
| `name` | display name in the plugins menu |
| `id` | unique id (for published plugins, Figma assigns one; any stable string works in development) |
| `api` | the plugin API version — `"1.0.0"` |
| `main` | **the sandbox file** (`code.js`). Required. |
| `ui` | **the iframe file** (`ui.html`). Omit for a no-UI command plugin. |
| `editorType` | `["figma"]`, `["figjam"]`, `["dev"]`, `["slides"]` — where it runs. Many APIs (e.g. variables) are figma-only. |
| `documentAccess` | use `"dynamic-page"` (the modern default) — pages load on demand ⇒ use the **async** getters. |
| `networkAccess` | the network permission surface (below) |
| `menu`, `parameters`, `relaunchButtons`, `capabilities` | optional surfaces (submenus, quick params, relaunch entries) |

## networkAccess — be offline unless you aren't

The **modern form is an object**:

```json
"networkAccess": { "allowedDomains": ["none"] }                       // fully offline (preferred)
"networkAccess": { "allowedDomains": ["https://api.example.com"] }     // explicit allowlist
"networkAccess": { "allowedDomains": ["*"], "reasoning": "why" }       // wildcard needs a reason
```

- The older string `"networkAccess": "none"` is still seen in the wild; prefer the object form.
- `allowedDomains` constrains what the **UI iframe** may `fetch` — the sandbox never does network.
- **Default to `["none"]`.** A design-system/token plugin needs zero network; declaring it offline is
  both correct and a trust signal. Only widen when a real remote call exists, and list exact domains.

## editorType + capability mismatch

A plugin that calls `figma.variables.*` but declares `editorType:["figjam"]` will fail at runtime —
the API surface differs per editor. Match `editorType` to the APIs you call.

## Common import-time rejections

- `main` (or `ui`) points at a file that doesn't exist next to the manifest.
- `networkAccess` malformed (string where an object is expected by the current schema, or missing).
- `editorType` missing/empty.
- `documentAccess` omitted while the code uses async page APIs that require it — set `"dynamic-page"`.

`bin/check-figma-plugin.py` catches the mechanical ones (missing `main`/`ui` files, non-offline
networkAccess without justification, sandbox impurity) before you import.
