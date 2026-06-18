---
date: 2026-04-27
coverage: extended
peers:
  - ../transpilation/babel-preset-env.md
  - ../transpilation/swc-targets.md
  - ../meta/the-modern-baseline.md
  - ../anti-patterns/preset-env-no-browserslist.md
primary_sources:
  - https://github.com/tc39/proposal-pipeline-operator — TC39 proposal-pipeline-operator (Stage 2)
  - https://tc39.es/proposal-pipeline-operator/ — Spec text (Hack-style with topic reference)
  - https://github.com/tc39/proposals — TC39 master proposal list
  - https://blogs.igalia.com/compilers/2025/03/27/summary-of-the-february-2025-tc39-plenary/ — February 2025 plenary summary
  - https://blogs.igalia.com/compilers/2025/05/20/summary-of-the-april-2025-tc39-plenary/ — April 2025 plenary summary
  - https://blogs.igalia.com/compilers/2025/07/03/summary-of-the-may-2025-tc39-plenary/ — May 2025 plenary summary
  - https://babeljs.io/docs/babel-plugin-proposal-pipeline-operator — Babel pipeline-operator plugin
  - https://benlesh.com/posts/tc39-pipeline-proposal-hack-vs-f-sharp/ — Hack vs F# pipe history
---

# Pipeline operator — Stage 2 since 2021, no movement, Babel-only at our baseline

The pipeline operator `|>` is the longest-running Stage 2 proposal that hasn't moved. It has been at Stage 2 since 2021. **No public progression in 2024 or 2025.** It is not coming to engines anytime soon. Do not adopt for production at the modern baseline — this would mean every consumer of your code needs a Babel pipeline aligned to your placeholder choice.

## What the proposal is

The pipeline operator [proposal-pipeline-operator](https://github.com/tc39/proposal-pipeline-operator) introduces a `|>` infix operator that pipes a value into an expression. The "Hack-style" form — the version championing committee currently advances — uses a **topic reference** placeholder so the right-hand side can express any expression position, not just a unary call:

```js
// Hack-style — current proposal
result = value |> double(%) |> square(%) |> toString(%);

// Equivalent without pipeline (today)
result = toString(square(double(value)));
```

The topic-reference token is **`%`** in current spec text but is explicitly not final — the [proposal explainer](https://tc39.es/proposal-pipeline-operator/) notes "the precise token for the topic reference is not final. `%` could instead be `^`, or many other tokens. We plan to bikeshed what actual token to use before advancing to Stage 3."

## TC39 stage history — the slow road

Two competing proposals lived in parallel for years:

| Form | Syntax | Status |
|---|---|---|
| **F#-style** | `value \|> double \|> square` (RHS must be unary callable) | Rejected; not advanced |
| **Hack-style** | `value \|> double(%) \|> square(%)` (RHS uses topic reference) | Current Stage 2 proposal |
| **"Smart" pipelines** | Hybrid; would auto-detect F# vs Hack form | Withdrawn |

The Hack form won at the **August 2021** TC39 plenary, after several years of debate. F# pipes were rejected twice; the consensus reasoning was that Hack accommodates `await`, `yield`, conditional expressions, and arbitrary expression positions, while F# requires curried unary callables that don't fit JavaScript ergonomics.

**Stuck since 2021.** Per the Igalia plenary summaries:

- [February 2025 plenary](https://blogs.igalia.com/compilers/2025/03/27/summary-of-the-february-2025-tc39-plenary/) — pipeline operator not on agenda.
- [April 2025 plenary](https://blogs.igalia.com/compilers/2025/05/20/summary-of-the-april-2025-tc39-plenary/) — pipeline operator not on agenda.
- [May 2025 plenary](https://blogs.igalia.com/compilers/2025/07/03/summary-of-the-may-2025-tc39-plenary/) — pipeline operator not on agenda.

There has been **no movement to Stage 2.7** (the new validation stage introduced in late 2023) or beyond in 2024 or 2025. As of April 2026, the proposal champions have not presented for advancement at any plenary in the 2025 calendar year. Verify against the latest tc39/notes plenary minutes.

Champions: J. S. Choi, James DiGioia, Ron Buckton, Tab Atkins-Bittner. Daniel Ehrenberg is a former champion.

## At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+)

**Not in any engine.** No native shipping in V8, SpiderMonkey, or JavaScriptCore. Not on any roadmap. caniuse does not even track the feature.

| Tool | Support |
|---|---|
| **Babel** | Yes — `@babel/plugin-proposal-pipeline-operator` with `proposal: "hack", topicToken: "%"` |
| **SWC** | Experimental — `jsc.experimental.pipeline_operator` (verify the exact key in current SWC docs; this changes) |
| **esbuild** | No support; would emit syntax error |
| **TypeScript** | No native support; pipeline must be transpiled away before TS sees it |

## Babel-only verdict — why this matters

The Babel-only constraint is load-bearing. If you adopt the pipeline operator:

- **Your build pipeline must include Babel** (or SWC with the experimental flag) for every file that uses `|>`.
- **Library authors who ship pipeline syntax force Babel onto every consumer.** A consumer using Vite + esbuild without a Babel step will fail to build.
- **The placeholder token is unstable.** If you write `%` today and the committee picks `^` before Stage 3, every line of pipeline code in your codebase needs rewriting.
- **The Babel `topicToken` choice is a project-wide commitment.** Two libraries on different `topicToken` settings cannot be combined in the same build.

**Verdict at this baseline: skip until Stage 3 movement happens.** The risk-reward is poor — you take on transpilation overhead, lock-in to a Babel-flavor of the language, and spec instability, in exchange for syntactic sugar that has working alternatives.

## Common idioms — native alternatives

Native function composition handles 90% of pipeline use cases without any transpile cost:

```js
// Native — works today, no transpile
const result = toString(square(double(value)));

// Pipeline — Babel-only, Hack-style with %
const result = value |> double(%) |> square(%) |> toString(%);
```

For longer chains where readability suffers, extract a `pipe` helper:

```js
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);

const result = pipe(double, square, toString)(value);
```

This is type-checkable in TypeScript with appropriate variadic generics, runs in every engine since ES2015, and survives any future spec churn. Most Hack-style pipeline code in the wild can be rewritten as `pipe()` calls with no semantic loss.

For RxJS-style operator chains, the existing `pipe` method on `Observable` and `pipeable` operator pattern is already well-established and predates the operator proposal.

## Why no movement? — implementer signals

Three structural reasons the pipeline operator has stalled:

1. **No engine champion.** Every advanced TC39 proposal needs at least one engine team actively prototyping or signaling intent to ship. None of V8, SpiderMonkey, or JSC has signaled implementation interest for the Hack-style operator. Engine teams have reportedly indicated that pipe-as-syntax is low priority compared to feature work that unblocks new web APIs.
2. **Lack of urgency.** Pipeline syntax is purely ergonomic — it expresses what `pipe()` and method-chaining already express. Unlike `await`, generators, or the `||=` family of assignment operators, it does not unlock anything that wasn't already possible. Stage progression for purely-ergonomic proposals tends to be slower than for proposals that close real expressiveness gaps.
3. **Token instability.** The `%` placeholder is contentious because it conflicts with modulo-operator-flavored visual reading. Bikeshedding over `%`, `^`, `?`, `$`, `_`, and other tokens has consumed most of the 2022-2024 plenary discussion bandwidth on this proposal. No token has reached consensus.

The combination — no engine pressure, low feature urgency, unresolved bikeshed — is why progression is stalled. The proposal could remain at Stage 2 for several more years without advancing or being withdrawn.

## Risks if you adopt anyway

If you ignore the position above and ship pipeline syntax in production code today:

- **Token churn rewrite cost.** Switching `%` → `^` (or whatever the committee picks) means a codebase-wide find-and-replace. This is mechanically tractable but reviewers will hate it.
- **Build pipeline lock-in.** Removing Babel becomes harder — every pipeline expression must be transpiled before any other build step runs. esbuild-only or SWC-only pipelines (the modern fast path) become impossible.
- **Library composition fragility.** Two libraries published with different `topicToken` settings cannot coexist in the same Babel build without the build flagging an error.
- **Spec-shape risk.** If the proposal regresses (gets withdrawn like Records & Tuples, or is reshaped) you own the migration cost.

The pipeline operator is not a Stage 4 feature waiting on the last engine; it is a Stage 2 feature with no clear path to Stage 4. Treat it accordingly.

## Position

**Skip the pipeline operator at this baseline.** Adopt only if (1) Stage 3 has happened and the placeholder token is locked, (2) at least one native engine has shipped or committed publicly, and (3) your build pipeline already requires Babel for other reasons.

Reconsider when:

- Proposal advances to Stage 2.7 with implementation feedback.
- A native engine ships an implementation behind a flag.
- Babel marks the plugin stable (currently `@babel/plugin-proposal-*` — the `proposal-` prefix indicates experimental).

Until any of those happen, the cost of adoption (Babel everywhere, placeholder churn, library compatibility) outweighs the syntactic win.

## Cross-references

- Babel preset-env, where the experimental plugin lives: `../transpilation/babel-preset-env.md`
- SWC experimental flags: `../transpilation/swc-targets.md`
- The modern baseline (why "Babel-only" is a real cost): `../meta/the-modern-baseline.md`
- Anti-pattern: shipping experimental syntax to consumers: `../anti-patterns/preset-env-no-browserslist.md`
