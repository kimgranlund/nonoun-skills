---
date: 2026-04-27
coverage: extended
peers:
  - ../products/sveltekit.md
  - ../products/nuxt.md
  - ../products/solidstart.md
  - ../meta/the-modern-baseline.md
  - ../runtime-polyfills/cookie-store-api.md
  - ../build-tools/browserslist-recipes.md
  - ../anti-patterns/target-es5-modern.md
primary_sources:
  - https://lit.dev/ — Lit official site
  - https://lit.dev/docs/releases/upgrade/ — Lit 3 upgrade guide (ES2021 target)
  - https://lit.dev/docs/ssr/overview/ — Lit SSR (declarative shadow DOM)
  - https://github.com/lit/lit — Lit repo
  - https://stenciljs.com/ — Stencil official site
  - https://stenciljs.com/docs/server-side-rendering — Stencil SSR docs
  - https://github.com/stenciljs/core/blob/main/CHANGELOG.md — Stencil changelog
  - https://fast.design/ — Microsoft FAST
  - https://github.com/microsoft/fast — FAST repo
  - https://github.com/microsoft/fast/issues/5849 — future of FAST Components RFC
  - https://caniuse.com/wf-scoped-custom-element-registries — scoped registries support data
  - https://www.npmjs.com/package/@webcomponents/scoped-custom-element-registry — official polyfill
  - https://www.npmjs.com/package/@webcomponents/webcomponentsjs — legacy bundle (don't ship at baseline)
  - https://web.dev/articles/declarative-shadow-dom — Declarative Shadow DOM article
---

# Web Components frameworks — polyfill posture at the modern baseline

Lit, Stencil, FAST, and the broader web-components ecosystem all assume modern browsers. At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+), the historical web-components polyfill story — `@webcomponents/webcomponentsjs`, the custom-elements polyfill, the shadow-DOM polyfill — is largely obsolete. The one feature that still requires a polyfill is **Scoped Custom Element Registries** for Firefox; everything else is native.

> The TL;DR: Stop shipping `@webcomponents/webcomponentsjs`. ElementInternals, Form-Associated Custom Elements, Declarative Shadow DOM, and `:state()` are all native at our baseline. The single live polyfill candidate is scoped element registries, and only for Firefox.

## What's native at our baseline

The canonical web-components surface, all shipped across every baseline engine:

| Feature | Status at baseline | Notes |
|---|---|---|
| **Custom Elements v1** | Universal | Chrome 54, Firefox 63, Safari 10.1 |
| **Shadow DOM v1** (`attachShadow`) | Universal | Chrome 53, Firefox 63, Safari 10 |
| **`<template>`, `<slot>`** | Universal | Pre-baseline by years |
| **HTML Imports** | **DEAD** | Removed from spec; never shipped in Firefox/Safari; Chrome removed Feb 2020 |
| **ElementInternals** (`attachInternals()`) | Native | Chrome 90, Firefox 126, Safari 17.4 — at baseline |
| **CustomStateSet** (`:state()` pseudo-class) | Native | Chrome 121, Firefox 126, Safari 17.4 — at baseline |
| **Form-Associated Custom Elements** (FACE) | Native | Chrome 90, Firefox 126, Safari 17.4 — at baseline |
| **Declarative Shadow DOM** (`<template shadowrootmode>`) | Native | Chrome 111, Firefox 123, Safari 16.4 — Baseline Aug 2024 |
| **`adoptedStyleSheets`** | Native | Chrome 73, Firefox 101, Safari 16.4 |
| **Constructible stylesheets** (`new CSSStyleSheet()`) | Native | Chrome 73, Firefox 101, Safari 16.4 |

Everything above was a polyfill candidate at some point; none are at this baseline. **Shipping `@webcomponents/webcomponentsjs` to users on these engines is bundle bloat and slows page load.** It loads code that no modern browser needs.

## What's NOT native at our baseline

The single live polyfill candidate at our baseline:

| Feature | Status | Polyfill |
|---|---|---|
| **Scoped Custom Element Registries** | Safari 26 (Sept 15, 2025) ✓; Chrome 146 (March 10, 2026) ✓; **Firefox: not shipped** | `@webcomponents/scoped-custom-element-registry` (Firefox only) |

[`caniuse.com/wf-scoped-custom-element-registries`](https://caniuse.com/wf-scoped-custom-element-registries) tracks the support matrix. At our baseline, **Safari and Chrome ship native** (recent additions — Safari 26 was the first to ship; Chrome 146 followed); **Firefox 129–latest does not**. If you authored against the spec and ship to Firefox at our floor, the polyfill is required.

## Lit 3+

[Lit](https://lit.dev/) is the most-deployed web-components library. Maintained by Google, MIT-licensed, ~5KB minified + gzipped.

| Component | Current | Notes |
|---|---|---|
| **Lit** | **3.3.x** (latest 3.3.2, Dec 2025) | ES2021 target; smaller and faster than Lit 2 |

[Lit 3 is published as ES2021](https://lit.dev/docs/releases/upgrade/) — wider syntax support than Lit 2's ES2019 publishing target. At our baseline (every engine fully supports ES2024) you can re-bundle without lowering. **Lit ships no polyfills**; it assumes the platform has Custom Elements, Shadow DOM, and `Promise`. Every assumption is met at our baseline.

The Lit 3 upgrade note: most apps move from `^2.0.0` to `^2.0.0 || ^3.0.0` with no code changes. Lit 3 dropped IE11 support — irrelevant at our baseline.

### Lit SSR

[`@lit-labs/ssr`](https://lit.dev/docs/ssr/overview/) renders Lit components to HTML on the server, emitting Declarative Shadow DOM (`<template shadowrootmode>`). On the client, `@lit-labs/ssr-client/lit-element-hydrate-support.js` rehydrates. The client polyfill — `template-shadowroot` — used to be needed for browsers without DSD, but **DSD is native at our baseline**, so the polyfill is no longer required.

## Stencil 4

[Stencil](https://stenciljs.com/) is Ionic's TypeScript-decorator-based web-components compiler. Apache 2.0, ships ~30 utility runtime KB depending on output target.

| Component | Current | Notes |
|---|---|---|
| **Stencil** | **4.43.4** (April 13, 2026) | TypeScript decorator API; SSR via `@stencil/ssr` |

Stencil's compiler emits modern JavaScript by default. The transpile option exposes the JS target — `es2017` is the recommended modern target; lower (e.g. `es5`) only if you genuinely need legacy support. **At our baseline, set `transpile.target: 'es2022'` or higher** — every baseline engine supports it.

Historical note: Stencil supported a differential build with separate ES5 + ES2017 bundles for IE11 vs modern browsers. At this baseline, set `buildEs5: false` (the default in Stencil 4) and ship only the modern bundle.

### Stencil SSR

Stencil 4 ships [SSR support](https://stenciljs.com/docs/server-side-rendering) for React and Vue output targets, plus auto-detected enhancements for Vite, Remix, Next.js, and Nuxt. The compiler emits Declarative Shadow DOM during SSR (or scoped-mode markup as fallback). DSD is native at baseline; no polyfill needed for hydration.

## Microsoft FAST

[FAST](https://fast.design/) is Microsoft's web-components framework — `@microsoft/fast-element` (the lightweight authoring library), `@microsoft/fast-foundation` (component compositions), and `@fluentui/web-components` (Fluent design system on top).

Status as of April 2026: FAST is in a maintenance posture — fast-element and fast-foundation continue nightly publishes ([RFC #5849](https://github.com/microsoft/fast/issues/5849)) but the team has signaled the project's focus is platform gap-filling rather than producing components themselves. `@fluentui/web-components` (the Fluent UI layer) remains the most active downstream consumer.

FAST targets modern browsers. Polyfill posture: nothing exotic; the same custom-elements + shadow-DOM assumptions as Lit and Stencil. **Skip `@webcomponents/webcomponentsjs`** at our baseline.

## Scoped Custom Element Registries — the only live polyfill

Per the WICG proposal ([implementation history](https://wicg.github.io/webcomponents/proposals/Scoped-Custom-Element-Registries.html)), scoped registries let multiple constructors register the same tag name within different `ShadowRoot` scopes. Useful for component libraries that want to avoid global tag-name collisions.

**Browser support timeline**:

- **Safari 26** — September 15, 2025 — first to ship native.
- **Chrome 146** — March 10, 2026 — second engine to ship.
- **Firefox** — not shipped, no implementation in progress as of April 2026.

At our baseline (Firefox 129+ floor), Firefox is **17+ versions behind** Safari/Chrome and shows no near-term implementation. If you author against scoped registries and your audience includes Firefox, you need the polyfill.

### `@webcomponents/scoped-custom-element-registry`

[Official polyfill](https://www.npmjs.com/package/@webcomponents/scoped-custom-element-registry) maintained by the webcomponents/polyfills repo (Google + Lit team). Apache 2.0. Implementation uses native CustomElements to register stand-in classes that delegate to the constructor in the registry for the element's scope — avoiding manual tree walks for upgrade.

```html
<script src="/node_modules/@webcomponents/scoped-custom-element-registry/scoped-custom-element-registry.min.js"></script>
```

Or via npm + bundler:

```js
import '@webcomponents/scoped-custom-element-registry';
```

**Known caveat on Firefox**: a long-standing issue ([webcomponents/polyfills#580](https://github.com/webcomponents/polyfills/issues/580)) — events do not propagate upward outside the web-component on Firefox specifically. Affects all events, not just MouseEvents. Reported with Lit-element v3 and polyfill v0.0.9. If you hit it, either drop the polyfill (and lose the feature on Firefox) or upgrade to a version with the fix; verify against the issue tracker before adopting.

The community alternative is [`scoped-registries`](https://github.com/manolakis/scoped-registries) by manolakis — different implementation, same goal.

### Feature detection

Gate via:

```js
if ('CustomElementRegistry' in window
    && CustomElementRegistry.prototype.constructor.length > 0) {
  // native scoped registries available
}
```

Or load the polyfill conditionally:

```js
if (!('CustomElementRegistry' in window
      && CustomElementRegistry.prototype.constructor.length > 0)) {
  await import('@webcomponents/scoped-custom-element-registry');
}
```

## `@webcomponents/webcomponentsjs` — stop shipping it

[`@webcomponents/webcomponentsjs`](https://www.npmjs.com/package/@webcomponents/webcomponentsjs) is the historical bundle covering Custom Elements + Shadow DOM + HTML Imports. **At our baseline, every feature it polyfilled is native.** Shipping it loads code no engine needs and slows page load.

The package isn't formally deprecated — it's still useful for IE11 support, which is out of scope here. The `webcomponents-loader.js` variant only loads polyfills the specific browser actually needs, but at our baseline it loads nothing useful. Strip the dependency.

## Recommended setup at our baseline

For a pure web-components project (no Lit / Stencil / FAST):

```html
<!-- index.html -->
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Modern web components</title>
  </head>
  <body>
    <my-element></my-element>
    <script type="module" src="/src/my-element.js"></script>
  </body>
</html>
```

```js
// src/my-element.js — ES2022+ class authoring, no polyfills needed
class MyElement extends HTMLElement {
  static observedAttributes = ['count'];
  #internals = this.attachInternals();

  connectedCallback() {
    this.attachShadow({ mode: 'open' }).innerHTML = `
      <style>:host { display: block; padding: 1rem; }</style>
      <slot></slot>
    `;
  }
}
customElements.define('my-element', MyElement);
```

For Lit 3:

```js
// vite.config.ts (Lit + Vite)
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: ['chrome125', 'safari17.4', 'firefox129'],
  },
});
```

For Stencil 4:

```ts
// stencil.config.ts
import { Config } from '@stencil/core';

export default {
  namespace: 'my-components',
  buildEs5: false,
  outputTargets: [{ type: 'dist' }, { type: 'docs-readme' }],
} satisfies Config;
```

For Firefox + scoped registries (if you use them):

```js
// entry.ts — load polyfill before any element registration
if (!('CustomElementRegistry' in window
      && CustomElementRegistry.prototype.constructor.length > 0)) {
  await import('@webcomponents/scoped-custom-element-registry');
}
// then your element imports
import './components/my-button.js';
```

## Common web-components polyfill mistakes (the audit checklist)

The five patterns most likely to appear in real projects:

1. **`@webcomponents/webcomponentsjs` shipped unconditionally.** Loads code no modern engine needs. Strip at this baseline.
2. **Lit 1 or Lit 2 in a project that could be Lit 3.** Lit 3's ES2021 publishing target produces smaller bundles at our baseline; the upgrade is usually `npm install lit@^3` with no code changes.
3. **Stencil's `buildEs5: 'prod'` or default-on legacy build.** Doubles output. Set `buildEs5: false` (Stencil 4 default).
4. **Scoped registries used without Firefox polyfill.** Code works in Safari 26+ and Chrome 146+ but breaks silently on Firefox. Either polyfill or feature-gate.
5. **Declarative Shadow DOM hydration polyfill (`template-shadowroot`) shipped at baseline.** Native everywhere; the polyfill is unnecessary overhead. Strip it.

## Cross-references

- [`./sveltekit.md`](./sveltekit.md), [`./nuxt.md`](./nuxt.md), [`./solidstart.md`](./solidstart.md) — meta-frameworks that may host web components.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — full feature support table (web-platform section covers the WC surface).
- [`../runtime-polyfills/cookie-store-api.md`](../runtime-polyfills/cookie-store-api.md) — different angle on polyfilling for incomplete browser surface.
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical browserslist queries.
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — why Stencil's ES5 differential build is wrong at this baseline.
