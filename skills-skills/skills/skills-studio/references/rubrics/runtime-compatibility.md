# Runtime Compatibility Rubric

**Purpose:** Assess whether a skill correctly declares its runtime target, implements within that target's constraints, and degrades gracefully when targeting both runtimes.

**Load when:** Evaluating any skill during `score` or `promote` mode. Load alongside `skills-holistic.md` — runtime compatibility is a prerequisite gate; D1–D10 scores are meaningless if the skill targets the wrong runtime.

**Foundation:** `references/foundations/runtime-environment-foundations.md`

**Primary critic:** Simon (trust boundaries — a wrong runtime assumption is an injection surface: a chat skill that silently falls back to executing user-supplied content is a scope escape)

---

## D0 — Runtime Target Declaration `[gate]`

Does `skill.json` include a `target` field with a valid value?

**Allowed values:** `"agent"`, `"chat"`, `"both"`

| Score | Evidence |
| --- | --- |
| 5 | `target` present, valid, consistent with the skill's actual tool usage |
| 3 | `target` present but inconsistent (declares `"chat"` but Bash appears in Invocation) |
| 1 | `target` absent — automatic fail; blocks downstream dimension scores |

**Mechanical check:** `grep '"target"' skill.json` — value must be in the allowed set.

---

## D1 — Tool Usage Consistency `[gate]`

Do all tool references in SKILL.md, §SelfAudit, and reference files match the declared target?

**For `"agent"`:** Any tool is valid. Verify referenced MCP tools name their install command. No false restrictions (an agent skill that avoids Bash for no reason is under- powered).

**For `"chat"`:** No Bash, Write, Edit, Read (file path), Glob, Grep, Agent, Workflow, or MCP tool references anywhere in skill instructions. Allowed: conversation, artifacts, file uploads, WebFetch/WebSearch (marked optional), CDN scripts in artifacts.

**For `"both"`:** Chat code path must be tool-clean; agent code path may use any tool. Both paths must be explicitly documented — "agent mode does X; chat mode does Y."

| Score | Evidence |
| --- | --- |
| 5 | All tool references match the declared target with no exceptions |
| 4 | One minor reference leaks (e.g. a chat skill mentions Bash in a "see also") |
| 3 | A secondary mode uses an out-of-target tool |
| 1 | Primary output mechanism requires an out-of-target tool |

---

## D2 — §SelfAudit Runtime Gates `[gate]`

Does §SelfAudit include the correct runtime gates per the foundation spec (`runtime-environment-foundations.md` §SelfAudit section)?

**For `"agent"`:** MCP tools listed with install commands; tool names are specific, not generic ("run a PDF tool" → fail; "call html2pdf MCP (`npx -y html2pdf-mcp`)" → pass).

**For `"chat"`:** Explicit gate that no agent-only tools are invoked; CDN URLs named specifically (not just "use a CDN library").

**For `"both"`:** Chat degradation documented — what output is missing or reduced vs. agent mode. Must be specific: "PDF export not available in chat; HTML artifact with `window.print()` button provided instead."

| Score | Evidence |
| --- | --- |
| 5 | All required gates present, labeled `[gate]`, and mechanically verifiable |
| 3 | Gates present but labeled `[review]` when they should be `[gate]` |
| 2 | Partial — some gates present, others missing |
| 1 | Runtime gates absent entirely |

---

## D3 — Chat Artifact Quality `[review]`

_Applies to: `"chat"` and `"both"` targets only. N/A for `"agent"`._

If the skill produces artifacts in chat mode: are they self-contained, scoped to the Claude Chat sandbox, and using CDN-safe dependencies?

| Score | Evidence |
| --- | --- |
| 5 | Fully self-contained (inline CSS/JS or `cdnjs.cloudflare.com`); system fonts or base64-embedded fonts; download mechanism works via Blob URL or `window.print()`; no blocked CDNs, no `eval()` |
| 4 | Works but uses jsDelivr or unpkg (blocked by some Claude.ai CSP configs) |
| 3 | Works in Chrome but uses html2pdf.js (raster output — text not selectable) |
| 2 | Artifact requires server-side rendering or code execution outside the sandbox |
| 1 | Artifact does not function at all in Claude Chat |
| N/A | Skill is `"agent"` with no chat artifact path |

---

## D4 — Graceful Degradation `[review]`

_Applies to: `"both"` targets only. N/A for `"agent"` or `"chat"`._

For `"both"` skills: is the chat experience meaningfully useful, not just technically possible?

| Score | Evidence |
| --- | --- |
| 5 | Chat mode delivers the same core value with documented trade-offs clearly stated in SKILL.md (e.g. "PDF requires manual Chrome print; registry requires copy-paste back into Project Knowledge") |
| 4 | Chat mode works but trade-offs are only in §SelfAudit, not surfaced in Quick Start |
| 3 | Chat mode works but key outputs are missing without documentation of the gap |
| 1 | Chat mode is nominally declared but unusable (all meaningful output requires Bash) |
| N/A | Single-target skill — it fails clearly, not degrades |

---

## D5 — MCP Dependency Documentation `[gate]`

_Applies to: `"agent"` skills that use MCP tools. N/A if no MCP tools used._

| Score | Evidence |
| --- | --- |
| 5 | Each MCP tool named with: (1) install command (`npx -y ...` or equivalent), (2) what capability it provides, (3) fallback behavior when absent (skip / warn / hard fail) |
| 3 | MCP tools named but install command absent |
| 2 | MCP tools referenced by capability only ("use a PDF tool") without naming the specific tool |
| 1 | MCP dependency exists but is undocumented — users cannot reproduce the skill's behavior |
| N/A | Skill uses no MCP tools |

---

## Summary

| Dim | Label | Scope | What it checks |
| --- | --- | --- | --- |
| D0 | `[gate]` | All | `target` field present and valid in skill.json |
| D1 | `[gate]` | All | Tool references match declared target |
| D2 | `[gate]` | All | §SelfAudit has correct runtime gates |
| D3 | `[review]` | chat, both | Artifact sandbox safety and CDN correctness |
| D4 | `[review]` | both | Chat degradation is meaningful, not nominal |
| D5 | `[gate]` | agent (MCP) | MCP tools documented with install commands |

**D0 is a hard prerequisite.** Score 1 on D0 blocks all downstream dimension scores — a skill without a declared target cannot be evaluated for runtime correctness.
