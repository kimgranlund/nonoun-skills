# figma.variables — collections, modes, and the alias cascade

Writing **variables** is the most common "design system" plugin job. The shape: a **collection** has
**modes** (e.g. Light/Dark); a **variable** holds one **value per mode**; a value is either a concrete
color or an **alias** to another variable (the cascade). All under `figma.variables.*`, all from the
**sandbox**.

## Color format — 0..1, not 0..255

A COLOR value is `{ r, g, b, a }` in **0..1 floats**:

```js
const rgba = { r: 255/255, g: 140/255, b: 33/255, a: 1 }; // == {r:1, g:0.549, b:0.129, a:1}
```

Convert at the boundary. W3C DTCG token `components` are already 0..1 — pass them straight. 8-bit hex
needs `/255`. A missing or doubled conversion is a silent wrong-color (it still "works", just wrong).

## Async under documentAccess: "dynamic-page"

With `"documentAccess": "dynamic-page"` (the recommended manifest setting) you MUST use the **async**
getters; the sync ones throw:

```js
const cols = await figma.variables.getLocalVariableCollectionsAsync();
const vars = await figma.variables.getLocalVariablesAsync();
// also: getNodeByIdAsync, loadFontAsync, getStyleByIdAsync, …
```

`createVariableCollection`, `createVariable`, `setValueForMode`, `createVariableAlias`, `addMode`,
`renameMode` are **synchronous**. Only the *getters* are async.

## Build a collection with modes

```js
async function ensure(name) {
  const cols = await figma.variables.getLocalVariableCollectionsAsync();
  return cols.find((c) => c.name === name) || figma.variables.createVariableCollection(name);
}

const sem = await ensure("Semantic");
const lightMode = sem.modes[0].modeId;              // a new collection has one default mode
sem.renameMode(lightMode, "Light");
const darkMode = (sem.modes[1] && sem.modes[1].modeId) || sem.addMode("Dark");
if (sem.modes[1]) sem.renameMode(darkMode, "Dark"); // addMode returns a modeId

const v = figma.variables.createVariable("brand/primary", sem, "COLOR"); // "a/b" → group "a", var "b"
v.setValueForMode(lightMode, { r: 0.1, g: 0.4, b: 0.9, a: 1 });
v.setValueForMode(darkMode,  { r: 0.4, g: 0.6, b: 1.0, a: 1 });
```

- A `/` in a variable name creates a **group** (`"brand/primary"` → group `brand`, var `primary`).
- Same names are fine in **different collections**.
- `createVariable(name, collection, "COLOR")` — also `"FLOAT" | "STRING" | "BOOLEAN"`.

## The alias cascade — what native JSON import can't do

A semantic variable that should *track* a raw one is set to an **alias**, not a copy. Editing the raw
value then propagates to every alias — the "live" design-token cascade:

```js
const raw = rawByName["brand/blue-600"];                       // a Variable object
semVar.setValueForMode(lightMode, figma.variables.createVariableAlias(raw));
semVar.setValueForMode(darkMode,  figma.variables.createVariableAlias(rawDark));
```

`createVariableAlias(variable)` takes the **Variable object** (resolve it first from your name index).
This is exactly the gap a plugin fills: Figma's native "import variables" can set concrete values but
not reliably wire cross-collection aliases — so a plugin reads/creates the raw collection, then aliases
the semantic collection to it.

## Idempotency

Re-running should not duplicate. **Find-or-create** by name every time:

```js
const byName = {};
for (const v of await figma.variables.getLocalVariablesAsync())
  if (v.variableCollectionId === coll.id) byName[v.name] = v;
const v = byName[name] || figma.variables.createVariable(name, coll, "COLOR");
```

After creating a batch, index from your in-memory map (don't re-fetch per variable — it's slow and the
new vars may not appear until the next async read).

## Reading the document (nodes), same rules

`figma.currentPage.selection`, `await figma.getNodeByIdAsync(id)`, `node.fills = [{type:"SOLID",
color:{r,g,b}, opacity}]`. Always async getters under dynamic-page; colors 0..1; from the sandbox only.
