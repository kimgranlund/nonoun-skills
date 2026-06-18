---
date: 2026-05-24
status: draft
version: "0.1.0"
---

# Mechanization Best Practices — Rubric

**Mechanization is the discipline of removing variance from repeatable agent work.**

A prompt can ask an agent to remember a rule. A harness can tell the agent to follow a process. A skill can describe a procedure. But any step that is repeated, testable, safety-relevant, or silently failure-prone should eventually become a deterministic mechanism: a script, hook, validator, formatter, code generator, CI gate, workflow, policy check, or infrastructure boundary.

The purpose of mechanization is not to create more tools. The purpose is to move the parts of agent work that should not vary out of probabilistic prose and into deterministic execution.

The agent should decide **what needs to happen**. The mechanism should perform or enforce the part that should happen the same way every time.

**Companion docs:**

- `inversion-and-abstraction.md` — why procedures should become tools and where abstraction earns its keep
- `tool-use.md` — how tools should be invoked, scoped, and reported
- `agentic-coding.md` — Plan → Execute → Verify as the execution loop
- `security-and-scope-containment.md` — blast radius, least privilege, dry-run boundaries, and irreversible-action gates
- `evaluation-workflows.md` — how mechanisms become testable regression infrastructure
- `observability-and-telemetry.md` — how mechanism usage, failures, and drift are measured

---

## §The Problem

Agents are strong at judgment, synthesis, decomposition, and context adaptation. They are weak at being deterministic machines across repeated invocations. When a skill asks an agent to manually perform a repeatable procedure, the procedure becomes a variance source.

A skill ecosystem without mechanization accumulates predictable failures:

1. **Manual procedure drift** — the agent follows the procedure slightly differently each time.
2. **Forgotten steps** — the agent skips a step that the prose described but did not enforce.
3. **Inconsistent verification** — the agent verifies with different evidence across runs.
4. **Silent failure modes** — the agent believes the procedure succeeded because nothing visibly failed.
5. **Untyped output interpretation** — the agent reads prose output and infers success incorrectly.
6. **Repeated recovery work** — the same failure is diagnosed manually in session after session.
7. **Unsafe mutation** — the agent performs destructive or irreversible work without a preview gate.
8. **Prompt-enforced determinism** — the system asks the agent to remember behavior that should be enforced.
9. **Mechanization bloat** — scripts, hooks, and validators are created speculatively and never used.

Mechanization is the correction: identify repeated, testable, variance-prone work and move it into an enforceable mechanism with a clear contract.

The goal is not full automation. The goal is **proper allocation**:

```txt
Agent judgment → choose mode, scope, mechanism, interpretation, recovery
Mechanism execution → parse, scan, format, validate, generate, gate, report
```

---

## §First Principles

### 1. Judgment stays with the agent; repeatability moves to mechanisms

The agent should decide:

- What mode am I in?
- What scope is authorized?
- Which mechanism should run?
- Did the mechanism pass?
- What does the result mean?
- What should happen if it fails?

The mechanism should handle:

- Parsing
- Scanning
- Diffing
- Formatting
- Counting
- Schema validation
- Version bumping
- File generation
- Test invocation
- Dry-run previews
- Exit codes
- Machine-readable output

If a step needs contextual judgment, keep it in the agent's reasoning path. If a step needs repeatable execution, move it into a mechanism.

### 2. Mechanize after evidence, not fantasy

A mechanism should usually emerge from observed repetition, not from imagined future use.

A procedure becomes mechanization-ready when it meets **three or more** of these conditions:

- Repeated across 3+ invocation cycles
- Has binary or typed success criteria
- Has silent failure modes
- Has destructive or high-blast-radius consequences
- Requires multi-step orchestration
- Produces frequent agent mistakes
- Has expensive manual review cost
- Requires consistency across agents or sessions
- Needs to run as a regression gate

A procedure that meets only one criterion can remain prose. A procedure that meets three or more is mechanization-bait. Convert it.

### 3. Mechanization is broader than scripts

A script is only one mechanism type. The mechanism should match the failure mode.

```txt
Repeated file edit → script
Formatting drift → formatter or pre-commit hook
Schema drift → validator
Prompt routing drift → eval corpus
Unsafe mutation → dry-run gate
Release inconsistency → workflow
Local forgetfulness → lifecycle hook
Team-wide correctness → CI gate
Security boundary → infrastructure policy
```

The question is not “should we write a script?” The question is “what deterministic boundary would remove this variance?”

### 4. Hooks enforce behavior that prompts can only request

A prompt can say:

```txt
Always run the formatter before committing.
```

A hook can actually run the formatter or block the commit.

Use prompts for intent, judgment, and mode selection. Use hooks for behavior that must happen at a specific lifecycle point. If the cost of forgetting a step is high, that step should not rely on memory.

### 5. CI gates are the promotion path for shared correctness

A local mechanism improves one agent's behavior. A CI gate improves the system's behavior.

Mechanisms often mature through this path:

```txt
manual command
→ documented script
→ agent-invoked script
→ hook-triggered script
→ CI-required gate
→ infrastructure-enforced policy
```

Not every mechanism should be promoted all the way up the ladder. Low-risk convenience scripts can remain local. Shared correctness checks should become CI gates. Security and irreversible-operation boundaries should become infrastructure-enforced policies.

### 6. Mechanisms need contracts, not hidden behavior

A mechanism that agents cannot invoke reliably is not fully mechanized. The interface is part of the mechanism.

A good mechanism contract defines:

- Purpose
- Inputs
- Outputs
- Exit codes
- Dry-run behavior
- JSON output shape
- Strict-mode behavior
- Failure messages
- Safety boundaries
- Examples

The agent should not need to read the implementation to use the mechanism correctly. If it does, the mechanism is under-specified.

### 7. Irreversible mechanisms must be two-phase

Any mechanism that deletes, publishes, deploys, sends, migrates, rewrites history, or mutates external state needs a preview phase.

```txt
Phase 1: dry-run → show intended mutation
Phase 2: execute → only after explicit authorization
```

Tool access is not authorization. The user or operator must authorize the specific irreversible action for the current task.

### 8. Mechanization must preserve scope containment

A mechanism can make the wrong action faster. It must therefore be scope-aware.

A safe mechanism knows:

- Which files or systems it is allowed to touch
- Which outputs it may write
- Whether it is running in read-only, dry-run, or execute mode
- Whether secrets must be redacted
- Whether external calls are allowed
- Whether operator confirmation is required

Mechanization that ignores scope is not maturity. It is amplified blast radius.

### 9. Mechanisms should produce evidence, not just side effects

A mechanism should leave behind a result the agent can reason over:

- What changed
- What passed
- What failed
- What was skipped
- What remains uncertain
- What requires authorization

For agentic systems, “the command ran” is not enough. The mechanism should produce evidence that can bind the Verify phase.

### 10. Mechanization has a lifecycle

Mechanisms are living assets. They should be introduced, promoted, audited, and deleted.

The lifecycle:

```txt
Observed repeated procedure
→ prose procedure in skill
→ mechanization candidate
→ local script / validator / hook
→ agent-facing contract
→ usage tracking
→ promotion to CI or workflow if shared correctness depends on it
→ audit and pruning
```

A dead script is not harmless. It consumes routing attention, creates stale affordances, and can mislead agents into using obsolete behavior.

---

## §Mechanization Ladder

Use the ladder to choose the minimum mechanism that removes the relevant variance.

| Level | Mechanism | Use when | Enforcement strength |
| --- | --- | --- | --- |
| 0 | Prompt instruction | One-off or judgment-heavy behavior | Advisory |
| 1 | Skill procedure | Reusable but still context-dependent behavior | Advisory |
| 2 | Script | Repeatable, testable procedure | Agent-invoked |
| 3 | Validator | Typed or structural correctness check | Agent/CI-invoked |
| 4 | Hook | Behavior must happen at a lifecycle point | Local enforcement |
| 5 | CI gate | Shared correctness must not regress | Repository enforcement |
| 6 | Workflow | Multi-step release/build/deploy orchestration | Pipeline enforcement |
| 7 | Infrastructure policy | Security, scope, or irreversible-action boundary | Architectural enforcement |

The higher the level, the less the system depends on the agent remembering what to do.

### Promotion heuristic

Promote a mechanism upward when the cost of missing it exceeds the cost of enforcing it.

```txt
Low-risk + infrequent → prompt or skill prose
Repeated + testable → script
Repeated + structural correctness → validator
Must happen locally → hook
Must hold across the team → CI gate
Multi-step operational flow → workflow
Security / irreversible / external-state mutation → infrastructure policy
```

---

## §The Rubric

### Dimension 1 — Mechanization candidate detection

Does the system reliably identify which procedures should become mechanisms?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Repeated, testable, failure-prone procedures are tracked and promoted into mechanisms. The 3-condition threshold is applied consistently. Mechanization candidates are reviewed during skill audits. |
| **4 — Good** | Most obvious candidates become scripts or validators. Some medium-frequency procedures remain prose. Promotion is mostly based on observed use, not speculation. |
| **3 — Adequate** | Scripts exist, but candidate detection is ad hoc. Procedures become mechanisms only after a failure or repeated annoyance. |
| **2 — Poor** | Many repeated procedures remain prose. Agents manually execute steps that are clearly testable or failure-prone. |
| **1 — Failing** | No candidate-detection discipline. Everything remains prompt/skill prose unless a human happens to write a tool. |

**Test**: inspect the 10 most repeated skill procedures. Which meet three or more mechanization conditions? If more than 3 remain prose, mechanization is underdeveloped.

---

### Dimension 2 — Mechanism fit

Is the chosen mechanism appropriate to the failure mode?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Mechanism type matches the failure mode: scripts for repeatable edits, validators for structure, hooks for lifecycle enforcement, CI for shared gates, workflows for orchestration, infrastructure policy for security boundaries. |
| **4 — Good** | Most mechanisms fit their failure modes. A few scripts could be better represented as hooks or validators, but the system works. |
| **3 — Adequate** | Mechanization exists but defaults to scripts for nearly everything. Fit is acceptable but not intentional. |
| **2 — Poor** | Mechanisms are mismatched: scripts for judgment, prose for deterministic steps, CI gates for low-risk convenience, prompts for high-risk enforcement. |
| **1 — Failing** | No mechanism-fit model. The system uses whichever mechanism was easiest to create. |

**Test**: pick 5 mechanisms. For each, name the failure mode it prevents. If the failure mode and mechanism type do not match, the mechanism is misfit.

---

### Dimension 3 — Interface contract quality

Can an agent invoke the mechanism correctly without reading its source?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Mechanisms expose complete contracts: `--help`, `--json`, `--strict`, `--dry-run` where relevant, clear exit codes, actionable errors, typed output schema, examples. Skill prose cites the mechanism rather than duplicating behavior. |
| **4 — Good** | `--help` and clear errors exist. JSON/strict/dry-run modes exist for most high-value mechanisms. Some edge-case behavior is under-documented. |
| **3 — Adequate** | Mechanism is usable but terse. Agent may need one failed attempt to infer correct invocation. Output is semi-structured. |
| **2 — Poor** | Mechanism exists but has weak documentation. Agent must inspect source, infer flags, or interpret vague output. |
| **1 — Failing** | Mechanism is a black box. No contract, no examples, no reliable success/failure signal. |

**Test**: give a fresh agent only the skill citation and `--help` output. Can it invoke the mechanism correctly and interpret the result?

---

### Dimension 4 — Enforcement level

Is the mechanism enforced at the right level for its risk and scope?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Enforcement level matches risk: advisory for low-risk convenience, hooks for local invariants, CI gates for shared correctness, infrastructure policy for security/irreversible boundaries. |
| **4 — Good** | High-risk mechanisms are enforced. Some medium-risk checks remain agent-invoked rather than hook/CI enforced. |
| **3 — Adequate** | Mechanisms are mostly agent-invoked. Enforcement depends on the agent remembering to run them. |
| **2 — Poor** | Important checks are documented but not enforced. Agents often skip them. |
| **1 — Failing** | No enforcement model. Mechanisms exist but are optional and frequently bypassed. |

**Test**: identify the 5 highest-risk correctness checks. Are they enforced by hook, CI, workflow, or policy? If they rely on prompt memory, enforcement is too weak.

---

### Dimension 5 — Verification binding

Does the mechanism produce evidence that can close the Verify phase?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Mechanisms emit concrete evidence: changed files, diff summary, test results, schema violations, release artifact, registry lookup, dry-run mutation list. Agent can cite the output as verification evidence. |
| **4 — Good** | Mechanisms produce pass/fail plus useful logs. Some outputs are not fully structured but still interpretable. |
| **3 — Adequate** | Mechanism exits 0/1, but the evidence behind the result is thin. Agent can tell pass/fail but not why. |
| **2 — Poor** | Mechanism produces vague prose like “looks good.” Agent must infer whether verification succeeded. |
| **1 — Failing** | Mechanism produces side effects only. No verification evidence. |

**Test**: after a mechanism runs, can the agent answer: what changed, what passed, what failed, and what remains uncertain?

---

### Dimension 6 — Safety and blast-radius control

Can the mechanism cause damage outside the authorized task scope?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Mechanisms are scope-aware, dry-run capable, confirmation-gated for irreversible actions, secret-redacting, and audit-logged. Writes are bounded to declared outputs. External calls are explicit. |
| **4 — Good** | High-risk mechanisms have dry-run and confirmation. Scope is mostly respected. Some low-risk tools have broad file access. |
| **3 — Adequate** | Safety exists in tool descriptions, but enforcement is partial. Agent is expected to avoid misuse. |
| **2 — Poor** | Mechanisms can mutate broad project state with minimal guardrails. Dry-run missing for some destructive operations. |
| **1 — Failing** | Mechanisms can delete, publish, deploy, send, or mutate external state without preview, confirmation, or scope checks. |

**Test**: call the mechanism with the wrong arguments. What is the maximum damage? If the answer is “unknown” or “large,” blast-radius control is insufficient.

---

### Dimension 7 — Lifecycle maintenance

Are mechanisms pruned, versioned, and promoted based on real use?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Usage is tracked. Dead mechanisms are removed. Contracts are versioned. Hooks and CI gates are audited. Mechanisms have owners or clear maintenance paths. Promotion/demotion follows observed value. |
| **4 — Good** | Mechanisms are reviewed periodically. Dead scripts are uncommon. Some usage tracking is manual. |
| **3 — Adequate** | Mechanisms are maintained when they break. No regular audit. Some stale scripts exist but are not actively harmful. |
| **2 — Poor** | Mechanisms accumulate. Old scripts, obsolete flags, and stale hooks remain available. Agents may use outdated mechanisms. |
| **1 — Failing** | Mechanism graveyard. No pruning. No owner. No one knows which mechanisms are still valid. |

**Test**: list mechanisms unused for 30/60/90 days. Are they deleted, demoted, or explicitly retained? If no one knows, lifecycle maintenance is missing.

---

## §Mechanism Types

### Scripts

Use scripts for repeatable, bounded procedures that can run on demand.

Good candidates:

- Version bumping
- File generation
- Bulk renaming
- Manifest updates
- Dependency graph checks
- Structured audits
- Repeated migration steps

Script contract minimum:

```txt
--help      explains behavior and arguments
--json      emits machine-readable output
--strict    exits non-zero when findings exist
--dry-run   previews changes before mutation, where relevant
```

### Validators

Use validators when the task is to prove a structure conforms to a contract.

Good candidates:

- Skill metadata validation
- Manifest schema validation
- Routing corpus validation
- Output-contract validation
- Token naming validation
- File/folder convention validation

Validators should emit:

```txt
rule_id
severity
path
message
expected
actual
suggested_fix
```

### Hooks

Use hooks when a behavior must happen at a lifecycle point.

Good candidates:

- Format before commit
- Block edit outside scope
- Prevent secret leakage
- Run local validation after generated files change
- Record telemetry after tool execution
- Stop repeated retries after stuck-counter threshold

Hooks should be narrow, fast, and observable. A slow hook becomes friction; a silent hook becomes confusion.

### CI gates

Use CI gates when shared correctness must not regress.

Good candidates:

- Build
- Test
- Type check
- Routing eval
- Skill schema validation
- Security scan
- Generated-file freshness check
- Documentation link validation

CI gates should have clear failure output and a local command that reproduces the failure.

### Workflows

Use workflows for multi-step orchestration.

Good candidates:

- Release pipeline
- Package publish
- Documentation generation
- Eval suite run
- Multi-agent task fan-out and merge
- Environment promotion

Workflows should expose checkpoints, rollback behavior, and artifact links.

### Infrastructure policies

Use infrastructure policy when the boundary is security-relevant or irreversible.

Good candidates:

- Least-privilege tool access
- External network restrictions
- Secret access control
- Production deployment authorization
- Scope-restricted file access
- Destructive-operation approval gates

Policies should not rely on the agent’s cooperation. They should hold even when the agent is wrong.

---

## §Anti-patterns

### AP-01 — The LLM-as-script

**Symptom**: the skill gives the agent deterministic instructions such as “open every package file, find the version field, increment it, update the lockfile, and check all versions match.”

**Root cause**: the procedure seems simple enough for the agent to do manually.

**Correction**: simplicity is not the criterion. Repeatability, testability, and failure modes are. Write a script with `--dry-run`, `--json`, and `--strict`. Have the skill cite the command.

---

### AP-02 — Prompt-enforced determinism

**Symptom**: the system relies on instructions like “always run tests before claiming done.”

**Root cause**: behavior that should be enforced is encoded as prose.

**Correction**: use hooks, CI gates, or workflow checks for behavior that must always happen. Prompts should express intent; mechanisms should enforce invariants.

---

### AP-03 — Script without contract

**Symptom**: a script exists, but the agent must read the source to understand flags, outputs, or failure behavior.

**Root cause**: the script was written for humans who already knew the context, not for agents.

**Correction**: treat `--help` as the behavioral contract. Add `--json` for machine output, `--strict` for gate behavior, and actionable errors for recovery.

---

### AP-04 — Mechanization theater

**Symptom**: a mechanism exists but only wraps a vague manual process.

Example:

```txt
scripts/check-quality.mjs
→ "Looks good."
```

**Root cause**: the existence of a script is mistaken for deterministic evidence.

**Correction**: emit typed findings with rule IDs, severities, paths, expected/actual values, and exit codes. If the mechanism cannot produce evidence, it is not a verification mechanism.

---

### AP-05 — The local-only gate

**Symptom**: a local script catches important failures, but CI does not run it. Different agents or team members bypass it.

**Root cause**: useful local mechanisms are not promoted to shared enforcement.

**Correction**: if the check protects shared correctness, promote it to CI. Local scripts are convenience; CI gates are governance.

---

### AP-06 — Premature tool taxonomy

**Symptom**: a skill launches with 20 scripts for imagined future cases. Most are never invoked.

**Root cause**: taxonomy design feels like progress before usage proves the shape.

**Correction**: start with prose. Track repeated procedures. Mechanize after the threshold is met. Delete unused mechanisms.

---

### AP-07 — Unsafe automation

**Symptom**: a mechanism can delete branches, publish packages, deploy code, or mutate a database without dry-run.

**Root cause**: automation was optimized for speed before blast radius was understood.

**Correction**: irreversible mechanisms are two-phase: preview first, execute only after explicit authorization. Confirmation is logged.

---

### AP-08 — Agent-visible secrets

**Symptom**: a mechanism requires the agent to pass credentials as text arguments or read a `.env` file into context.

**Root cause**: credential convenience was treated as tool usability.

**Correction**: tools receive credentials through infrastructure, environment variables, or a secrets manager. The agent never sees the secret value. Logs redact secret-like strings.

---

### AP-09 — Mechanism graveyard

**Symptom**: scripts, hooks, validators, and workflows accumulate. Agents discover obsolete tools and use them because they still exist.

**Root cause**: mechanisms are created but not owned, audited, or deleted.

**Correction**: mechanisms have lifecycle states: experimental, active, promoted, deprecated, removed. Run a 30/60/90-day usage audit.

---

### AP-10 — Mechanized judgment

**Symptom**: the system tries to script a context-heavy decision such as “choose the right architecture” or “decide whether this API is good.”

**Root cause**: overcorrection from agent variance into over-mechanization.

**Correction**: use rubrics for judgment and mechanisms for repeatability. Mechanisms can gather evidence for judgment; they should not replace judgment where context is irreducible.

---

## §Hard Tests

1. **Mechanization threshold test** Inspect the 10 most repeated skill procedures. Which meet three or more mechanization criteria? Which remain prose?

2. **Agent variance test** Run the same procedure through 5 fresh agents. If outputs differ materially, mechanize the deterministic portion.

3. **Contract test** Can a fresh agent invoke the mechanism correctly using only the skill citation and `--help`?

4. **JSON test** Can the agent parse the output without prose interpretation? If not, add `--json` or a typed output schema.

5. **Strict-mode test** Can the mechanism fail the task with a non-zero exit when findings are present? If not, it is not gate-ready.

6. **Dry-run test** For destructive actions, can the mechanism show the exact intended mutation before doing it?

7. **CI-promotion test** If this mechanism protects shared correctness, is it enforced in CI? If not, why is local execution sufficient?

8. **Hook test** If this mechanism protects local consistency, is it wired into the relevant lifecycle point?

9. **Dead-mechanism test** Which mechanisms have not been invoked in 30/60/90 days? Are they deleted, deprecated, or explicitly retained?

10. **Blast-radius test** What is the maximum damage if this mechanism is called with wrong arguments? If the answer is large, add scope enforcement, dry-run, or policy boundaries.

11. **Recovery test** Trigger a known failure. Does the mechanism produce an actionable error that tells the agent how to recover, or does the agent have to inspect implementation details?

12. **Evidence test** After the mechanism runs, can the agent report what changed, what passed, what failed, and what remains uncertain?

13. **Over-mechanization test** Pick 5 mechanisms. For each, ask: does this reduce variance or merely add indirection? Remove or collapse mechanisms that do not reduce variance.

14. **Scope test** Run the mechanism in a task scoped to one directory. Does it touch files outside the declared scope? If yes, scope containment is missing.

15. **Secret test** Run the mechanism with logging enabled. Do credentials, tokens, or secret-like strings appear in output, telemetry, or error messages?

---

## §Decision Guide

Use this guide when deciding how to mechanize a procedure.

### Keep as prose when:

- The task is judgment-heavy
- The procedure is rarely repeated
- Success cannot be reduced to a typed or observable signal
- The cost of building the mechanism exceeds the cost of manual execution
- The procedure is still changing every time it is invoked

### Convert to a script when:

- The steps are repeated
- Inputs and outputs are bounded
- Success/failure can be detected
- The procedure touches files or generated artifacts
- Manual execution creates drift

### Convert to a validator when:

- The target has a schema or convention
- Violations can be listed
- The output should be findings rather than changes
- The mechanism should run in CI or strict mode

### Convert to a hook when:

- The behavior must happen at a lifecycle point
- Forgetting the behavior is common or costly
- The check is fast enough not to disrupt flow
- Local consistency matters before CI

### Convert to a CI gate when:

- The check protects shared correctness
- Regressions must block merge
- The mechanism has stable output
- The local equivalent exists and can reproduce failures

### Convert to a workflow when:

- The process has multiple stages
- Each stage has artifacts or checkpoints
- Rollback or resume behavior matters
- Release, publish, deploy, or multi-agent orchestration is involved

### Convert to infrastructure policy when:

- The boundary is security-relevant
- The action is irreversible
- Tool access must be least-privilege
- The system must be safe even when the agent is wrong

---

## §Recommended Mechanism Contract Template

````md
# <mechanism-name>

## Purpose
One sentence describing the variance this mechanism removes.

## Use when
- Condition 1
- Condition 2
- Condition 3

## Do not use when
- Boundary 1
- Boundary 2

## Command
```bash
node scripts/<name>.mjs --flag value --json --strict
````

## Inputs

| Argument    | Required | Meaning                                   |
| ----------- | -------: | ----------------------------------------- |
| `--scope`   |      yes | File, directory, package, or system scope |
| `--json`    |       no | Emit machine-readable output              |
| `--strict`  |       no | Exit non-zero on findings                 |
| `--dry-run` |       no | Preview changes without writing           |

## Outputs

```json
{
  "ok": true,
  "changed": [],
  "findings": [],
  "summary": ""
}
```

## Exit codes

| Code | Meaning                          |
| ---: | -------------------------------- |
|    0 | Success / no findings            |
|    1 | Findings present in strict mode  |
|    2 | Invalid input or scope violation |
|    3 | Runtime/tool failure             |

## Safety

- Scope-aware: yes/no
- Dry-run supported: yes/no
- Writes files: yes/no
- External calls: yes/no
- Secrets redacted: yes/no

## Verification evidence

What the agent can cite after running this mechanism.

````

---

## §Summary

Mechanization is not the opposite of agentic work. It is what makes agentic work reliable.

The agent should own intent, judgment, decomposition, and recovery. Mechanisms should own the
repeatable, testable, failure-prone parts of execution. A mature skill system does not ask the
agent to manually perform deterministic procedures forever. It observes repeated work, extracts
mechanisms, binds those mechanisms to contracts, promotes them into enforcement when needed, and
prunes them when they stop earning their keep.

The final test is simple:

```txt
If this step must happen the same way every time, why is it still prose?
````
