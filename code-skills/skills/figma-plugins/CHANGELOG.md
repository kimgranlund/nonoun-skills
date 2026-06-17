# Changelog — figma-plugins

## 0.1.1 — 2026-06-16 — the sandboxed-iframe storage trap

Folded a hard-won lesson from running the HCT generator as a plugin: Figma's plugin **iframe** can deny
web storage — `localStorage`/`sessionStorage` **throw a `SecurityError`**, not return `null` — so an
unguarded read at UI boot blanks the panel (works in a browser tab, blank in Figma; a *separate* inline
`<script>` such as an Apply button still renders, masking it as "loaded but empty").

- **SKILL.md:** "the four things that bite" → **five** (the iframe's browser is sandboxed too); new
  §SelfAudit gate **[gate] UI storage guarded**.
- **references/architecture.md:** the persistence cell now reads `localStorage` **may throw**; added the
  blank-panel callout (the boot-crash signature vs. a layout bug).
- **bin/check-figma-plugin.py:** advisory `WARN` when `ui.html` touches web storage with **no `try/catch`
  anywhere** (a guarded plugin is assumed deliberate → silent); two new selftest fixtures (unguarded
  warns, guarded stays silent); storage is advisory and never fails the hard gate. Real plugin dogfoods
  clean.

## 0.1.0 — 2026-06-16 — initial draft

Distilled from building the HCT Palette Generator as a Figma plugin (the generator UI running
inside Figma, writing variable collections directly). First release.

- **Spine:** a plugin is **two execution contexts joined by a message channel** — sandbox (`code.js`,
  the `figma` API, no DOM/network) ⇄ iframe (`ui.html`, the DOM, no document access) — declared by
  `manifest.json`. Most plugin bugs are violations of that seam.
- **Modes:** BUILD (scaffold) · REVIEW (audit) · TEST (headless gate).
- **References:** `architecture` (the seam + lifecycle), `message-bridge` (the postMessage contract +
  the `pluginMessage` envelope + init detection), `variables-api` (collections/modes/createVariable/
  setValueForMode/createVariableAlias, async under dynamic-page, 0..1 color), `manifest` (every field +
  networkAccess/documentAccess/editorType), `testing` (mock the `figma` global, the `new Function` load
  trick), `packaging` (single-file ui.html, the dev loop).
- **Mechanization:** `bin/check-figma-plugin.py` — static gate (manifest shape, files exist, offline
  networkAccess, sandbox purity with comments stripped), self-tested with good/bad/comment fixtures.
- **§SelfAudit:** sandbox purity · offline · manifest wiring · the bridge envelope · single-file UI ·
  color boundary · idempotent apply · a trust boundary for untrusted imported content.
- **Routing corpus:** 12 triggers / 6 adversarials (adversarials route to design-tokens-converter,
  maintain-tokens, or out-of-scope: REST API / widgets / publishing).
- **Build-time red-team (Simon + Wlaschin floor):** folded two findings — (Simon) named the
  document-read + network **exfiltration trifecta** in the offline §SelfAudit gate; (Wlaschin) added a
  "type the protocol" section (discriminated message union → illegal messages unrepresentable). Full
  9-critic panel deferred to pre-`stable` (see ROADMAP).
