---
name: perf-verifier
description: Reason about and verify perceived latency — the invariants every async surface must satisfy: latency feedback windows, skeleton vs spinner vs optimistic decisions, streaming UX, layout-stability (CLS) budgets, image-dimension reservation, and cancellation. Use when checking or auditing loading UX that feels slow despite acceptable wire latency, when CLS is eroding trust, or when streaming responses need coherent presentation. NOT for text/background contrast, palette, or color-blind safety (color-verifier); NOT for focus order, keyboard nav, hit-targets, or focus rings (focus-verifier); NOT for RTL/bidi, dir/lang on text surfaces, locale Intl formatting, or text-expansion (i18n-verifier); NOT for destructive high-blast actions, undo/type-to-confirm, or audit-trail/audit-event UX (safety-verifier); NOT for color-space theory or palette math (color-science); NOT for back-end wire latency or JS bundle-size profiling; NOT for building a spinner or skeleton-loader component (component-decomposer).
---

# perf-verifier

Reasoning skill that owns the *perceived-latency* layer of ui-dev. Wire latency is measured in ms; perceived latency is measured in trust. This skill names the feedback-obligation windows, the loading-affordance decision tree, the layout-stability budgets, and the streaming-presentation invariants. Upstream: `ui-compose-interaction` (async four-state), `ui-compose-motion` (durations, continuous role), `ui-compose-voice` (loading slot). Downstream: component libraries, `ui-audit-quality`.


## Invocation

This is a **constraint** decomposition skill. The user needs loading or streaming UX invariants. Decompose: (1) identify the async surface, (2) set latency thresholds, (3) choose skeleton vs spinner vs optimistic, (4) define feedback cadence and layout-stability budgets.

### Step 1 — Ingestion

Classify the ask surface:
- "This feels slow" → measure perceived vs wire latency; often wire is fine, presentation is not
- "Which loading pattern?" → skeleton (structured), spinner (unstructured), optimistic (instant)
- "Streaming responses" → markdown streaming, progressive disclosure, partial-render decisions
- "CLS eroding trust" → layout-stability budget; reserve space before data arrives

### Step 2 — Decomposition

| Sub-ask | Threshold | Pattern |
|---|---|---|
| Instant feedback | < 100ms | No loading indicator required |
| Perceived progress | 100–1000ms | Skeleton preferred; spinner acceptable for unstructured |
| Deferred completion | 1000–3000ms | Skeleton + progress bar; cancel button |
| Long operation | > 3000ms | Staged loading; background continuation; notify on completion |
| Optimistic update | Any latency | Instant UI state change with rollback on error |
| Streaming | Progressive | `X-Accel-Buffering: no`; Streamdown or fetch+ReadableStream |
| CLS budget | Core Web Vital | Cumulative Layout Shift < 0.1 across all surfaces |

### Step 3 — Execution routing

Every async surface must carry an `observedLatency` measurement. If wire latency < 200ms but skeleton shows for 800ms, the problem is presentation scheduling, not server speed. Optimistic updates must declare rollback targets in `InteractionSchema`.


## When to use

- Loading UX feels slow despite acceptable server latency — perceived ≠ measured.
- Skeletons and spinners coexist inconsistently; no rule governs which to use.
- Cumulative Layout Shift (CLS) is high — content reflows as data arrives.
- A new feature will stream responses (LLM output, live search, etc.) and needs coherent UX.
- Optimistic UI is being introduced and its boundaries need naming.

## When NOT to use

- Back-end performance tuning — wire latency belongs to engineering, not this skill.
- Bundle-size analysis — that's build-system work.
- Animation performance (jank, composited layers) — partially owned by `ui-compose-motion`.

## Rate-limiting factor

**Perceived latency is a function of feedback obligation, not wall-clock.** The irreducible observation: users tolerate long operations when feedback is continuous and predictable; users distrust short operations that are silent. Every async surface must declare what feedback it owes the user, measured against declared *perception thresholds*, not against raw latency numbers.

## First principles

1. **Perception thresholds are canonical.** `< 100ms` feels instant. `100–300ms` feels responsive. `300ms–1s` needs acknowledgement. `> 1s` needs continuous progress. `> 10s` needs cancellation.
2. **Feedback obligation grows with latency.** Short operations owe a micro-acknowledgement; long operations owe continuous progress + ETA.
3. **Optimistic > spinner for reversible.** When outcome is almost-always-success, optimistic UI beats a spinner on the same path.
4. **Skeletons > spinners for layout-bearing data.** When data will occupy measurable space, a skeleton that reserves that space beats a spinner that reflows.
5. **Spinners > skeletons for unknown-shape responses.** When the result's shape is not predictable, a spinner is honest.
6. **Streaming is progressive rendering.** Stream tokens are committed progressively; no flash between stream completion and final render.
7. **Layout stability is a budget.** CLS target ≤ 0.1 per interaction. Every async insertion reserves space.
8. **Cancellation is first-class.** Operations > 10s expose a cancel affordance.
9. **Stale-while-revalidate is a UX posture**, not just a caching one. Show cached data during revalidation; mark as stale.
10. **Silence > fake progress.** A fake "loading… 50%" bar is worse than no bar.

## Procedure

### Step 1 — Classify the operation

```ts
type AsyncOperation = {
  id: string;
  expectedLatencyP50Ms: number;
  expectedLatencyP95Ms: number;
  outcomeShape: "known" | "streamed" | "unknown";
  idempotent: boolean;
  cancelable: boolean;
  reversible: boolean;
};
```

### Step 2 — Pick the feedback recipe
Use the perception-thresholds table:

| p50 latency | recipe |
|---|---|
| `< 100ms` | no explicit feedback (instant); the state change itself is feedback |
| `100–300ms` | inline micro-feedback: button enters `busy`; content placeholder flickers only if > 300ms |
| `300ms–1s` | skeleton (if layout-bearing) or spinner (if unknown-shape); no blocking dialog |
| `1–3s` | skeleton + subtle continuous animation; show cached data if possible |
| `3–10s` | progress indicator with ETA if knowable; cancel affordance mandatory |
| `> 10s` | progress + ETA + cancel + proactive explanation ("This usually takes ~15s") |

### Step 3 — Decide optimistic vs. non-optimistic
Optimistic UI applies when:

- Outcome is almost-always-success (e.g., toggle a like, rename a thing).
- Reversible on failure (rollback target declared — see `ui-compose-interaction`).
- Idempotent.
- Low blast radius.

Otherwise: non-optimistic (show pending state, commit on confirm).

### Step 4 — Decide skeleton vs. spinner
Skeleton when:

- Layout-bearing: the data will occupy measurable space whose shape is known.
- Multiple items arrive (list, grid).
- Duration is 300ms–3s.

Spinner when:

- Result shape is unknown.
- Single-item replacement.
- Duration is 300ms–1s and no layout to reserve.

Neither when:

- `< 300ms` — let the existing UI show its `busy` state.
- `> 10s` — promote to a real progress indicator with ETA.

### Step 5 — Reserve layout space
For every async insertion that occupies measurable space:

- Reserve the space with a skeleton, aspect-ratio box, or `min-block-size` placeholder.
- Do not use `display: none` → `display: block` for async content.
- Images: declare `width × height` or `aspect-ratio`; use `content-visibility: auto` for long lists.
- Web fonts: declare `size-adjust` / `font-display: swap` + matched metrics; or `font-display: optional` for tight budgets.

### Step 6 — Stream progressively
For streamed responses (LLM outputs, SSE, etc.):

- Render tokens as they arrive; do not buffer to completion.
- Never flash between stream-end and final-rendered state — the streaming view *is* the final view.
- Stabilize layout: stream into a container whose `min-block-size` grows monotonically.
- Respect `prefers-reduced-motion` — no typing-style token animation for users with reduced motion.
- Announce progress via aria-live politely, not per-token (too noisy); chunk to sentence- or paragraph-level for screen readers.

### Step 7 — Handle stale-while-revalidate
When cache returns data:

- Render cached data immediately.
- Start revalidation in parallel.
- Mark UI as `stale` (subtle indicator + stale timestamp, not blocking).
- On revalidation success, update in place with no layout shift.
- On revalidation failure, keep stale data and surface the error non-intrusively.

### Step 8 — Handle cancellation
For operations > 10s:

- Expose a cancel affordance co-located with the progress indicator.
- Cancellation restores prior state (no half-applied changes) when possible.
- Cancellation within the recall window is non-destructive (see `safety-verifier`).

### Step 9 — Emit the PerceivedPerformanceSchema

```ts
type PerceivedPerformanceSchema = {
  operations: AsyncOperation[];
  recipes: Record<OperationId, "instant" | "busy" | "skeleton" | "spinner" | "progress" | "progress+eta+cancel">;
  optimisticOperations: OperationId[];
  cancelableOperations: OperationId[];
  clsBudgetPerInteraction: number;   // default 0.1
  streamingOperations: Array<{ id: string; chunkBy: "token" | "sentence" | "paragraph"; reducedMotionFallback: string }>;
};
```

## Invariants

1. Every async operation declares a recipe from the perception-thresholds table.
2. Optimistic UI is used only when outcome is almost-always-success, idempotent, reversible, and low-blast.
3. Skeletons reserve layout-bearing space; spinners do not reserve space.
4. CLS per interaction ≤ 0.1.
5. Images and media declare dimensions or aspect-ratio.
6. Streaming views render progressively with no flash at stream-end.
7. Operations > 10s expose cancel.
8. Stale data is visually marked, not hidden.
9. Aria-live announcements during streaming are chunked, not per-token.
10. No fake progress (percentages fabricated from time, not real completion).


- **INV-PER-001** — Every proof cites specific schema paths or CSS rules it evaluates (enforcement: convention)
- **INV-PER-002** — Remediation suggestions are scoped to the schema/artifact that can fix them (enforcement: convention)

## Typed Interface

**Domain:** `ui-design`

**Consumes:** Relevant schemas and artifacts.

**Produces:** `PerceivedPerformanceProof` — constraint-satisfaction proof or violation report.

**Invariants:** Evaluations cite schema paths or CSS rules; remediation suggestions scoped to fixable artifact.

**Downstream:** `ui-audit-quality`.

## Anti-patterns this skill refuses

- Spinner on every async call, regardless of duration or layout.
- Skeleton for operations expected to complete in < 200ms — flashes on the viewer.
- Replacing rendered content with a spinner while revalidating — blanks prior data.
- Layout shift when async content arrives — CLS spike.
- Fake "loading bar" that approaches 90% over time, regardless of progress.
- Per-token aria-live announcements — floods assistive tech.
- Blocking dialog "Loading, please wait" for any operation under 3s.
- Optimistic UI without rollback (see state skill) — silent failure on error.
- Streaming responses buffered server-side and rendered in one chunk — defeats streaming.
- Using `font-display: block` which hides text until font arrives (FOIT).
- Long operations without cancellation — user is trapped.

## Handoff

- `ui-compose-interaction` consumes operation classifications and supplies the async four-state machine + optimistic rollback contract.
- `ui-compose-motion` supplies the `continuous` motion role for skeleton shimmer / spinner; enforces reduced-motion fallback.
- `ui-compose-voice` supplies `loading-state` slot copy + proactive explanations for long operations.
- `ui-compose-nav` consumes the 200ms hold rule for route loaders.
- `safety-verifier` shares the recall/cancellation contract for long destructive operations.
- `ui-compose-responsive` supplies container-query scoping for skeletons that match the final layout.
- `ui-audit-quality` runs perf checks: recipe per operation, skeleton/spinner decision, CLS budget, image dimensions, streaming posture, cancel affordance, no-fake-progress.

## Bundled reference files

- `thresholds/perception.json` — canonical latency → recipe table.
- `decisions/skeleton-vs-spinner.json` — decision tree for loading affordance choice.
- `optimistic/eligibility.json` — criteria for when optimistic UI applies.
- `streaming/posture.json` — streaming rendering invariants and aria-live chunking rules.
- `cls/budget.json` — layout-stability budget per interaction and reservation patterns.
- `cancellation/contract.json` — cancel affordance placement + state-restoration rules.
