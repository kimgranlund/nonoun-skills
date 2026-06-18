---
date: 2026-04-27
coverage: canonical
peers:
  - ../meta/baseline-glossary.md
  - ../meta/the-modern-baseline.md
  - ../meta/decision-tree.md
  - ../feature-detection/ponyfill-pattern.md
  - ../feature-detection/prollyfill-pattern.md
  - ../landscape-shifts/polyfill-io-attack.md
  - ../anti-patterns/corejs-entry-modern.md
  - ../transpilation/babel-preset-env.md
primary_sources:
  - https://developer.mozilla.org/en-US/docs/Glossary/Polyfill — MDN canonical "polyfill" definition
  - https://ponyfoo.com/articles/polyfills-or-ponyfills — Sindre Sorhus's coinage essay for "ponyfill"
  - https://github.com/sindresorhus/ponyfill — canonical README defining the pattern
  - https://infrequently.org/2014/08/the-prollyfill-question/ — Alex Russell's 2014 essay; "prollyfill" definition
  - https://web.dev/baseline — canonical Web Platform Baseline definition
  - https://github.com/browserslist/browserslist#readme — browserslist query semantics
  - https://babeljs.io/docs/babel-preset-env — `useBuiltIns` definition
  - https://tc39.es/process-document/ — TC39 stages 0–4 process spec
  - https://developer.mozilla.org/en-US/docs/Web/CSS/@supports — `@supports` syntax
  - https://web.dev/articles/baseline-and-polyfills — modern position on polyfilling vs Baseline
---

# Glossary — terms in the polyfill space

A definition for every term this skill uses, plus the immediately useful corollary (when to use it, where it falls down, what it links to). Every entry assumes the load-bearing baseline: **Chromium 125+ / Safari 17.4+ / Firefox 129+** (April 2024 floor).

## Core feature-shimming terms

### Polyfill

Runtime code that mutates globals or prototypes so that a missing API behaves as if it were native. Term coined by Remy Sharp (2010). MDN's definition is "a piece of code (usually JavaScript) used to provide modern functionality on older browsers that do not natively support it" ([MDN](https://developer.mozilla.org/en-US/docs/Glossary/Polyfill)).

A polyfill, properly defined, satisfies two conditions: (1) it installs the missing feature under the standard name (e.g. `globalThis.fetch`, `Array.prototype.at`); (2) it is a no-op when the feature is already present. The first condition is what makes polyfills dangerous — they defeat tree-shaking, break feature detection, and create global-state coupling.

**When to use:** the feature is in code paths every user hits, ponyfills are infeasible (e.g. it has to be `globalThis.X`), and your support floor includes browsers that lack it.

**See:** `../runtime-polyfills/` for the actual polyfills the modern baseline still needs.

### Ponyfill

A pure-function alternative imported explicitly; never mutates globals or prototypes. Term coined by Sindre Sorhus ([Pony Foo essay](https://ponyfoo.com/articles/polyfills-or-ponyfills)) — the etymology is that a ponyfill is "polyfill, but pony" because it doesn't mutate the global host.

```js
// Polyfill — mutates a global
import 'core-js/actual/array/group-by';
[1, 2, 3].groupBy(x => x % 2); // works, but you mutated Array.prototype globally

// Ponyfill — explicit import
import { groupBy } from 'es-feature-helpers';
groupBy([1, 2, 3], x => x % 2); // no global mutation; tree-shakes
```

**When to use:** any time you can. Tree-shakes, scope-isolates, doesn't conflict with other code's polyfills, doesn't defeat feature detection.

**See:** `../feature-detection/ponyfill-pattern.md`.

### Prollyfill

Speculative implementation of a *pre-spec* feature. Term coined by Alex Russell (2014, ["The Prollyfill Question"](https://infrequently.org/2014/08/the-prollyfill-question/)) — "probably-fill", because the spec might still change. Distinct from a polyfill (which implements a finalized spec) and a ponyfill (which is a delivery model, not a spec-stage signal).

**When to use:** rarely, and never as default behavior. Ship behind a flag; commit to ripping it out when the spec changes.

**Risk:** prollyfills shipped to production become version-locking; the OddBird popover-polyfill is an example of a community shim that started as a prollyfill (when popover was at WICG/draft) and became a polyfill once the API stabilized.

**See:** `../feature-detection/prollyfill-pattern.md`.

### Shim

The umbrella term. Sometimes synonymous with polyfill; sometimes specifically a *workaround for a browser bug* (the feature exists but is broken). The Tailwind v4 `color-mix(in oklab, ...)` swap for Safari < 18 is a shim, not a polyfill — the feature is there, it just renders the wrong hue.

**When to use the word:** when "polyfill" overclaims (the feature exists) or "ponyfill" underclaims (the workaround is global). Use it for bug workarounds, vendor-prefix bridging, and broken-feature replacements.

**See:** `../css-color-bugs/` (every file in this axis is a shim, not a polyfill).

## Build-time terms

### Transpilation

Build-time syntax transformation. Babel, SWC, esbuild, and TypeScript lower modern JS syntax (optional chaining, nullish coalescing, async/await, decorators, the `using` declaration) to older syntax that older runtimes can parse.

**Critical distinction**: transpilation handles *syntax*, not *runtime APIs*. Babel can rewrite `a?.b ?? c` as `a == null ? c : a.b`, but it cannot give you `Array.prototype.at` — for that you need a polyfill (or a ponyfill, or to raise your target).

**When to use:** when your support floor includes browsers that don't parse modern syntax. At our baseline (Chromium 125 / Safari 17.4 / Firefox 129), this is essentially zero — all three parse ES2024 syntax. Transpiling for browsers above the baseline is anti-pattern (`../anti-patterns/target-es5-modern.md`).

**See:** `../transpilation/babel-preset-env.md`, `../transpilation/swc-targets.md`, `../transpilation/esbuild-targets.md`.

### Lowering

Synonym for transpilation. Common in lightningcss / esbuild / swc docs. ("Lowering" is the compiler-theory word; "transpilation" is the build-tooling word.) Lightning CSS calls its `targets` option's behavior "lowering" because it lowers modern CSS (color-mix, nesting, range syntax, logical properties) to older equivalents.

**See:** `../build-tools/lightningcss-features.md`.

### Target lowering

The act of configuring a build tool to emit code compatible with older browsers. The opposite of *target raising* — i.e. setting your build-tool target to a higher floor so the compiler stops shipping legacy code. At the modern baseline, target raising is almost always the right move.

**Anti-pattern:** target lowering by default ("safe" `target: 'es5'`) ships ~30–60 KB of unnecessary helpers and runtime polyfills. See `../anti-patterns/target-es5-modern.md`.

### Spec compatibility vs runtime compatibility

The difference between syntax that *parses* and behavior that's *correct*. A browser may parse `Array.prototype.flat()` but ship a buggy implementation that copies references instead of cloning; that's a runtime-compatibility issue that no polyfill can fix without overriding the prototype.

**When the distinction matters:** debugging "why does this work in Chrome but not Safari?" The first question to ask is which kind of incompatibility — parser-level (transpile) or runtime-level (polyfill / shim).

### Tree-shaking

Dead-code elimination. Build tools (esbuild, Rollup, Webpack 5+, SWC's bundler, Bun) discard exports that no module imports. **Polyfills compromise tree-shaking** because they install side-effect global mutations; the bundler sees `import 'core-js/...'` and must keep the whole thing. Ponyfills do not compromise tree-shaking because they're pure-function imports.

**Why this matters:** the bundle-size case for ponyfills > polyfills is mostly a tree-shaking case.

### Conditional polyfill

Loading a polyfill only when feature detection fails. Common pattern:

```js
if (!('groupBy' in Object)) {
  await import('./group-by-polyfill.js');
}
```

**When to use:** the feature is in non-critical paths and the polyfill is large enough that always-shipping it hurts startup. At our baseline this is mostly historical — the surface area is small.

**Pitfall:** dynamic import adds a network round-trip; if the feature is in the first-paint path, eagerly inline the polyfill instead.

### Differential serving

The module/nomodule pattern: ship two bundles, gate by `<script type="module">` (modern) vs `<script nomodule>` (legacy). At our baseline, every browser supports `type="module"`; differential serving's value is approximately zero, and Vite's `@vitejs/plugin-legacy` documents this — it's only useful if your floor is below ES module support (Safari 10.1, Edge 16).

**See:** `../build-tools/vite-build-target.md`, `../products/vite-6.md`.

## Detection terms

### Feature detection

Runtime/CSS-level check for a feature's presence.

JS:
```js
if ('groupBy' in Object) { ... }
if (typeof structuredClone === 'function') { ... }
if (CSS.supports('color', 'oklch(50% 0.1 0)')) { ... }
```

CSS:
```css
@supports (text-wrap: balance) { ... }
@supports selector(:has(*)) { ... }
@supports (anchor-name: --foo) { ... }
```

**When to use:** always, before you reach for a polyfill. If the feature works, ship native; if not, fall back. See `../feature-detection/at-supports-recipes.md`.

**Pitfalls:** behavioral bugs slip past presence checks. `'fetch' in window` returns true on every browser at our baseline, but iOS Safari `fetch` plus `signal: AbortSignal.timeout()` had a bug in 17.4 that returned a hang instead of an abort — the right detection here is the workaround, not the polyfill.

### `@supports`

CSS feature query at-rule. Three forms:

| Form | What it tests |
|---|---|
| `@supports (property: value)` | Property/value pair is recognized |
| `@supports selector(...)` | Selector is recognized — needs the `selector()` function form |
| `@supports (font-tech(...))` / `@supports (font-format(...))` | Font feature support |

Composable with `not`, `and`, `or`. Nested `@supports` is allowed and shipped at all three baseline browsers since 2022.

**See:** `../feature-detection/at-supports-recipes.md`.

## Configuration terms

### Browserslist

Declarative configuration of browser support targets shared across tools. A single `.browserslistrc` (or `package.json` `"browserslist"` field) drives Babel preset-env, autoprefixer, postcss-preset-env, esbuild, SWC, lightningcss, and Vite simultaneously.

Query examples:
- `last 2 versions` — last two major versions of each browser. **Almost always wrong** because "browser" includes IE, KaiOS browser, etc.
- `defaults` — last 1 major version + > 0.5% global usage + Firefox ESR + not dead. Polyfills 2017-era IE behavior unnecessarily.
- `Chrome >= 125, Firefox >= 129, Safari >= 17.4` — the explicit form for our baseline.
- `baseline widely available` — a Vite v6+ keyword resolving to ['chrome111', 'edge111', 'firefox114', 'safari16.4']. Older than our baseline by ~14 versions; check before adopting.

**See:** `../build-tools/browserslist-recipes.md`, and `meta/baseline-glossary.md` for `defaults` deconstruction.

### Baseline

[Web Platform Baseline](https://web.dev/baseline) — the cross-engine support tier system maintained by the Web Platform DX Community Group. Two states: **Newly Available** (interoperable across all main engines) and **Widely Available** (Newly Available + 30 months elapsed). Annual sets are **Baseline 2024**, **Baseline 2025**, etc., and capture which features became Newly Available within that calendar year.

**When to cite Baseline:** as a shorthand for "all four engines support this." When a feature is Baseline Widely Available, polyfilling it is almost certainly bundle bloat. When it's Newly Available but still inside the 30-month window, decide based on your specific user mix.

**See:** `meta/baseline-glossary.md` for the full reference.

### `useBuiltIns`

Babel preset-env option controlling polyfill injection.

| Value | Behavior |
|---|---|
| `false` (default) | No polyfills injected. Burden on the consumer. |
| `'entry'` | Inject all polyfills referenced via `import 'core-js/stable'` at entry, filtered by browserslist. |
| `'usage'` | Inject only polyfills the AST analyzer can see referenced. Smaller bundle but misses dynamic usage. |

**Modern stance:** `'usage'` for codebases targeting browsers that need polyfills; `false` for modern-only codebases. Never `'entry'` for modern targets — see `../anti-patterns/corejs-entry-modern.md`. ([Babel docs](https://babeljs.io/docs/babel-preset-env))

### Spec compatibility vs runtime compatibility

(Cross-listed: see Build-time terms above.)

## Stage / version terms

### Stage 0 / 1 / 2 / 2.7 / 3 / 4

[TC39 proposal stages](https://tc39.es/process-document/). Maturity ladder for additions to ECMAScript:

| Stage | Name | What it means | Polyfill posture |
|---|---|---|---|
| 0 | Strawman | Idea | Don't ship — even prollyfilling is premature |
| 1 | Proposal | Champion + use cases | Don't ship to production |
| 2 | Draft | Tentative semantics + spec text | Prollyfill candidate behind flag |
| 2.7 | Preview | Editorial polish; tests; "essentially Stage 3" | Prollyfill OK with rip-out plan |
| 3 | Candidate | Spec stable; implementations begin | Polyfill is safe; prep for native |
| 4 | Finished | Ships in next ECMAScript edition | Polyfill at known sunset; remove when targets hit |

**At April 2026:**
- Stage 4 (ES2025+): Iterator helpers, Set methods, Promise.try, Promise.withResolvers, RegExp escape, Float16Array, Error.isError, Array.fromAsync, JSON modules, Explicit Resource Management (`using`), Temporal (Stage 4 March 11, 2026).
- Stage 3: Decorators (`2023-11`), AsyncContext, ArrayBuffer transfer.
- Stage 2.7: ShadowRealm.
- Stage 2: Pipeline operator (no movement 2025), Pattern Matching.

**See:** `../js-language-status/` per-feature files.

### ES2025 / ES2026

Annual ECMAScript editions. ES2025 was finalized June 2025 and includes Iterator helpers, Set methods, Promise.try, Promise.withResolvers, RegExp.escape, Float16Array, JSON modules, Explicit Resource Management (`using`), `Error.isError`. ES2026 includes Temporal (Stage 4 March 11, 2026) and successors of ongoing Stage 3 work.

**Why the year matters:** when a feature is referred to as "ES2025", it's been in the spec for at least one annual cycle and is in three of three engines. Polyfilling ES2025 features at our baseline is mostly historical at this point — Iterator helpers in Safari 17.4–18.3 is the one real candidate.

### Vendor prefix

`-webkit-`, `-moz-`, `-ms-`, `-o-` etc.; experimental-feature naming convention dating to ~2007. Mostly historical at our baseline.

**Live exceptions at this baseline:**
- `-webkit-line-clamp` (CSS Overflow 4 unprefixed shipped in Chrome 125+, Safari 18.5+, Firefox 137+ — old `-webkit-` form still required for Safari < 18.5)
- `-webkit-tap-highlight-color` (no spec equivalent; iOS-specific)
- `-webkit-text-size-adjust` (CSS Text Size Adjustment exists but Firefox/Safari implementation lags)
- `-webkit-overflow-scrolling: touch` (deprecated; remove)
- `-webkit-appearance: none` (now `appearance: none` everywhere; old form harmless)

**Stance:** stop adding prefixes. Autoprefixer with our browserslist emits zero prefixes for modern CSS at this baseline; if it does emit one, that's a signal you've found a live exception worth investigating.

## Voice / posture terms

### Modern-first

The expert-polyfills default stance. Don't polyfill; raise the floor. Burden of proof is on the polyfill, not on going without. Inverts the 2017-era "ship to everyone, polyfill the gap" assumption.

### Self-host

Serve polyfills from your own origin (or a trusted first-party CDN you control). Never `<script src="cdn.polyfill.io/...">`. Not even via Cloudflare or Fastly mirrors — even those load 3rd-party JS, which is a supply-chain risk beyond the polyfill.io domain compromise of June 2024. See `../landscape-shifts/polyfill-io-attack.md`.

## Cross-references

- For the baseline's exact meaning: `the-modern-baseline.md`.
- For Baseline-tier definitions: `baseline-glossary.md`.
- For the do-I-need-a-polyfill flowchart: `decision-tree.md`.
- For per-feature polyfill recommendations: `../runtime-polyfills/`, `../css-polyfills-and-shims/`.
