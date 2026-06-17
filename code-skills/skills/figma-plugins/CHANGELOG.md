# Changelog — figma-plugins

## 0.1.2 — 2026-06-17 — full 9-critic promote review (verdict CONDITIONAL → stays draft)

Ran the skills-studio `promote` complete review: Stage-0 gates, D1–D10 holistic scan, and the full
9-critic council. Three Criticals blocked `stable`; folded the cheap+correct findings, deferred the
expensive ones to the ROADMAP gate. **Status stays `draft`.**

- **Stage-0 fix:** the description contained angle brackets (`UI<->sandbox`) → `quick_validate --strict`
  rejected it. Replaced with `UI↔sandbox` in `SKILL.md` + `skill.json`.
- **Simon (Critical) — `new Function` self-contradiction.** `testing.md` recommended loading `code.js`
  via `new Function`, which the §SelfAudit trust boundary forbids for untrusted content. Scoped it
  explicitly to **first-party** code (BUILD/TEST); for an under-review third-party plugin, run the static
  `bin/` gate and only ever execute inside a locked-down `node:vm`.
- **Charity (Critical) — unrecorded Verify Target.** A transient `figma.notify` leaves nothing to audit.
  The Verify Target now requires the apply handler to **return a structured result** (`{created, updated,
  aliased, errors[]}`) surfaced over the bridge, and a thrown error to be a *surfaced* message — so "did
  the last apply succeed?" is answerable without re-running.
- **`[gate]` inflation (Boris/Huyen/Karpathy/Simon/Wlaschin/Farley) — mechanized two convergent checks.**
  `check-figma-plugin.py` now **fails** a SYNC getter under `documentAccess:"dynamic-page"` (gotcha #2,
  async naturally excluded) and **warns** on the document-read + network exfiltration trifecta. §SelfAudit
  updated to point at the now-mechanized checks; two new selftest fixtures each way.
- **Asserted-not-measured F1 (Boris/Karpathy/Huyen).** `routing-corpus.json` `_note` no longer claims a
  measured "F1 1.0" — relabelled author-estimated/hypothesis, with the scorer-run owed before stable.
- **Dangling routes (Steve).** Fixed adversarial routes that named non-existent skills (`brand-or-color`
  → `brand-studio`; the REST-API adversarial → `none`).
- **Elon (Critical) — N=1 overclaim** + **behavioral evals / 2nd-plugin generalization**: deferred to the
  ROADMAP "Validation owed before stable" gate (genuinely expensive; can't be folded in a doc pass).

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
