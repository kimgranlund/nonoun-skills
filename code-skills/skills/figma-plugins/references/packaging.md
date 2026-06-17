# Packaging — the single-file UI + the dev loop

## ui.html must be ONE self-contained file

The iframe is loaded as the literal contents of `manifest.ui` (injected into the sandbox as
`__html__`). It is **not** served from your repo, so it has no module graph and no base URL for
relative paths:

- `<script type="module" src="./app.js">` or `import "./model.js"` → **fails** in Figma (no sibling to
  fetch), even though it works when you serve the folder locally. This is the #1 "UI is blank in
  Figma" cause.
- Inline **everything**: all JS in `<script>`, all CSS in `<style>`, assets as data-URIs. Produce one
  HTML file.

If your UI is a real app (a framework, a web component, multiple modules), **bundle it to a single
HTML** as a build step, then point `manifest.ui` at the bundle. Generating `ui.html` from a bundle
keeps one source of truth:

```js
// gen-ui.mjs — ui.html = the offline single-file bundle + a Figma bridge injected before </body>
const src = readFileSync("dist/app.html", "utf8");
const bridge = `<button id="apply" hidden>Apply</button>
<script>
  addEventListener("message",e=>{var m=e.data&&e.data.pluginMessage;if(m&&m.type==="figma-init")apply.hidden=false;});
  apply.addEventListener("click",()=>parent.postMessage({pluginMessage:{type:"apply",data:getData()}},"*"));
</script>`;
writeFileSync("ui.html", src.replace("</body>", bridge + "</body>"));
```

The bridge is the only Figma-specific code; the app itself stays unchanged and still runs as a normal
web app (it just never receives `figma-init`, so the Figma button stays hidden).

## The dev loop

1. **Import once**: Figma → Plugins → Development → **Import plugin from manifest** → `manifest.json`.
2. **Edit + re-run**: change `code.js`/`ui.html` (rebuild the bundle if you generate `ui.html`), then
   re-run the plugin (it re-reads the files each launch). Figma's **Plugins → Development → Hot reload**
   reloads on file change.
3. **Console**: open the dev console (Plugins → Development → Show/Hide console, or the browser
   devtools in the desktop app) to see `console.log` from both `code.js` and `ui.html`.

A regenerated `ui.html`/`code.js` is picked up on the next run — but if you changed the *manifest*
(new `ui`/`main`/permissions), re-import it.

## Distribution vs. development

- **Development** (what this skill covers): import-from-manifest, local files, no review.
- **Publishing**: Figma's review process, an assigned plugin `id`, screenshots/description, optional
  payments — out of scope here; the *code* shape is identical, the surrounding metadata differs.

## Checklist before you import

- `ui.html` is one self-contained file (no relative `import`/`fetch`).
- `manifest.main`/`ui` point at files that exist.
- `networkAccess` is `["none"]` (or an explicit, justified allowlist).
- `code.js` is sandbox-pure and uses async getters under `documentAccess:"dynamic-page"`.
- `bin/check-figma-plugin.py <dir>` is green.
