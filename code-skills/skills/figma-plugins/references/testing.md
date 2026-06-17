# Testing a plugin headlessly — mock the `figma` global

You can't run Figma in CI, but the sandbox's *logic* is plain JS that calls the `figma` API. Make the
plugin's document-mutating function **pure-ish over an injected `figma`**, then drive it with an
in-memory **mock** and assert the resulting collections/variables/nodes. This gates the whole
UI→sandbox→document contract without Figma.

## What to make testable

Factor the work into a function that takes a payload and uses the `figma` global:

```js
// code.js
async function applyBundle(data) { /* … figma.variables.* … */ return { raw, semantic }; }
figma.ui.onmessage = async (m) => { if (m.type === "apply") await applyBundle(m.data); };
```

`applyBundle` is what the test exercises.

## A minimal mock

Model only the API the code calls — collections + variables in memory, with `setValueForMode` and
`createVariableAlias`:

```js
function mockFigma() {
  const collections = [], variables = [];
  let id = 0;
  const figma = {
    showUI() {}, notify() {}, closePlugin() {},
    ui: { _h: null, postMessage() {}, set onmessage(f){ this._h = f; }, get onmessage(){ return this._h; } },
    variables: {
      async getLocalVariableCollectionsAsync() { return collections.slice(); },
      createVariableCollection(name) {
        const c = { id:"c"+id++, name, modes:[{modeId:"m"+id++, name:"Mode 1"}],
          renameMode(mid,nm){ const m=this.modes.find(x=>x.modeId===mid); if(m)m.name=nm; },
          addMode(nm){ const m={modeId:"m"+id++, name:nm}; this.modes.push(m); return m.modeId; } };
        collections.push(c); return c;
      },
      async getLocalVariablesAsync() { return variables.slice(); },
      createVariable(name, coll, type) {
        const v = { id:"v"+id++, name, variableCollectionId:coll.id, type, values:{},
          setValueForMode(mid,val){ this.values[mid]=val; } };
        variables.push(v); return v;
      },
      createVariableAlias(v) { return { type:"VARIABLE_ALIAS", id:v.id }; },
    },
  };
  return { figma, collections, variables };
}
```

## Loading code.js with the mock injected

`code.js` is a non-module sandbox script (no `export`). Load it with the mock as `figma`, exposing the
function under test:

```js
import { readFileSync } from "node:fs";
const code = readFileSync("code.js", "utf8");
const F = mockFigma();
const load = new Function("figma", "__html__", "module", code + "\nreturn { applyBundle };");
const { applyBundle } = load(F.figma, "<html>", undefined);   // closes over the MOCK figma
await applyBundle(payload);
// assert on F.collections / F.variables:
//   the expected collections exist with the expected modes,
//   N variables created with the right values,
//   every alias value is { type:"VARIABLE_ALIAS", id } pointing at a created raw var.
```

`new Function(code + "return {…}")` parses-and-runs `code.js` in a scope where `figma`/`__html__` are
params — so top-level `figma.showUI(...)` is a no-op on the mock, and the function under test closes
over the mock you control. (Guard any `if (typeof module !== "undefined") module.exports = …` so it's
inert here.)

> ⚠ **`new Function` runs the file's top level — only point it at code YOU authored.** This is the
> exact `eval`/`new Function`-on-untrusted-content the §SelfAudit trust boundary forbids. It is safe
> here because in BUILD/TEST *your own* `code.js` is the thing under test — first-party, not data you
> ingested. It is **not** safe in REVIEW when the plugin dir is a third-party artifact you're auditing:
> loading its `code.js` with `new Function` is arbitrary code execution with full `fs`/`process` scope.
> **For an under-review (untrusted) plugin: run `bin/check-figma-plugin.py` (pure static analysis, no
> execution) for the audit, and only ever execute it inside a locked-down `node:vm` context with no
> `require`/`fs`/`net` — or not at all.** The mock harness is a first-party regression tool, not an
> auditing sandbox.

## Static gate (no JS run)

`bin/check-figma-plugin.py` covers the mechanical floor: manifest shape, `main`/`ui` exist, offline
networkAccess, and **sandbox purity** — `code.js` calls no `document`/`fetch`/`XMLHttpRequest`/
`WebSocket`/`localStorage`/`import(` (stripping comments first, so a comment that *names* those APIs
to say it avoids them doesn't trip the check).

## What the mock can't cover

The mock proves your *logic*; it does NOT prove Figma accepts the manifest, the UI renders (the
single-file trap), the async-getter timing, or that values look right on canvas. Keep one **human
import-and-run** (the `## Verify Target`) as the real signal; the mock is the regression net beneath it.
