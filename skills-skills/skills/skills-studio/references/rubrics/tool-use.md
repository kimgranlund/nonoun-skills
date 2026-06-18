---
date: 2026-05-23
status: draft
version: "0.1.0"
---

# Tool Use — Best Practices Rubric

**A tool is a contract between an agent and the world.** The contract has four terms: (1) what inputs are valid, (2) what the tool will do with them, (3) what success looks like, and (4) what failure looks like. A tool that omits any of these terms will be hallucinated, misused, or silently fail in production.

Tool hallucination is one of the highest-impact failure modes in production agentic systems. Spectral Guardrails research (2025): hallucinated tool calls occur when (a) the tool description is too broad, (b) the input schema lacks validation, or (c) the agent infers tool existence from context rather than reading an explicit tool list. All three are design problems, not model problems.

**Companion docs:**

- `agentic-coding.md` (this folder) — PEV loop that verification tool use enables
- `context-engineering.md` (this folder) — token budget for tool definitions
- `harness-design.md` (this folder) — where tool definitions live in the harness

---

## §The Problem

Tools are the agent's interface to the external world. Unlike generating text, tool calls have real side effects: files are deleted, APIs are called, code is deployed, money is spent. The failure modes are correspondingly higher-stakes:

1. **Tool hallucination**: the agent invokes a tool that doesn't exist, or with arguments it has never seen validated.
2. **Silent failure**: the tool exits 0 but produces unexpected output that the agent misinterprets as success.
3. **Scope creep**: a tool named "modify database" gets invoked for reads because nothing prevents it. The write side effect is unintended.
4. **Overly broad tools**: one `run_command(shell_command)` tool replaces 20 specific tools. The agent will run it for anything; there's no contract defining what "anything" means.
5. **Missing error types**: tool returns "operation failed" without context. The agent tries the same call again, and again, until the budget runs out.

---

## §First Principles

### 1. Single responsibility — one tool does one thing

A tool named `interact_with_database` is a footgun. Does it read? Write? Execute DDL? The agent will infer the answer from context, and context is often wrong. A tool named `execute_read_only_query(sql)` has no ambiguity: it reads, it takes SQL, it doesn't write.

Single responsibility also enables the harness to disable tools selectively. A task that only requires reads doesn't need write tools in the context. Fewer active tools = fewer hallucinated calls to wrong tools.

### 2. Explicit input schemas with constraints

Per MCP design patterns (Klavis AI 2025): define required and optional parameters with constraints. `branch_name: { type: string, pattern: "^[a-z0-9-]+$" }` is not over-engineering — it prevents agents from creating branches with spaces or slashes that break git. Validation at the tool layer is cheaper than debugging downstream.

The schema is also part of the routing signal: an agent that reads `branch_name: pattern ^[a-z0-9-]+$` understands what a valid branch name looks like. It doesn't need the harness to repeat this.

### 3. Deterministic, structured output (JSON over prose)

A tool that returns `"Completed successfully."` tells the agent nothing verifiable. A tool that returns `{ "status": "success", "branch": "feat/auth-v2", "sha": "abc123" }` gives the agent actionable data it can pass to the next tool or use to verify state.

CLI tools are attractive (familiar, easy to wrap) but their output formats change across versions and contexts (colored vs. plain, verbose vs. terse). If a CLI tool is load-bearing, wrap it in an API layer that normalizes output and validates responses.

### 4. Explicit error types with actionable messages

A tool that returns `{ "error": "operation failed" }` is worse than a tool that raises an exception — at least an exception creates an obvious signal. A well-designed error response: `{ "error": "branch_already_exists", "branch": "feat/auth-v2", "suggestion": "delete or rename the existing branch before creating a new one" }`

Error type + context + suggestion. The agent can read this and choose the right recovery path without improvising.

### 5. Dry-run modes for irreversible operations

Any tool with destructive, irreversible, or expensive operations should support a `--dry-run` or `preview` mode that shows exactly what would happen without executing. This is not defensive programming — it is what makes verification possible before commitment. An agent that can dry-run before executing can verify intent without risk.

### 6. Bounded tool sets (disable what isn't needed)

Unused tools still consume context tokens and increase hallucination risk. An agent doing a read-only audit doesn't need write tools. The harness should configure the minimal tool set for each mode. This is not premature optimization — it is the difference between a tool ecosystem with 30 candidates and one with 6, which measurably reduces hallucinated calls.

---

## §The Rubric

### Dimension 1 [review] — Precision of tool descriptions

Does every tool's description give the agent a complete, unambiguous contract?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every tool: (a) explicit WHAT (one sentence), (b) parameter descriptions with constraints and examples, (c) output format documented (schema or example), (d) error cases documented, (e) NOT-use cases for tools with overlapping siblings. Agent selects the correct tool for the task on the first try. |
| **4 — Good** | WHAT + parameters documented. Output and errors implied but not explicitly stated. Occasional wrong-tool selection; corrected on second try. |
| **3 — Adequate** | Tool names are self-explanatory. Parameters listed but without constraints. Agent makes reasonable inferences from names. Occasional hallucinated arguments. |
| **2 — Poor** | Tool descriptions are one-liners. Agent has to infer inputs, outputs, and behavior from the name. Hallucination rate elevated. |
| **1 — Failing** | Tool name is the entire description. No parameters documented. Agent makes up arguments. |

**Test**: present an agent with a task. Does it select the right tool without re-reading the tool description multiple times? Does it supply correct arguments on the first call?

---

### Dimension 2 [gate] — Input schema validation

Are invalid inputs caught before the tool executes, not after?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | All parameters have typed schemas with constraints (regex patterns, enum values, ranges, nullability). Invalid inputs return schema validation errors with specific guidance before the tool executes. No execution begins on invalid inputs. |
| **4 — Good** | Most parameters validated. Some unconstrained string parameters. Gross invalid inputs caught; edge cases may slip through. |
| **3 — Adequate** | Types validated (string vs. int) but no constraints. An agent can call `delete_branch("main")` and it won't be blocked at schema level. |
| **2 — Poor** | No schema validation. All inputs accepted. Tool itself may fail internally; error message is tool-internal and opaque to the agent. |
| **1 — Failing** | Tool accepts any input. Errors surface only after execution (often as unhandled exceptions). |

**Test**: call the most destructive tool with an obviously invalid argument (wrong type, malformed string). Does the tool reject it with a clear schema error before executing?

---

### Dimension 3 [gate] — Output determinism and structure

Does the tool return structured, verifiable data — or human-readable prose?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | All tools return JSON with explicit success/failure fields. Errors are typed (`error_type`) with actionable context. Success responses include machine-readable state (IDs, paths, timestamps). Agent can use the output in the next tool call without parsing prose. |
| **4 — Good** | Success responses are structured. Some error responses are prose but include enough context for recovery. |
| **3 — Adequate** | Mix of structured and prose. Structured for known-success; prose for errors. Agent can usually parse errors but occasionally misinterprets them. |
| **2 — Poor** | Most responses are prose. Agent has to parse natural language output to determine success/failure. Ambiguous responses cause retries. |
| **1 — Failing** | Tool output is whatever the underlying CLI produces: colored terminal output, optional whitespace, locale-dependent dates. Agent parses this differently on each platform. |

**Test**: call a tool and examine the output. Can the success/failure status be determined programmatically (without LLM parsing) from the response?

---

### Dimension 4 [review] — Error handling quality

When something goes wrong, does the tool help the agent recover — or leave it guessing?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each distinct failure mode has its own error type (not just `"error"`). Each error includes: the type, the relevant context, and a suggested recovery. Agent can select the right recovery path without human intervention for common errors. |
| **4 — Good** | Error types distinguished. Some errors have recovery suggestions; others just have context. Agent can usually recover from common errors. |
| **3 — Adequate** | One `"error"` type with a message. Message is descriptive enough that the agent can usually understand what went wrong. Recoveries improvised. |
| **2 — Poor** | Error messages are internal (stack traces, exception messages not intended for agents). Agent can't reliably extract useful information. |
| **1 — Failing** | Errors surface as success responses with empty or partial data. Agent doesn't know it failed. |

**Test**: deliberately trigger each distinct error condition in the most-used tool. For each: does the agent receive enough information to choose the correct recovery path?

---

### Dimension 5 [gate] — Blast radius management

Are destructive operations protected against accidental or malicious invocation?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | All destructive operations have: (a) dry-run mode, (b) explicit confirmation requirement in the description ("requires operator confirmation before execution"), (c) scope constraints in input schema (e.g., `cannot target protected branches`). Harness mode-specific tool sets disable write tools during read-only tasks. |
| **4 — Good** | Dry-run mode exists for high-stakes operations. Some confirmation requirements documented. Scope constraints present for the highest-risk operations. |
| **3 — Adequate** | Dry-run mode missing but tool descriptions warn "use with caution." Harness doesn't restrict tool sets by mode. |
| **2 — Poor** | Destructive tools have the same description density as read tools. No dry-run. No confirmation requirement. No scope constraints. |
| **1 — Failing** | Destructive operations identical to non-destructive ones in interface. A `delete_all_branches()` tool looks like a `list_branches()` tool to the agent. |

**Test**: tell an agent it needs to "clean up stale branches" without specifying which ones. Does it (a) call a dry-run first and present results for confirmation, or (b) immediately delete branches?

---

### Dimension 6 [gate] — Hallucination resistance

Does the tool ecosystem minimize the conditions that cause hallucinated tool calls?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Explicit tool manifest in harness (one-line per tool: name, one-line WHAT). Tool set bounded per mode. Tool names are self-explanatory. No broad tools (`run_command`) that admit open-ended interpretation. Hallucination rate measurably low. |
| **4 — Good** | Tool manifest in harness. Some broad tools exist for escape-hatch purposes but are documented as "use only when no specific tool exists." |
| **3 — Adequate** | Tool names are good but no explicit manifest. Agent discovers tools from descriptions only. Some incidental hallucination from over-broad interpretation. |
| **2 — Poor** | Broad tools dominate (e.g., one `bash(command)` tool). Agent interprets the tool as a general-purpose shell. Hallucination rate high. |
| **1 — Failing** | Agent infers tool availability from context, not an explicit tool list. Hallucinated tools occasionally "succeed" (agent claims to have called a non-existent tool). |

**Test**: run 10 diverse tasks. On how many does the agent call a tool it wasn't given? The answer should be 0. Any non-zero rate means the tool ecosystem has hallucination-inviting gaps.

---

## §Anti-patterns

### AP-01 — The god tool (`run_command`, `bash`, `execute`)

**Symptom**: One tool accepts arbitrary shell commands. Agent uses it for everything: reads, writes, deploys, deletes. Scope is unlimited; blast radius is unlimited. **Root cause**: Convenience (one tool does everything) valued over safety (bounded scope). **Correction**: Replace with specific tools. For file reads: `read_file(path)`. For git: `git_status()`, `git_commit(message, files)`. Yes, this is more tools. Each is safer, each is better for routing.

### AP-02 — Prose-output tool

**Symptom**: `run_tests()` returns "12 tests passed, 3 failed: TestAuth, TestLogin, TestSession". Agent has to parse English to extract the failure list. **Root cause**: Wrapping a CLI tool without normalizing output. **Correction**: `{ "total": 15, "passed": 12, "failed": 3, "failed_tests": ["TestAuth", "TestLogin", "TestSession"] }`. The agent reads the JSON; it doesn't parse English.

### AP-03 — Missing error taxonomy

**Symptom**: All errors return `{ "error": "operation failed" }`. Agent can't distinguish "branch doesn't exist" from "permission denied" from "network timeout." It retries all errors identically. **Root cause**: Error handling added as an afterthought. All internal errors mapped to one public type. **Correction**: Enumerate the distinct error conditions the tool can produce. Name each one. The agent selects the recovery path from the error type, not from the message text.

### AP-04 — Validation-free schema

**Symptom**: `create_branch(name: string)` accepts "main", "../escape", "spaces in name". No constraint prevents any of these. **Root cause**: Schema defined for documentation, not enforcement. **Correction**: Add constraints to every parameter that has them: `name: { pattern: "^[a-z0-9-]+$" }`. The tool rejects invalid inputs before execution. The agent learns the constraint from the error.

### AP-05 — Loaded-but-unused tools

**Symptom**: 40 tools loaded on every turn. 80% of invocations use 5 of them. **Root cause**: Convenience: "load everything, the model will figure out which to use." **Correction**: Mode-specific tool sets. A read-only audit mode loads read tools only. A write mode loads write tools. Each reduction in active tools reduces hallucination surface and context cost.

### AP-06 — Destructive-without-dry-run

**Symptom**: `clean_up_branches(older_than_days)` deletes branches without preview. Called with `older_than_days=30` in production; deletes a branch that was 31 days old but not yet merged. **Root cause**: Dry-run treated as optional; added only after an incident. **Correction**: For any tool with irreversible side effects: dry-run is mandatory before release. The dry-run signature is identical to the real call, with an added `preview: true` flag that returns what would happen without executing.

---

## §Hard Tests

1. **The hallucination test**: give an agent 10 tasks covering all the tool space. Count hallucinated calls (tools invented by the agent that don't exist). Should be 0. If > 0, find the gap: is there a missing specific tool that the agent tries to infer from context?

2. **The wrong-tool test**: for tools with overlapping descriptions (e.g., `get_user` vs. `get_user_profile`), does the agent reliably select the correct one? If not, the NOT clauses in the descriptions are missing.

3. **The argument test**: call each tool once with the minimum valid arguments. Does it succeed? Now call each tool with one argument removed. Does it return a schema error or silently proceed with a null default?

4. **The error-recovery test**: trigger each distinct error condition for the most-used tool. For each: can the agent read the error and choose the correct recovery without operator help? Any "I don't know how to recover from this" = the error message is inadequate.

5. **The blast-radius test**: ask the agent to "clean up stale resources." Without specification: does it dry-run first? Does it ask for scope? Or does it immediately delete?

6. **The scope test**: in a read-only task, are write tools active in the context? If yes, the mode-specific tool set is missing.

7. **The Musk test**: for each tool in the ecosystem, ask "why does this tool exist?" If the answer is "because it evolved from a CLI script and nobody redesigned it," that's a tool that should be rebuilt with first principles. Tools that exist because they were convenient to create, not because they serve a clear contract, are the primary source of production tool failures.
