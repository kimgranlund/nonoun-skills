# Runtime Environment Foundations

## Why This Matters

A skill that assumes Bash execution silently fails in Claude Chat. A skill that assumes only artifact output misses powerful automation in Claude Code. Declaring runtime target is a structural property of the skill — as fundamental as its mode table — because it determines what the skill can promise and under what conditions.

The runtime axis is independent of control mode (D2). A fully autonomous skill can run in Claude Chat (via artifact delivery) and a human-in-the-loop skill can run in Claude Code. Runtime target answers: **what execution environment does this skill require to function correctly?**

---

## Runtime Classification

Every skill declares one of three runtime targets in `skill.json`:

| Target | Value | Meaning |
| --- | --- | --- |
| Claude Code / Cowork | `"agent"` | Requires tool access: Bash, file system, MCP, or subagents |
| Claude Chat | `"chat"` | Works with conversation + artifacts only; no code execution |
| Both | `"both"` | Works in either; chat mode may have reduced output — document the delta |

A skill that does not declare a target is implicitly `"agent"` if it references any tool by name in its Invocation section. Omitting `target` is a validation error.

---

## Claude Code Runtime — Full Tool Inventory

Claude Code is the full agent runtime. The following tools are available.

### File System

**Read** — Read a file at an absolute path.

- Params: `file_path` (required), `offset` (start line), `limit` (line count)
- Also supports: PDFs (`pages` param), images (visual), Jupyter notebooks (cells + output)
- Rule: must Read an existing file before editing it with Edit or Write
- Use: load config, inspect source, read artifacts; prefer over `cat`/`head` in Bash

**Write** — Create or fully overwrite a file.

- Params: `file_path`, `content`
- Rule: must Read existing files first to avoid data loss; prefer Edit for modifications
- Use: create new files, complete rewrites only

**Edit** — Targeted string replacement within a file (requires prior Read).

- Params: `file_path`, `old_string` (must be unique), `new_string`, `replace_all`
- Rule: `old_string` must match exactly including whitespace; re-read if match fails
- Use: surgical edits; always prefer over Write for modifications to existing files

**Glob** — Find files by glob pattern.

- Params: `pattern` (e.g. `**/*.ts`), `path` (directory scope)
- Returns: matching paths sorted by modification time
- Use: discover files before reading; never use `find` via Bash instead

**Grep** — Search file contents with ripgrep.

- Params: `pattern` (regex), `path`, `glob` (file filter), `type`, `output_mode` (`content` / `files_with_matches` / `count`), context (`-A`, `-B`, `-C`), `-i`
- Use: find symbol definitions, locate string patterns; never use shell `grep` instead

### Execution

**Bash** — Execute shell commands.

- Params: `command`, `timeout` (ms, max 600000), `run_in_background` (bool), `description`
- Working directory persists within a session; shell state does not
- Background commands notify on completion via task-notification — do not poll
- Rule: prefer dedicated tools (Read/Edit/Grep/Glob) over shell equivalents; never use `find`/`grep`/`cat`/`head`/`tail` when a dedicated tool exists
- Use: run tests, install packages, git commands, compile, run servers, anything not covered by a dedicated tool

### Web

**WebFetch** — Fetch a URL and return its content.

- Returns: page text (HTML stripped) or raw content
- Rule: never guess or invent URLs; only use URLs from user messages or known docs

**WebSearch** — Search the web and return results.

- Use: research questions, find current information, locate documentation

### Agent Orchestration

**Agent** — Spawn a subagent for complex, multi-step, or parallel work.

- Params: `description` (3–5 words), `prompt` (self-contained brief), `subagent_type` (claude / Explore / general-purpose / Plan), `run_in_background` (bool), `name` (addressable via SendMessage), `isolation` ("worktree" for parallel file mutations — expensive, use sparingly)
- Rule: foreground blocks; background notifies on completion — do not poll
- Use: open-ended research; tasks protecting main context; parallelizable independent work

**Workflow** — Run a deterministic JS orchestration script (fan-out/parallel/pipeline).

- Params: `script` (inline JS), `scriptPath` (pre-written file), `args`, `resumeFromRunId`
- Primitives: `agent(prompt, opts)`, `parallel(thunks)`, `pipeline(items, ...stages)`, `phase(title)`, `log(msg)`, `workflow(name, args)`
- Rule: requires explicit user opt-in ("workflow" keyword or explicit request); not for tasks an Agent call handles; default to `pipeline()` over `parallel()`
- Use: multi-agent fan-out; large migrations or audits; structured parallel research

**SendMessage** — Continue a named or ID'd background agent.

- Params: `to` (agent name or ID)
- Use: resume a background agent with follow-up instructions

**Monitor** — Stream stdout events from a background process.

- Use: watch a running server or test suite; pair with `until` loops

### Task Management

**TaskCreate** — Create a task to track in-conversation work items. **TaskUpdate** — Update task status (`in_progress` → `completed`). **TaskGet / TaskList** — Read current task state. **TaskOutput** — Write structured output to a task. **TaskStop** — Stop a running task.

- Use: break non-trivial implementation into tracked steps; mark done immediately on completion; never batch completions

### Planning

**EnterPlanMode / ExitPlanMode** — Switch to plan-approval mode: edits require user sign-off before executing.

- Use: before significant multi-file changes; when user asks to "plan first"

### Scheduling

**ScheduleWakeup** — Re-invoke the agent after a delay (used in /loop dynamic mode).

- Params: `delaySeconds` (60–3600), `reason`, `prompt`
- Use: self-paced loops; waiting for external state to change

### Skills

**Skill** — Invoke a registered skill by name.

- Params: `skill` (exact name from available-skills list), `args`
- Rule: only invoke skills listed in system-reminder; never guess skill names

### Jupyter

**NotebookEdit** — Edit cells in a Jupyter notebook (.ipynb).

- Use: data science workflows; notebook-based documentation

### Tool Discovery

**ToolSearch** — Load schema for a deferred MCP tool so it can be called.

- Params: `query` ("select:ToolName" for direct lookup, or keywords)
- Rule: MCP tools appear by name only until fetched; calling without schema fails with InputValidationError — always ToolSearch before invoking an unfamiliar MCP tool

### MCP Tools (User-Configured)

MCP (Model Context Protocol) tools extend Claude Code via user configuration. Common categories and capabilities:

| Category | Examples | Capability |
| --- | --- | --- |
| Browser | Playwright MCP (`npx '@playwright/mcp@latest'`) | Headless browser: navigate, screenshot, PDF (`browser_pdf_save`) |
| PDF export | html2pdf MCP (`npx -y html2pdf-mcp`) | HTML → PDF via headless Chrome; `convert_html_to_pdf` tool |
| File system | MCP filesystem server | Extended file ops beyond working directory |
| Version control | GitHub MCP | PR creation, issue management, review comments |
| Databases | SQLite MCP, Postgres MCP | Query execution, schema inspection |
| Communication | Slack MCP | Message sending, channel reads |
| Search | Brave Search MCP, Exa MCP | Structured web search results |
| Brand/content | Domain-specific MCPs | Custom data access (e.g. brand tokens, CMS) |

Skills referencing MCP tools must: (1) name the specific MCP tool, (2) document the install command, (3) document fallback behavior when the tool is absent, (4) declare `"target": "agent"` in skill.json.

---

## Claude Chat Runtime — Full Capability Inventory

Claude Chat is the conversation + artifact runtime. No code execution, no file system writes, no subagents.

### Conversation

- Multi-turn dialogue with full conversation history
- Markdown rendering (headers, tables, code blocks, bold/italic)
- Code blocks with syntax highlighting — displayed only, not executed
- LaTeX math rendering

### File Uploads (User → Claude)

Users upload files that Claude reads as context:

| Type | Formats | Notes |
| --- | --- | --- |
| Documents | PDF, DOCX, TXT, MD | Full text extraction |
| Data | CSV, JSON, XLSX | Claude reads as structured data |
| Images | PNG, JPG, GIF, WEBP | Vision-capable; Claude describes and analyzes |
| Code | Any text file | Read as source code |
| Audio | MP3, WAV, M4A | Transcription-capable |

Constraint: uploads are read-only input. Claude cannot write files back to the user's file system.

### Artifacts (Claude → User)

Claude generates downloadable or renderable artifacts:

| Type | Description | Use cases |
| --- | --- | --- |
| HTML | Self-contained HTML + CSS + JS | Invoices, reports, interactive tools |
| SVG | Scalable vector graphics | Diagrams, icons, charts |
| React | JSX component rendered in sandbox | Interactive UIs, data visualizations |
| Code | Any language, syntax-highlighted | Scripts, configs, implementations |
| Markdown | Rendered document | Reports, specs, documentation |

**HTML artifact sandbox constraints:**

- Runs in a sandboxed iframe
- CDN whitelist: `cdnjs.cloudflare.com` is reliably allowed; jsDelivr, unpkg, Google Fonts may be blocked by Anthropic's CSP
- No `localStorage`, `sessionStorage`, `eval()`, `window.open()`, cookies
- `window.print()` reliability is limited in-sandbox — prefer Blob URL download: `pdfMake.download('file.pdf')` or `<a href="blob:..." download>`
- External fonts (Google Fonts, Adobe Fonts) may be blocked; prefer system fonts or base64-embedded font data within the artifact

### Web Access (When Available)

- **WebSearch**: available if Anthropic enables it for the session — not guaranteed
- **WebFetch**: available if Anthropic enables it for the session — not guaranteed
- Skills must not hard-require either; mark as `[review]` not `[gate]` in §SelfAudit

### Project Knowledge (Claude.ai Projects)

Files added to a Claude.ai Project appear in every conversation's context automatically:

- Always-available without re-uploading: registry files, reference docs, style guides
- Read-only from Claude's perspective; user manually updates files in the Project
- Use for: accounting-registry.json, client data, brand guidelines, config JSON
- Maximum file size and count limits apply (subject to Anthropic's Project limits)

### Custom Instructions

System-level guidance injected into every conversation in a Project:

- Use for: default behaviors, persona, output format preferences
- Store API tokens as Project variables (referenced by name, not pasted in chat)

### MCP Tools in Claude Chat (Limited)

Claude.ai supports MCP integrations configured per-account via the Integrations panel:

- Availability varies by account and tool — not guaranteed
- Tools requiring OAuth need interactive authentication on first use
- Browser-based MCP tools may be absent in headless/non-interactive contexts
- Skills targeting `"both"` must degrade gracefully when MCP is absent in Chat

### What Claude Chat Cannot Do

| Capability | Available | Notes |
| --- | --- | --- |
| Execute code (Python, JS, shell) | No | Artifacts display code; they don't run it |
| Write to user's file system | No | Artifacts are downloads; no direct writes |
| Run Bash commands | No | Claude Code only |
| Playwright/Puppeteer native | No | Possible via MCP if user has configured it |
| Spawn subagents | No | Claude Code only |
| Run Workflow scripts | No | Claude Code only |
| Access local fonts / local files | No | Only uploaded files or Project Knowledge |
| Persist state between conversations | No | Project Knowledge is the persistence mechanism |
| Guaranteed web access | No | WebFetch/WebSearch are session-dependent |

---

## Declaring Runtime Target in skill.json

Add a `target` field to every skill's `skill.json`:

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "target": "agent",
  ...
}
```

| Value | Requirements |
| --- | --- |
| `"agent"` | Uses any of: Bash, Write, Edit, Glob, Grep (file system), Agent, Workflow, MCP tools |
| `"chat"` | Uses only: conversation text, artifacts, file uploads, web access (optional) |
| `"both"` | Works in both; §SelfAudit must document the chat degradation explicitly |

Omitting `target` is a validation error — `check-skill-metadata.py` will flag it.

---

## Design Patterns by Runtime

### Agent-Only Patterns

- **Script generation + execution**: Write a Python/JS file, then Bash-execute it
- **Multi-file transformation**: Glob → Read → Edit across N files in one pass
- **Cached data pipeline**: fetch via API → cache JSON to disk → transform → render HTML
- **Subagent fan-out**: parallel Agent calls for independent research or generation tasks
- **MCP-powered output**: html2pdf MCP for PDF generation; Playwright MCP for screenshots

### Chat-Only Patterns

- **Upload → process → artifact**: User uploads CSV → Claude parses → emits HTML artifact
- **Project Knowledge as registry**: User maintains a JSON file in Project; Claude reads and updates it, outputting the new JSON block for the user to paste back
- **CDN-loaded in-artifact tooling**: pdfmake via cdnjs for in-browser PDF download button
- **Conversation-driven CRUD**: "add client X" → Claude outputs updated JSON → user pastes back into Project Knowledge

### Both-Target Patterns

- **Mode-split via §SelfAudit**: document two code paths; agent path uses Bash/MCP; chat path uses artifacts + Project Knowledge
- **Graceful degradation**: agent mode generates PDF directly; chat mode generates HTML with a "Save as PDF" button for Chrome print; same invoice layout, different delivery
- **Shared template, different delivery**: same HTML template; Playwright for agent PDF; `window.print()` for chat PDF; base64 fonts in both (no CDN required)

---

## §SelfAudit Gates for Runtime

Include these in §SelfAudit based on the skill's declared target:

**For `"agent"` skills:**

- [ ] `skill.json` declares `"target": "agent"` `[gate]`
- [ ] All tool references in Invocation name specific tools (Bash, Read, Write, etc.) `[gate]`
- [ ] Any MCP tools list their install command and fallback behavior `[gate]`

**For `"chat"` skills:**

- [ ] `skill.json` declares `"target": "chat"` `[gate]`
- [ ] No Bash, Write, Edit, Glob, Grep, Agent, Workflow, or MCP tool calls anywhere in skill instructions `[gate]`
- [ ] All output delivered via artifacts or conversation text `[gate]`
- [ ] Any CDN dependency names the specific URL (e.g. `cdnjs.cloudflare.com/...`) `[gate]`

**For `"both"` skills:**

- [ ] `skill.json` declares `"target": "both"` `[gate]`
- [ ] §SelfAudit explicitly documents chat degradation: what outputs are missing or reduced vs. agent mode `[review]`
- [ ] Chat code path verified to use no agent-only tools `[gate]`
