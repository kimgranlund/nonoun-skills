# The message bridge — UI ⇄ sandbox

The two contexts talk **only** over `postMessage`, and the `pluginMessage` envelope is mandatory in
both directions. Getting the envelope wrong (reading `e.data` instead of `e.data.pluginMessage`, or
posting the bare payload) is the most common bridge bug.

## The four lines

```js
// ── sandbox → UI ──
figma.ui.postMessage({ type: "init", payload });        // code.js
window.onmessage = (e) => {                              // ui.html
  const msg = e.data.pluginMessage;                      //  ← .pluginMessage, NOT e.data
  if (msg && msg.type === "init") { /* … */ }
};

// ── UI → sandbox ──
parent.postMessage({ pluginMessage: { type: "apply", payload } }, "*");   // ui.html (note the envelope + "*")
figma.ui.onmessage = async (msg) => {                                     // code.js
  if (msg.type === "apply") { /* mutate the document */ }
};
```

- UI → sandbox: `parent.postMessage({ pluginMessage: X }, "*")`. The target origin is `"*"` (the
  iframe can't know Figma's origin). Figma unwraps it and calls `figma.ui.onmessage(X)`.
- Sandbox → UI: `figma.ui.postMessage(X)`. The UI receives a `message` event with `e.data = {
  pluginMessage: X, pluginId }`. **Read `e.data.pluginMessage`.**

## Patterns

**Init / "am I in Figma?"** — there is no synchronous global the UI can read to know it's inside Figma.
Have the sandbox announce itself, and reveal plugin-only controls on receipt:

```js
// code.js, right after showUI:
figma.ui.postMessage({ type: "figma-init" });
// ui.html:
addEventListener("message", (e) => {
  const m = e.data.pluginMessage;
  if (m && m.type === "figma-init") applyBtn.hidden = false; // only inside Figma
});
```

This is also how one bundle can serve **both** a normal web app and the plugin UI: the web app never
receives `figma-init`, so the Figma-only button stays hidden.

**Request → response** — tag a correlation id if the UI needs the answer to a specific request:

```js
// ui.html: parent.postMessage({pluginMessage:{type:"getSelection", id:42}}, "*")
// code.js: figma.ui.postMessage({type:"selection", id:42, nodes:[...]})
```

**Resize** — let the UI resize its own window: UI posts `{type:"resize", w, h}`; sandbox calls
`figma.ui.resize(w, h)`.

## Type the protocol (make illegal messages unrepresentable)

The bridge is a private contract between two files you own — so type it once and share it, rather than
sprinkling string literals. A discriminated union means neither side can send or handle a message shape
the other doesn't expect:

```ts
type ToSandbox = { type: "apply"; data: Bundle } | { type: "getSelection"; id: number };
type ToUI      = { type: "figma-init" } | { type: "selection"; id: number; nodes: NodeInfo[] };
// code.js: figma.ui.onmessage = (m: ToSandbox) => switch(m.type){…}  — exhaustive, no default needed
// ui.html: post only ToSandbox; handle only ToUI
```

Even in plain JS, keep the message `type` strings in **one shared list** referenced by both sides; a
typo in one half is the quiet "nothing happens" bug. An exhaustive `switch` on `type` (with the
no-op/unknown case logged) beats scattered `if (m.type === "…")` checks.

## Gotchas

- **The envelope.** Both directions need `pluginMessage`. A bare `parent.postMessage(payload)` never
  reaches `figma.ui.onmessage`.
- **Read side.** UI must read `e.data.pluginMessage` (sandbox already gets the unwrapped object).
- **Structured-clone only.** Messages are structured-cloned — pass **plain JSON-able data**. No DOM
  nodes, functions, class instances, or Figma node objects across the wire. Serialize first.
- **No shared memory.** The contexts share nothing; everything the sandbox needs from the UI (and
  vice-versa) crosses as a message payload.
