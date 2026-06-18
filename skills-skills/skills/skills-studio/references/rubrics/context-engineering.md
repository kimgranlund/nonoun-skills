---
date: 2026-05-23
status: draft
version: "0.1.0"
---

# Context Engineering — Best Practices Rubric

**Context is not a prompt. Context is an architecture.**

Context engineering is the discipline of designing and managing the complete information ecosystem that an LLM accesses during operation: system prompts, tool definitions, documentation, conversation history, memory systems, retrieval, and dynamic state. It is distinct from prompt engineering (which focuses on wording) and distinct from model selection (which focuses on capabilities).

The insight that separates practitioners from experimenters: **the challenge is not the prompt wording — it's thoughtfully curating all the information that enters the model's limited attention budget at each step.** The minimum effective dose of information beats exhaustive context. (Anthropic, "Context Engineering Explained")

65% of enterprise AI agent failures trace to **context drift** — stale, incomplete, or wrongly-ordered information in the context window. This rubric provides the scoring framework for context quality.

**Companion docs:**

- `harness-design.md` (this folder) — harness as the persistent context layer
- `skills-authoring.md` (this folder) — skills as on-demand context modules

---

## §The Problem

A model's attention is finite. On every turn, it reads everything in context — system prompt, conversation history, tool definitions, loaded documents — and allocates attention proportionally. Content that's irrelevant, stale, or duplicated consumes attention that could have been on the task. Context engineering is the practice of treating that attention budget as a precious resource.

The specific failures:

1. **Context stuffing**: loading "everything that might be relevant" because context windows are large. Large ≠ free. Every irrelevant token competes with relevant ones.
2. **Stale context**: conversation history that was useful 20 turns ago but is now misleading. The agent's working model of the problem becomes corrupted over time.
3. **Dead context**: documentation loaded at session start that was never relevant. Still consumes tokens on every turn.
4. **Context duplication**: same fact stated in the system prompt, in the tool description, and in the skill documentation. Three claims with the same content; model-level confidence is actually reduced when claims are inconsistently worded.
5. **Missing verification context**: agent can't verify its output because the real-product state isn't in context. It falls back to internal consistency checks.

---

## §First Principles

### 1. Context is a precision instrument, not a dumping ground

The minimum effective dose of information beats exhaustive context. Ask, for every piece of information: "does the model need this in the next 5 turns?" If not, exclude or defer it. The test is not "is this true?" or "could this be relevant?" — it's "is this needed now?"

### 2. Structure enables routing; prose enables drift

Structured context (JSON, YAML, typed frontmatter, tables) is easier for models to route — they can find the relevant section without reading everything. Prose is necessary for nuanced reasoning but should not be the primary organizational format for reference material. The harness should be structured; the reasoning should be prose.

### 3. Caching rewards stability; freshness requires freshness

Anthropic's prompt caching: static content (system prompt, tool definitions, CLAUDE.md, documentation) should be in the cacheable prefix — reads at 90% discount on subsequent turns. Dynamic content (current task state, error output, fresh user input) should be in the volatile suffix. If you're paying full price for content that hasn't changed, your context architecture is costing you 10x what it should.

### 4. Memory has three layers: in-context, session, persistent

- **In-context memory**: the current conversation window. Fast, expensive at scale, auto-purged.
- **Session memory**: external store, retrieved per-turn when relevant. Enables long-running tasks without re-loading everything on every turn.
- **Persistent memory**: cross-session corrections, learned rules, agent-scope facts. Encoded as documentation (CLAUDE.md, skill references), not as a vector store.

Each layer has a different cost structure and a different freshness guarantee. Using the wrong layer for the wrong data produces either unnecessary token cost or unacceptable staleness.

### 5. Retrieval sharpens context; ranking is the hard part

For large codebases, embedding-based retrieval is the right architecture — you can't load 500 files in context. But retrieval quality depends almost entirely on the ranking function, not the embedding model. Ranked by relevance to the current task, the top-5 retrieved files are usually correct. Ranked alphabetically or by recency, the top-5 are nearly random.

### 6. Context rot is a maintenance discipline, not a one-time design

A perfectly designed context at project start will be outdated within months. File paths change, APIs change, rules evolve. Context that was accurate at authoring time becomes misleading drift over time. The discipline is not "design great context once" — it's "audit and prune context on a cadence."

---

## §The Rubric

### Dimension 1 [review] — Context load architecture

Is the loading architecture layered (stable → dynamic) or monolithic (load everything)?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | 4-layer architecture: (1) cached system prompt + tool definitions; (2) cached CLAUDE.md + project rules; (3) cached conversation summary; (4) fresh current request + error output. Cache hits on layers 1-3 on every turn. Layer 4 is small (< 2k tokens). |
| **4 — Good** | Stable and dynamic content separated. Cache used for stable content. Some layer bleeding (e.g., large task context loaded upfront that could be deferred). |
| **3 — Adequate** | Caching used but not architecturally designed. Stable content mostly cached; some volatile content accidentally included in the cache prefix. |
| **2 — Poor** | No caching. Everything loaded fresh on every turn. Token cost grows linearly with conversation length. |
| **1 — Failing** | Monolithic prompt loaded at session start containing everything: docs, rules, examples, full codebase snippets. Massive cold-start cost; no refresh on dynamic state. |

**Test**: measure the token cost of the system prompt + tool definitions. Multiply by number of turns. If this number is significant, is it being cached?

---

### Dimension 2 [review] — Relevance discipline (minimum effective dose)

Is every piece of context earning its keep, or is the window a general-purpose knowledge dump?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | For each loaded document, there is a stated reason it's needed for the current session. Skills load references on-demand via the routing table in SKILL.md. No documentation pre-loaded that isn't referenced in the first 3 turns. |
| **4 — Good** | Most loaded content is relevant. A few documents loaded "just in case" but they're small and don't crowd out relevant content. |
| **3 — Adequate** | A significant portion of loaded context is never accessed in a typical session. Not harmful per se, but represents wasted budget. |
| **2 — Poor** | Large documents loaded at cold-start "for completeness." Context window consumed before the relevant task begins. |
| **1 — Failing** | Entire codebase or documentation set loaded on every session. Model receives thousands of irrelevant tokens before reading the task. |

**Test**: audit one full session. For each document loaded, count turns on which it was referenced. Docs with reference count = 0 are dead context. Dead context > 20% of total loaded context is a structural problem.

---

### Dimension 3 [review] — Freshness and drift prevention

Is context kept current, or does it gradually diverge from reality?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Dynamic state (error output, file content) refreshed on every relevant turn. Static documentation audited on a schedule (quarterly minimum). Stale documents flagged before loading (via `last_validated:` frontmatter or equivalent). No document in context contradicts current codebase state. |
| **4 — Good** | Dynamic state refreshed frequently. Static docs audited when the related substrate changes. Some stale docs present but easily identified. |
| **3 — Adequate** | Dynamic state refreshed on session start but not mid-session. Some docs known to be outdated but still loaded because "they're mostly right." |
| **2 — Poor** | Context loaded once, not refreshed during long sessions. Agents discover mid-task that a file path or API has changed. |
| **1 — Failing** | Context was accurate when written. Has never been audited for staleness. Some rules reference deleted files or changed APIs. |

**Test**: pick 5 specific claims in the loaded context. Verify each against current codebase state. If > 1 is inaccurate, the freshness discipline is broken.

---

### Dimension 4 [review] — History management (conversation window hygiene)

As conversations grow long, does the history help or hurt?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Conversation history summarized at checkpoints (e.g., every 20 turns). Summary preserves decisions and constraints; discards failed attempts and irrelevant detours. Fresh context injected at turn N doesn't re-argue decisions made at turn 5. |
| **4 — Good** | History managed via model-native compression (e.g., "compact context" feature). Some loss of nuance but correctness preserved. |
| **3 — Adequate** | History not explicitly managed but the session is short enough (< 20 turns) that the raw history still fits. Problematic for longer sessions. |
| **2 — Poor** | Long histories accumulate without management. Model spends tokens re-reading irrelevant early context on every turn. |
| **1 — Failing** | History includes failed attempts, abandoned approaches, and contradicted plans, all treated with equal weight as current state. |

**Test**: check a session with 30+ turns. Does the model in turn 30 behave consistently with decisions made in turn 5? If it re-opens closed decisions or "forgets" established constraints, history management is inadequate.

---

### Dimension 5 [review] — Memory architecture (cross-session learning)

Can the system build on prior sessions, or does every session start from zero?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Three-layer architecture in use: in-context (current session), session store (external, retrieved per-turn), persistent (CLAUDE.md / agent memory). Corrections from prior sessions visible at cold-start. Agents don't repeat errors from 3 sessions ago. |
| **4 — Good** | Persistent memory via CLAUDE.md or equivalent. Corrections captured and available at cold-start. No session store — some mid-session state lost between sessions. |
| **3 — Adequate** | CLAUDE.md updated inconsistently. Some corrections persist; others are lost. Same error may recur 1-2 sessions after correction. |
| **2 — Poor** | No persistent memory. Each session reinvents everything. Operator corrects same errors repeatedly. |
| **1 — Failing** | Session context discarded completely. Not only are corrections lost — the agent doesn't even remember the project conventions from last week. |

**Test**: create a correction to the agent's behavior in session 1. Run session 2 with a fresh context. Does the correction hold? If not, the persistent memory architecture is broken.

---

### Dimension 6 [review] — Verification context (real-product state in window)

Does the context contain what the agent needs to verify its output against reality?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | After execution, the verify-target's real state is fetched and injected into context: `curl` output, browser DOM, test results, error logs. Agent verifies against real data, not predictions. |
| **4 — Good** | Real-product state fetched for high-stakes verification (releases, deploys). Internal verification (test pass) accepted for lower-stakes changes. |
| **3 — Adequate** | Agent runs tests and reports pass/fail. Real product state not explicitly injected. Agent may declare done before production reflects the change. |
| **2 — Poor** | Verification context is the agent's own prediction ("I believe this change will work because..."). No external data. |
| **1 — Failing** | No verification context at all. Agent declares done when code is written, not when it works. |

**Test**: for the last successful task, what did the agent's context contain when it declared "done"? Was it the real product state, or an internal prediction?

---

## §Anti-patterns

### AP-01 — Context stuffing ("in case" loading)

**Symptom**: Cold-start context is 50k+ tokens because "the agent might need this later." **Root cause**: Treating large context windows as free storage rather than a precision budget. **Correction**: For every document in the cold-start context: is it needed in the first 3 turns? If not, defer to on-demand loading. A 5k-token cold-start with the right information beats a 50k-token cold-start with the right information buried in noise.

### AP-02 — Stale context rot

**Symptom**: Agent consistently makes mistakes about file paths, API signatures, or tool names — all of which changed 3 months ago but weren't updated in CLAUDE.md. **Root cause**: Context designed once, never audited. **Correction**: Quarterly context audit. Treat every claim in static context as a test: "is this still true?" If not, update or remove. Broken claims are worse than missing claims.

### AP-03 — Cache-unaware architecture

**Symptom**: 10,000-token system prompt loaded fresh on every turn of a 50-turn conversation. Total token cost: 500,000 tokens. Cache-aware architecture: 5,000 cached tokens at 90% discount = 50,000 equivalent. The difference is 10x cost. **Root cause**: Context architecture designed without considering Anthropic's caching system. **Correction**: Structure context as stable prefix (system prompt + CLAUDE.md + tool definitions, cached) + volatile suffix (current task + error output, fresh). Separate these deliberately.

### AP-04 — Conversation graveyard

**Symptom**: After 40 turns, the agent references a "decision" from turn 8 that was actually superseded by turns 12-15. The context contains the superseded decision alongside its correction at equal weight. **Root cause**: Conversation history accumulated without summarization or pruning. **Correction**: Checkpoint and summarize at regular intervals. The summary preserves: current task state, active decisions, known constraints, recent errors. It discards: abandoned approaches, superseded decisions, irrelevant detours.

### AP-05 — Single-layer memory

**Symptom**: All memory in one CLAUDE.md file. Small projects: fine. 200+ rules from 12 months of operation: the file is 5000 lines and the agent reads all of it on every cold-start. **Root cause**: Never graduated from Boris's "single CLAUDE.md" pattern to a structured memory architecture, even as the project scale demanded it. **Correction**: Per BORIS-feedback §B2: ticket → memory entry → hard rule. Only the highest-trust, most universal corrections earn a position in AGENTS.md (the cold-start harness). Everything else lives in skill references or per-agent memory files.

### AP-06 — Missing retrieval ranking

**Symptom**: Retrieval-augmented context fetches documents by recency, not relevance. The agent consistently receives documentation about unrelated features because they were recently modified. **Root cause**: RAG implemented as semantic search without relevance ranking relative to the current task. **Correction**: Rank retrieved results by relevance to the current task description, not by recency or popularity. Filtered embeddings (task-type filtered before ranking) outperform unfiltered on all precision metrics.

---

## §Hard Tests

1. **The minimum-dose test**: what is the smallest context that would allow the agent to complete the most common task? Compare to what is actually loaded. The ratio tells you the overhead factor. A ratio > 3x warrants a context audit.

2. **The cache-audit test**: estimate the token cost of content loaded on every turn (system prompt + stable docs). Is it being cached? If not, estimate the monthly overpayment.

3. **The drift test**: pick 5 specific factual claims from CLAUDE.md or loaded documentation. Verify each against current codebase state. ≥ 2 inaccuracies means context rot is active.

4. **The session-memory test**: identify a correction made in session N. Start session N+5 fresh. Does the correction hold? If not, what would need to be true for it to hold?

5. **The conversation-hygiene test**: review a 30+ turn session. Does the agent's behavior in the last 10 turns correctly reflect decisions made and superseded throughout the conversation? Or does it re-open resolved questions?

6. **The verify-context test**: what is the last piece of information the agent reads before declaring a task done? Is it evidence from the real product, or an internal self-check?

7. **The Karpathy test**: if you hired a very smart intern for one day and gave them only the context your agent receives at session start — would they be productive, or confused? If confused, the context is underspecified. If overwhelmed, it's overspecified.
