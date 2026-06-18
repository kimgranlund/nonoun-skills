---
date: 2026-05-24
status: draft
version: "0.1.0"
---

# Worktree Operations — Best Practices Rubric

**A worktree is an execution lane, not a folder.**

Worktree operations is the discipline of coordinating multiple autonomous or semi-autonomous coding agents across isolated Git worktrees while preserving intent, ownership, reviewability, and merge safety. In a multi-agent harness, the hard problem is not creating branches. The hard problem is preventing branch state, staged state, partial commits, conflicts, generated files, and integration order from becoming invisible operational debt.

The central failure mode: **state ambiguity**. An agent has modified files, another agent has touched the same subsystem, a third agent has staged unrelated changes, and the orchestrator no longer knows what is safe to commit, rebase, merge, abandon, or archive. Once state becomes ambiguous, every subsequent operation becomes risky.

The correction is to treat worktree management as an operations layer with typed state, explicit ownership, bounded mutation, and integration gates. Git remains the substrate. The harness supplies the operating model.

**Companion docs:**

- `harness-design.md` — harness as the cold-start operating layer
- `context-engineering.md` — keeping task state precise and current
- `progressive-context-construction.md` — loading operational context by phase
- `inversion-and-abstraction.md` — mechanizing repeated Git/worktree procedures
- `tool-use.md` — tool contracts, structured output, and blast-radius control
- `evaluation-workflows.md` — regression gates before integration

---

## §The Problem

Multi-agent coding fails when the system treats Git state as self-explanatory. Git can tell you that a worktree is dirty, a branch diverged, or a file is staged. It does not know whether those changes are intentional, whether they belong to the assigned task, whether the staged subset is coherent, whether another agent owns the same path, or whether the branch is safe to integrate.

The specific failures:

1. **Workspace collision**: multiple agents edit overlapping files without a declared ownership boundary. The conflict is discovered at merge time, when the task context is already stale.

2. **Staged-state ambiguity**: an agent partially stages files, leaves unstaged edits behind, and commits a subset that may or may not represent a coherent unit of intent.

3. **Commit without verification**: a branch is committed because the code compiles locally or the agent finished editing, but no gate has proven that the change works against the current integration state.

4. **Integration roulette**: branches are merged in whatever order they complete, not in dependency order or conflict-risk order. The integration branch becomes a conflict accumulator.

5. **Shared-file churn**: every feature branch modifies `package.json`, lockfiles, barrel exports, route registries, token indexes, or generated files. Most conflicts are not domain conflicts; they are coordination failures around shared surfaces.

6. **Dirty rebase / dirty merge**: the harness rebases or merges a worktree with unstaged, untracked, or partially staged changes. Recovery becomes forensic.

7. **Abandoned work without record**: a worktree is deleted or overwritten without preserving why it existed, what was attempted, and whether any useful patch should survive.

8. **Orchestrator blindness**: the harness relies on `git status` alone. It lacks a typed manifest describing task intent, owner, lifecycle state, allowed paths, validation target, and integration target.

---

## §First Principles

### 1. One task = one branch = one worktree = one owner

A worktree should map to a single unit of intent. A branch that contains three unrelated fixes is not a work lane; it is a bag of edits. A worktree with no owner is an unbounded mutation surface.

The invariant:

```txt
task id → branch → worktree path → owner → merge target
```

If any link is missing, the harness cannot reason safely about the work.

### 2. Git state is necessary but insufficient

`git status` tells you what changed. It does not tell you whether the change is allowed, coherent, validated, or ready to integrate. The harness needs its own state model layered over Git:

```txt
assigned → in_progress → dirty → staged → committed → validated → review_ready → integration_pending → integrated → archived
```

Git is the mechanical substrate. The manifest is the operational source of truth.

### 3. Agents author candidate changes; the orchestrator owns state transitions

An agent may edit files, run checks, propose staged changes, and create commits. It should not unilaterally decide that work is integrated, safe to merge, safe to rebase, or safe to delete.

The harness owns:

```txt
worktree creation
path ownership
stage approval
commit acceptance
validation gates
integration order
branch cleanup
archive policy
```

This separation prevents local agent confidence from becoming system-level truth.

### 4. Path ownership prevents most conflicts before they exist

Merge conflicts are usually late symptoms of early ambiguity. If two agents need the same files, that fact should be visible before they start. The harness should assign path ownership and flag shared surfaces explicitly.

High-conflict files should be orchestrator-owned by default:

```txt
package.json
lockfiles
route registries
barrel exports
global token files
schema registries
migration files
generated indexes
```

Agents may request changes to shared files. The orchestrator applies or regenerates them.

### 5. Staging is a review boundary

Staging is not a mechanical prelude to commit. It is the moment where the agent says: “this exact diff is the unit of intent.” The harness should inspect staged changes independently from unstaged changes.

A partially staged file is a warning, not a normal state:

```txt
MM src/foo.ts
```

It means the committed diff and working diff differ. That can be correct, but it must be intentional.

### 6. Integration is a separate lane

Branches should not land directly in `main` merely because they passed local checks. Multi-agent systems need an integration branch where completed work is merged in dependency order, tested together, and reviewed as a batch.

The integration lane is where local correctness becomes system correctness.

### 7. Recovery must be designed before failure

Any operation that rewrites history, deletes a worktree, rebases a branch, resolves conflicts, or abandons work should have a snapshot policy. For agent-authored work, prefer visible recovery artifacts:

```txt
WIP commit
patch export
manifest update
integration report
```

Stashes are acceptable for humans. For harnesses, durable and inspectable records are better.

---

## §The Operating Model

A mature harness should maintain a worktree manifest. The manifest should not duplicate Git internals; it should capture the operational facts Git does not know.

```json
{
  "id": "UI-142",
  "intent": "Implement command menu shell and keyboard navigation",
  "owner": "agent-a",
  "branch": "feature/UI-142-command-menu",
  "worktree": "../worktrees/UI-142-command-menu",
  "base": "main",
  "base_sha": "abc123",
  "status": "in_progress",
  "allowed_paths": [
    "src/components/command-menu/**",
    "tests/command-menu/**"
  ],
  "blocked_paths": [
    "package.json",
    "pnpm-lock.yaml",
    "src/index.ts"
  ],
  "merge_target": "integration/2026-05-24-agent-batch",
  "validation": [
    "npm run typecheck",
    "npm run test -- command-menu"
  ],
  "last_known_commit": null,
  "risk": "medium"
}
```

The manifest enables the harness to answer operational questions:

```txt
Who owns this path?
Which worktrees are dirty?
Which branches are committed but unvalidated?
Which branches are validated but not integrated?
Which tasks are blocked on shared-file changes?
Which worktrees can be archived?
```

Without a manifest, the orchestrator must infer these answers from Git and conversation history. That is the root of state ambiguity.

---

## §The Rubric

### Dimension 1 [gate] — Worktree isolation and ownership

Does every active task have a dedicated branch, worktree, owner, and merge target?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every active task has exactly one branch, one worktree, one owner, one base SHA, and one merge target recorded in a manifest. No agent edits the canonical checkout. Ownership is visible before work starts. |
| **4 — Good** | Most tasks have dedicated worktrees and clear owners. A few small fixes share a worktree but are explicitly grouped and reviewed as one unit. |
| **3 — Adequate** | Worktrees are used, but ownership lives in convention or conversation rather than a manifest. Agents usually avoid collisions but the system cannot prove it. |
| **2 — Poor** | Some agents work in branches without dedicated worktrees. Others share worktrees. Ownership is discovered from recent commits or chat history. |
| **1 — Failing** | Multiple agents mutate the same checkout or `main` branch. No reliable isolation exists. |

**Test**: list all active tasks. For each, identify branch, worktree path, owner, base SHA, and merge target. Any missing value is an isolation gap.

---

### Dimension 2 [gate] — Manifest-backed lifecycle state

Is work tracked through explicit lifecycle states, or inferred from raw Git state?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Harness tracks lifecycle states: `assigned`, `in_progress`, `dirty`, `staged`, `committed`, `validated`, `review_ready`, `integration_pending`, `integrated`, `archived`, `abandoned`. State transitions are explicit and logged. Git state and manifest state are reconciled automatically. |
| **4 — Good** | Manifest tracks major states: in progress, committed, validated, integrated. Some intermediate states such as partially staged or abandoned are handled manually. |
| **3 — Adequate** | Git state is inspected regularly, but no durable lifecycle model exists. Operators can reconstruct state, but only with effort. |
| **2 — Poor** | Status is tracked in comments, chat, or memory. Git and human understanding frequently diverge. |
| **1 — Failing** | No lifecycle state. The system cannot distinguish dirty, staged, committed, validated, and integrated work without manual forensics. |

**Test**: choose a random worktree. Can the harness state whether it is safe to commit, safe to rebase, safe to integrate, or safe to archive? If not, lifecycle state is under-modeled.

---

### Dimension 3 [gate] — Path ownership and shared-surface control

Does the harness prevent file-level collisions before agents start work?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every task has `allowed_paths` and `blocked_paths`. Shared files are orchestrator-owned. Changes outside allowed paths are blocked or escalated before commit. Generated files and registries are regenerated by the orchestrator, not hand-edited by feature agents. |
| **4 — Good** | Path ownership exists for high-risk areas. Shared-file edits require review. Some low-risk overlap is allowed with warnings. |
| **3 — Adequate** | Agents are instructed to stay in scope but enforcement is manual. Out-of-scope changes are usually caught during review. |
| **2 — Poor** | No path ownership model. Conflicts are handled after they occur. Shared files are edited freely by multiple agents. |
| **1 — Failing** | Agents routinely overwrite each other's changes or produce conflicting edits to shared files. Conflict resolution is the primary integration activity. |

**Test**: for every changed file in a worktree, compare it to the task's allowed paths. Any unexplained out-of-scope file is either a task expansion or a scope violation. It cannot be ignored.

---

### Dimension 4 [review] — Staging and commit discipline

Are staged changes treated as coherent units of intent?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Broad `git add .` is prohibited unless explicitly allowed. Harness inspects `git diff --cached` before commit. Partially staged files are flagged. Commit messages include task id, intent, changed scope, validation, risks, and follow-ups. |
| **4 — Good** | Explicit staging is standard. Staged diffs are reviewed before important commits. Commit messages include task id and validation. |
| **3 — Adequate** | Agents usually stage correctly, but broad adds occur. Commit messages are readable but not structured. Partially staged files are handled case-by-case. |
| **2 — Poor** | Agents frequently commit whatever is in the worktree. Staged and unstaged states are not distinguished in review. |
| **1 — Failing** | Commits contain unrelated changes, temporary files, generated artifacts, or unstated scope expansions. Commit history cannot be reviewed by intent. |

**Test**: inspect the latest commit from an agent branch. Can a reviewer determine the task, intent, changed files, validation performed, and known risks from the commit alone?

---

### Dimension 5 [gate] — Validation before integration

Does every branch pass defined gates before entering the integration lane?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each task has explicit validation commands. Branches cannot enter `integration_pending` until working tree is clean, scope check passes, tests/checks pass, and diff matches intent. Validation output is recorded. |
| **4 — Good** | Validation gates exist and are usually enforced. Some low-risk changes receive abbreviated validation, but the exception is documented. |
| **3 — Adequate** | Agents run tests before marking work done. Results may not be captured. Scope and diff review are manual. |
| **2 — Poor** | Validation is optional or inconsistent. Branches are integrated based on agent confidence. |
| **1 — Failing** | Work is merged without proof that it builds, tests, or satisfies its task contract. |

**Test**: pick the last integrated branch. Find the validation evidence. If the evidence is “the agent said it should work,” the gate is missing.

---

### Dimension 6 [review] — Integration ordering and batch control

Is integration orchestrated by dependency and risk, or by completion order?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Integration branch created per batch. Branches are merged in dependency order. High-conflict branches are integrated early or isolated. After each merge, targeted checks run; after the batch, full checks run. Integration report records order, conflicts, resolutions, and validation. |
| **4 — Good** | Integration branch exists. Merge order is considered manually. Full checks run before landing to `main`. Integration reports are lightweight but present. |
| **3 — Adequate** | Branches usually merge through PRs or an integration branch, but ordering is informal. Conflicts are resolved when encountered. |
| **2 — Poor** | Branches merge directly to `main` as they complete. Broken interactions are discovered after merge. |
| **1 — Failing** | Multiple agents push or merge directly to `main` without coordination. `main` is the integration test surface. |

**Test**: for the last batch, list the merge order and why that order was chosen. If the answer is “that is when the branches finished,” integration is not orchestrated.

---

### Dimension 7 [review] — Recovery, abandonment, and archive safety

Can the harness recover from failed rebases, abandoned work, and stale worktrees without losing useful state?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Before risky operations, harness creates a WIP commit or patch export. Abandoned work records reason, diff summary, and salvageable artifacts. Archived worktrees are removed only after integration or explicit abandonment. `git worktree prune` is part of cleanup. |
| **4 — Good** | Snapshotting is standard before rebases and destructive cleanup. Abandonment is recorded but not deeply summarized. |
| **3 — Adequate** | Operators usually stash or copy patches before risky operations. Recovery depends on operator discipline. |
| **2 — Poor** | Worktrees are deleted or reset ad hoc. Useful work is occasionally lost. |
| **1 — Failing** | Failed rebases, force resets, and worktree removals routinely destroy or obscure work. No recovery protocol exists. |

**Test**: intentionally abandon a half-finished branch. Can another agent later answer what was attempted, why it was abandoned, and whether any patch should be reused?

---

## §Anti-patterns

### AP-01 — The shared checkout swarm

**Symptom**: multiple agents work in the same repository checkout, switching branches or editing files concurrently.

**Root cause**: treating branches as isolation while ignoring filesystem state. Branches isolate commits; worktrees isolate working directories.

**Correction**: one agent lane gets one worktree. The canonical checkout stays on `main` or the integration branch. Agents do not edit it.

---

### AP-02 — Branch names without intent

**Symptom**: branches named `agent-a-work`, `fixes`, `new-feature`, or `wip`.

**Root cause**: branch naming optimized for creation speed, not reviewability.

**Correction**: encode type, task id, and short intent:

```txt
feature/UI-142-command-menu
fix/UI-155-dialog-focus-return
refactor/UI-161-token-compiler
```

A branch name should let the orchestrator predict scope before reading the diff.

---

### AP-03 — `git add .` as default behavior

**Symptom**: commits include debug files, unrelated edits, generated outputs, or changes from earlier attempts.

**Root cause**: staging treated as mechanical. The agent stages the filesystem, not the intent.

**Correction**: default to explicit path staging or patch staging. Permit `git add .` only inside a task-owned narrow directory or after the harness verifies the changed-file list.

---

### AP-04 — Dirty rebase

**Symptom**: a rebase starts while the worktree has unstaged, staged, or untracked changes. Recovery requires guessing which changes predated the rebase.

**Root cause**: the harness optimizes for progress over state clarity.

**Correction**: only rebase clean worktrees. If the worktree is not clean, create a WIP commit or patch export first. The context must change from “dirty” to “snapshotted” before history rewriting.

---

### AP-05 — Integration by arrival time

**Symptom**: branches merge in the order agents finish. A foundational refactor lands after dependent features. Conflicts are resolved repeatedly.

**Root cause**: completion order mistaken for integration order.

**Correction**: integrate by dependency and conflict risk. Foundational branches first, narrow leaf changes later. High-conflict shared surfaces should be merged or regenerated by the orchestrator.

---

### AP-06 — Shared-file free-for-all

**Symptom**: every feature modifies `src/index.ts`, routes, lockfiles, token maps, or registries. Most conflicts occur in files unrelated to the feature's actual logic.

**Root cause**: no distinction between feature-owned files and orchestrator-owned files.

**Correction**: move shared edits into manifests, generators, or orchestrator-owned follow-up commits. Feature agents create local artifacts; the orchestrator updates shared surfaces.

---

### AP-07 — Commit equals done

**Symptom**: once an agent commits, the task is treated as complete.

**Root cause**: conflating “changes recorded” with “changes validated.”

**Correction**: commit moves work to `committed`, not `validated`. Only verification evidence moves it to `review_ready` or `integration_pending`.

---

### AP-08 — Worktree graveyard

**Symptom**: stale worktrees accumulate. Nobody knows which are active, abandoned, merged, or safe to remove.

**Root cause**: worktree creation is mechanized; worktree cleanup is not.

**Correction**: every worktree has a lifecycle state and archive rule. Cleanup is a first-class harness operation, not a manual filesystem sweep.

---

## §Hard Tests

1. **The active-lane test**: list every active worktree. For each: task id, branch, owner, base SHA, status, merge target. If any answer requires reading chat history, the manifest is insufficient.

2. **The scope-diff test**: for each dirty or committed worktree, run changed-file inspection and compare against `allowed_paths`. Every out-of-scope change must be classified as intentional expansion, shared-surface request, or violation.

3. **The staged-coherence test**: inspect `git diff --cached` and `git diff`. If a file appears in both staged and unstaged diffs, require an explicit reason before commit.

4. **The validation-evidence test**: before integration, require recorded output for the task's validation commands. A branch without validation evidence cannot enter the integration queue.

5. **The integration-order test**: given five review-ready branches, ask the orchestrator to justify merge order by dependency and conflict risk. If it cannot, the batch is not ready.

6. **The shared-surface test**: identify the top 10 most commonly conflicted files. If they are registries, lockfiles, indexes, or generated files, move them to orchestrator-owned updates or generated outputs.

7. **The dirty-rebase test**: attempt to rebase a dirty worktree. The harness should refuse and require snapshotting. If it proceeds, recovery safety is failing.

8. **The archive test**: pick a worktree marked archived. Can you find the integration commit, abandonment reason, or patch export? If not, archive state is cosmetic.

9. **The main-protection test**: verify no agent worktree is on `main` and no agent has write permission to merge directly into `main`. If agents can mutate `main`, integration control is not real.

10. **The recovery-drill test**: simulate a conflict during integration. Can the harness produce a conflict report that names the branches, files, owners, and recommended resolution path? If not, conflict handling is improvised.

---

## §Reference Operating Procedure

### 1. Create the integration batch

```bash
git fetch origin
git checkout main
git pull --ff-only
git checkout -b integration/2026-05-24-agent-batch
```

Record the batch:

```json
{
  "batch": "integration/2026-05-24-agent-batch",
  "base": "main",
  "status": "open",
  "branches": []
}
```

### 2. Create a worktree per task

```bash
git worktree add ../worktrees/UI-142-command-menu \
  -b feature/UI-142-command-menu main
```

Record the lane in the manifest with owner, allowed paths, blocked paths, validation commands, and merge target.

### 3. Monitor worktree state

Run status inspection regularly:

```bash
git status --porcelain=v1
git diff --name-only
git diff --cached --name-only
git log --oneline main..HEAD
```

Classify the result into lifecycle state. Do not rely on the agent's self-report.

### 4. Stage intentionally

Prefer:

```bash
git add src/components/command-menu/command-menu.ts
git add src/components/command-menu/command-menu.css
git add tests/command-menu/command-menu.test.ts
```

Avoid broad staging unless the changed-file list is already scoped and reviewed.

### 5. Commit with operational metadata

```txt
feat(command-menu): add shell and keyboard navigation

Task: UI-142
Intent: Implement command menu shell with roving focus and keyboard navigation.

Changed:
- Added command menu custom element
- Added keyboard navigation behavior
- Added focused tests for open/close and arrow movement

Validation:
- npm run typecheck
- npm run test -- command-menu

Risks:
- Global shortcut wiring deferred to UI-143

Follow-ups:
- Add visual regression coverage after styling lands
```

### 6. Validate before queueing

A branch enters `review_ready` only after:

```txt
working tree clean
scope diff passes
validation commands pass
commit message carries task metadata
known risks are recorded
```

### 7. Integrate in order

On the integration branch:

```bash
git merge --no-ff feature/UI-142-command-menu
npm run typecheck
npm run test -- command-menu
```

After all queued branches:

```bash
npm run test
npm run build
```

Record conflicts, resolutions, and validation in an integration report.

### 8. Archive after landing

After the integration branch lands:

```bash
git worktree remove ../worktrees/UI-142-command-menu
git branch -d feature/UI-142-command-menu
git worktree prune
```

If the branch was squash-merged, deletion may require explicit force after confirming the integration record exists:

```bash
git branch -D feature/UI-142-command-menu
```

---

## §Minimum Viable Harness Contract

For small systems, start with only this:

```txt
one worktree per task
one branch per worktree
manifest with owner, intent, allowed paths, status, validation
no direct work on main
no commit from dirty ambiguity
no integration without validation evidence
no archive without merge or abandonment record
```

This is enough to prevent most multi-agent worktree failures.

---

## §Mature Harness Contract

For larger systems, add:

```txt
path ownership graph
integration queue
dependency-aware merge ordering
shared-surface ownership
generated index regeneration
structured validation records
WIP snapshot protocol
patch export protocol
conflict reports
archive reports
branch cleanup automation
worktree stale-state audits
```

The mature version looks like local CI/CD for agent work: not because ceremony is inherently valuable, but because uncontrolled local mutation is the bottleneck. The goal is not more Git process. The goal is fewer ambiguous states.

---

## §Hard Rule Summary

```txt
One task = one branch = one worktree = one owner.
Agents do not work on main.
The manifest is the operational source of truth.
Path ownership is declared before editing.
Shared files are orchestrator-owned by default.
Staging is a review boundary.
Commit does not mean done.
Validation evidence gates integration.
Integration happens in a dedicated lane.
Dirty work is snapshotted before risky operations.
Archive only after merge or explicit abandonment.
```
