---
date: 2026-05-24
status: draft
version: "0.1.0"
---

# Agents UX Wireframing (ASCII Wireframes) — Best Practices Rubric

**ASCII wireframes are not primitive mockups. They are compressed reasoning artifacts.**

An ASCII wireframe is a text-native structural contract between product intent, information architecture, interaction design, responsive behavior, and implementation decomposition. For agentic UI systems, it is one of the highest-leverage intermediate artifacts: cheap enough to revise, structured enough to review, and close enough to implementation to prevent layout hallucination before code is generated.

The central failure mode is **premature visual collapse**: an agent jumps from a product prompt directly to polished components, styling, or implementation before it has stabilized structure, hierarchy, state, navigation, and interaction ownership.

ASCII wireframing prevents this by forcing a useful intermediate step:

```txt
Intent → IA → Layout Structure → Interaction Model → ASCII Wireframe → Component Mapping → Visual Design → Implementation
```

The goal is not visual fidelity. The goal is structural clarity, reversible iteration, implementation decomposition, and reviewable intent.

**Companion docs:**

- `generative-ui-reasoning.md` — decision-first UI generation and avoidance of premature rendering
- `context-engineering.md` — minimum effective dose of context
- `progressive-context-construction.md` — loading the right information at the right phase
- `harness-design.md` — where wireframe generation and review should surface in the agent harness
- `evaluation-workflows.md` — how to test wireframe quality as an output contract
- `tool-use.md` — when wireframes should be produced by deterministic utilities vs. freeform prose

---

## §The Problem

Most agentic UI failures do not begin in code. They begin in the missing intermediate representation between the user's product intent and the agent's implementation output.

When an agent moves directly from prompt to UI, it tends to produce:

1. **Visually plausible but structurally incoherent UI** — cards, tables, sidebars, and filters appear because they are common patterns, not because they were derived from user goals, decisions, or information architecture.

2. **Layout hallucination** — the generated component tree implies spatial relationships that were never reasoned through: persistent panels that should be transient, scroll regions that conflict, navigation areas that duplicate each other, and density choices that cannot survive real data.

3. **Unstable implementation decomposition** — the code generator invents components before ownership is clear. State, focus, scrolling, and navigation end up smeared across the tree.

4. **Missing state surfaces** — the resting layout is represented, but loading, empty, error, expanded, collapsed, permission, and responsive states are omitted.

5. **Unreviewable visual artifacts** — screenshots or polished mockups are expensive to critique at the structural level because reviewers are pulled into visual taste, not system mechanics.

6. **Token-expensive iteration** — each iteration asks the model to regenerate prose, code, and style together. The actual question may have been only: "should the filter panel be persistent or collapsible?"

ASCII wireframes solve these failures by providing a low-cost, text-native, diffable representation of spatial reasoning before the system commits to visual or implementation detail.

---

## §First Principles

### 1. ASCII wireframes represent spatial reasoning, not visual design

An ASCII wireframe should answer:

```txt
what exists?
where does it live?
how does it relate?
what persists?
what changes?
what scrolls?
what owns focus?
what owns navigation?
what owns state?
what collapses responsively?
```

It should not answer:

```txt
what exact color?
what exact typography?
what brand expression?
what final spacing?
what animation curve?
```

Those are later decisions. Smuggling them into the wireframe collapses the reasoning layers too early.

### 2. The wireframe is a layout AST

Treat the wireframe as an intermediate structural representation.

```txt
boxes      → regions
labels     → semantics
nesting    → ownership
adjacency  → relationship
arrows     → transitions
brackets   → controls
annotations → behavior and constraints
```

The wireframe is not ASCII art. It is a compact syntax for layout hierarchy, interaction surfaces, state boundaries, and implementation segmentation.

### 3. Every region must justify its existence

A region is valid only if it traces to at least one upstream reason:

```txt
user goal
task
decision
data group
action group
navigation need
state surface
```

A region that exists because "dashboards usually have this" is a dead region. Dead regions become dead components, which become dead implementation surface.

### 4. Annotate ownership, not decoration

The wireframe should make ownership explicit:

```txt
scroll owner
focus owner
state owner
navigation owner
data owner
action owner
responsive owner
```

The key implementation failures in generated UI often come from ambiguous ownership, not from bad styling. An ASCII wireframe that shows boxes but not ownership is a partial artifact.

### 5. State variants are part of the wireframe

A static resting-state wireframe is not enough. Any meaningful UI surface should include the state variants that alter structure or interaction:

```txt
default
loading
empty
error
expanded
collapsed
selected
disabled
permission denied
mobile / narrow
wide / dense
```

State surfaces are not polish. They are required structural specifications.

### 6. Responsive behavior must be represented structurally

A desktop-only ASCII wireframe can be worse than no wireframe if it implies impossible responsive behavior. A useful wireframe either includes responsive variants or explicitly marks unknown responsive behavior as unresolved.

The minimum responsive questions:

```txt
what collapses?
what stacks?
what becomes modal?
what becomes hidden?
what remains persistent?
what changes navigation pattern?
what changes scroll ownership?
```

### 7. Wireframes are review gates, not final deliverables

The wireframe should be used to prevent downstream waste. It is a checkpoint before:

```txt
visual design
component mapping
code generation
agent implementation
multi-agent task decomposition
```

If the wireframe does not change the plan when problems are found, it is decorative documentation, not a gate.

### 8. The best wireframe is the smallest artifact that preserves the right decisions

Do not produce elaborate ASCII diagrams for trivial UI. The right level of detail depends on risk:

```txt
small component → semantic skeleton
page layout → region wireframe
workflow → interaction wireframe
application shell → persistent/responsive wireframe
complex product surface → full state + ownership wireframe
```

The wireframe should contain the minimum effective dose of structure needed to make the next step safe.

---

## §Wireframe Levels

ASCII wireframes operate at several levels. A mature agent should pick the level based on the task.

### Level 1 — Region Wireframe

Used for app shells, dashboards, pages, navigation structures, and layout exploration.

```txt
+-------------------------------------------------------------+
| Header: product / search / user menu                       |
+---------------+---------------------------------------------+
| Sidebar       | Main                                        |
| - Overview    | +----------------+ +----------------------+ |
| - Leads       | | KPI Summary    | | SLA Risk             | |
| - Reports     | +----------------+ +----------------------+ |
|               | +-----------------------------------------+ |
|               | | Lead Queue                              | |
|               | +-----------------------------------------+ |
+---------------+---------------------------------------------+
```

Answers:

```txt
what are the major regions?
which regions persist?
which regions are adjacent?
which regions dominate the surface?
```

### Level 2 — Interaction Wireframe

Used for flows, modal/sheet behavior, commands, state transitions, and focus/navigation models.

```txt
[Search Input]
    ↓ focus / shortcut
+--------------------------------+
| Command Menu                   |
|--------------------------------|
| Recent                         |
| Suggested Actions              |
| Navigation                     |
|--------------------------------|
| ↑/↓ move focus | Enter select   |
+--------------------------------+
    ↓ select
[Route Transition or Action]
```

Answers:

```txt
what changes?
what triggers the change?
what owns focus?
what action follows selection?
```

### Level 3 — State Wireframe

Used when structural behavior changes across states.

```txt
DEFAULT
+-------------------------------+
| Lead Queue                    |
| [Filter] [Sort] [Bulk Action] |
|-------------------------------|
| Row                           |
| Row                           |
| Row                           |
+-------------------------------+

EMPTY
+-------------------------------+
| Lead Queue                    |
|-------------------------------|
| No leads match these filters. |
| [Clear filters]               |
+-------------------------------+

ERROR
+-------------------------------+
| Lead Queue                    |
|-------------------------------|
| Could not load leads.         |
| [Retry] [View status]         |
+-------------------------------+
```

Answers:

```txt
what happens when data is absent?
what happens when loading fails?
what action is available from each state?
```

### Level 4 — Responsive Wireframe

Used when layout changes across width, density, or device posture.

```txt
WIDE
+----------+-----------------------------------+--------------+
| Sidebar  | Main                              | Inspector    |
+----------+-----------------------------------+--------------+

MEDIUM
+----------+-----------------------------------+
| Sidebar  | Main                              |
|          | [Inspector opens as side sheet]   |
+----------+-----------------------------------+

NARROW
+---------------------------------------------+
| Top Bar: Menu / Title / Actions             |
+---------------------------------------------+
| Main                                        |
|---------------------------------------------|
| [Inspector opens as full-height sheet]      |
+---------------------------------------------+
```

Answers:

```txt
what persists?
what collapses?
what becomes transient?
what owns navigation at each breakpoint?
```

### Level 5 — Semantic Component Wireframe

Used for implementation decomposition and multi-agent task planning.

```txt
<AppShell>
 ├─ <TopNav owns="global-navigation search user-menu">
 ├─ <Sidebar owns="primary-navigation">
 └─ <LeadDashboardPage>
     ├─ <LeadSummaryGrid owns="metrics">
     ├─ <LeadQueue owns="list-state filters selection">
     └─ <LeadInspector owns="selected-lead detail-actions">
```

Answers:

```txt
what becomes a component?
what owns state?
what receives data?
what can be assigned to separate agents?
```

---

## §Canonical Notation

A team or harness should define a small, stable grammar. The goal is not beauty; the goal is consistent interpretation by agents and reviewers.

### Region notation

```txt
+-----+       persistent region
|     |
+-----+

[Control]    interactive control

{State}      data/state surface

<Thing>      semantic component

→            transition or flow

↓            focus/flow descent

...          repeated content

/            responsive alternative

!            risk or unresolved issue
```

### Annotation notation

Use compact inline annotations:

```txt
Main Content [scroll: page]
Filter Panel [state: local] [collapse: narrow]
Command Menu [focus: roving] [dismiss: Escape/outside-click]
Inspector [data: selectedLead] [responsive: sheet@medium modal@narrow]
```

### Ownership notation

```txt
[owns: focus]
[owns: scroll]
[owns: selection]
[owns: route]
[owns: data-query]
[owns: mutation]
[owns: visibility]
```

### State notation

```txt
{loading}
{empty}
{error}
{permission-denied}
{stale}
{expanded}
{collapsed}
```

### Responsive notation

```txt
[wide: persistent]
[medium: side-sheet]
[narrow: full-screen-sheet]
[collapse < 768px]
[stack < 1024px]
```

### Unknown notation

Mark unresolved questions directly in the wireframe.

```txt
! unresolved: should filters persist on tablet?
! risk: table has 9 columns with no narrow strategy
! dependency: requires role permission model
```

Unknowns are useful. Hidden unknowns are not.

---

## §The Rubric

### Dimension 1 [gate] — Intent-to-structure traceability

Does every major region trace to a user goal, task, decision, or data/action group?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every major region has an explicit upstream reason. Region labels are semantic, not decorative. A trace table can be built from goal/task/decision → region → component. No dead regions. |
| **4 — Good** | All critical regions are justified. One or two secondary regions are thinly justified but harmless. |
| **3 — Adequate** | Most regions are plausible, but traceability is implicit. Reviewer can infer why they exist, but the wireframe does not state it. |
| **2 — Poor** | Several regions exist because they are common dashboard/app patterns, not because the task requires them. |
| **1 — Failing** | Wireframe is a generic template. Regions cannot be traced to the product intent. |

**Test**: pick any box in the wireframe. Ask: "what user decision, task, or data/action group requires this region?" If the answer is unclear, the region is suspect.

---

### Dimension 2 [gate] — Structural hierarchy clarity

Does the wireframe make layout hierarchy and containment unambiguous?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Parent/child containment is obvious. Persistent vs. page-local regions are distinct. Nesting, adjacency, and dominance are clear. A component tree can be derived without guesswork. |
| **4 — Good** | Hierarchy is mostly clear. One or two ambiguous relationships require a note. |
| **3 — Adequate** | The overall shape is understandable, but several relationships require interpretation. |
| **2 — Poor** | The diagram contains boxes but does not clearly show containment or ownership. Reviewers disagree on the intended structure. |
| **1 — Failing** | ASCII art is decorative. It does not encode useful hierarchy. |

**Test**: ask a second agent to produce a component tree from the wireframe. If it produces a materially different hierarchy from the author’s intent, the wireframe failed.

---

### Dimension 3 [gate] — Interaction ownership

Does the wireframe identify who owns focus, selection, navigation, dismissal, and primary actions?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | All interactive regions have ownership annotations. Focus movement, dismissal, selection, routing, and mutation ownership are explicit where relevant. |
| **4 — Good** | Primary interaction ownership is clear. Secondary controls may lack annotations but are low risk. |
| **3 — Adequate** | Interaction surfaces are shown, but ownership is mostly inferred from labels. |
| **2 — Poor** | Controls exist with no focus, selection, or action ownership. Implementation will have to invent behavior. |
| **1 — Failing** | Static layout only. No interaction model. |

**Test**: for every `[Control]`, ask: "what owns its state, what happens on activation, and where does focus go next?" Missing answers indicate an ownership gap.

---

### Dimension 4 [gate] — State coverage

Does the wireframe represent meaningful non-default states?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every data-driven region includes loading, empty, and error states. Stateful regions include expanded/collapsed/selected/disabled states where structurally relevant. |
| **4 — Good** | Critical data-driven states are represented. Some secondary states are deferred explicitly. |
| **3 — Adequate** | One or two state variants shown, but coverage is incomplete. |
| **2 — Poor** | Default state only. Missing states will materially affect implementation. |
| **1 — Failing** | Wireframe implies a happy path only. Real-world data or error conditions are absent. |

**Test**: list every data-driven region. For each, find `{loading}`, `{empty}`, and `{error}` or an explicit reason that the state is out of scope.

---

### Dimension 5 [gate] — Responsive decomposition

Does the wireframe specify what happens across meaningful layout constraints?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Wide, medium, and narrow structures are represented or explicitly scoped. Collapse/stack/sheet/modal behavior is clear. Scroll and navigation ownership remain valid across breakpoints. |
| **4 — Good** | Primary responsive changes are shown. Some low-risk details deferred. |
| **3 — Adequate** | Responsive behavior is described in prose but not diagrammed. |
| **2 — Poor** | Desktop structure only, despite obvious responsive risk. |
| **1 — Failing** | Wireframe implies a structure that cannot reasonably adapt to smaller widths. |

**Test**: take the widest row or densest region. Ask what happens at narrow width. If the answer requires invention, responsive decomposition is incomplete.

---

### Dimension 6 [review] — Density and information priority

Does the wireframe communicate visual/information priority without pretending to be final design?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Region size and placement communicate priority. Critical decisions/actions occupy dominant positions. Secondary content is clearly subordinate. Density is intentional and annotated where needed. |
| **4 — Good** | Priority is mostly clear. One or two regions may compete visually but the intended hierarchy is recoverable. |
| **3 — Adequate** | All content is present, but priority is flat. Reviewer can understand structure but not importance. |
| **2 — Poor** | Dense areas are packed without hierarchy. The wireframe hides prioritization problems. |
| **1 — Failing** | Everything appears equally important. The artifact cannot guide layout or implementation decisions. |

**Test**: ask what the user should look at first, second, and third. If the wireframe cannot answer, priority is underspecified.

---

### Dimension 7 [review] — Semantic component mapping

Can the wireframe be converted into a component plan without losing intent?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Semantic component boundaries are either annotated directly or derivable without ambiguity. State/data/action ownership maps to the proposed component tree. |
| **4 — Good** | Most components are derivable. A few boundaries require implementation judgment. |
| **3 — Adequate** | Component mapping is possible but not stable; different agents may choose different boundaries. |
| **2 — Poor** | Wireframe is layout-only. Componentization is left to downstream invention. |
| **1 — Failing** | Wireframe cannot be mapped to a plausible implementation structure. |

**Test**: ask two agents to produce component maps from the same wireframe. If their maps disagree on state-owning components, the wireframe needs clearer semantics.

---

### Dimension 8 [review] — Annotation discipline

Are annotations concise, consistent, and load-bearing?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Annotations use a stable grammar. Every annotation changes implementation or review behavior. Unknowns and risks are marked explicitly. |
| **4 — Good** | Mostly consistent notation. A few prose notes, but not enough to reduce clarity. |
| **3 — Adequate** | Notes are useful but inconsistent. Agents can still interpret them with effort. |
| **2 — Poor** | Annotations are verbose, inconsistent, or mostly decorative. The wireframe becomes a prose doc wrapped around ASCII. |
| **1 — Failing** | No annotation system. Important constraints are absent or buried outside the wireframe. |

**Test**: remove all annotations. Which implementation decisions become impossible or ambiguous? If none, the annotations were decorative. If many, check whether the notation is consistent enough to preserve them.

---

### Dimension 9 [gate] — Reviewability and diffability

Can the wireframe be reviewed, changed, and compared in a normal agent/code workflow?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Wireframe is stable plain text, line-wrapped, versionable, and diffable. Structural changes appear as small diffs. Review comments can target specific lines. |
| **4 — Good** | Mostly diffable. Some wide diagrams or alignment changes create noisy diffs. |
| **3 — Adequate** | Reviewable by humans, but diffs are noisy. Changes often require re-reading the whole diagram. |
| **2 — Poor** | Wireframe is hard to diff because of excessive spacing, decoration, or full redraws. |
| **1 — Failing** | Artifact is not useful in text review. It behaves like an image, not a structured text artifact. |

**Test**: make one structural change. Does the diff show that change cleanly, or does the whole diagram churn?

---

### Dimension 10 [review] — Appropriate fidelity

Is the wireframe detailed enough for the next decision, but not so detailed that it collapses later phases?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Fidelity matches risk. Structural questions are answered; visual styling is deferred. The artifact is no larger than needed. |
| **4 — Good** | Slightly more detail than necessary, but not harmful. |
| **3 — Adequate** | Some over-detailing or under-detailing. Still useful but not optimally scoped. |
| **2 — Poor** | Either too vague to implement or too visual to preserve optionality. |
| **1 — Failing** | Wireframe is the wrong artifact for the question being asked. |

**Test**: identify the next downstream action. Does the wireframe contain exactly what that action needs? Missing information is under-fidelity. Styling/detail irrelevant to the action is over-fidelity.

---

## §Operating Procedure

### Phase 1 — Derive before drawing

Before producing ASCII, the agent should state:

```txt
intent
primary user
primary task
critical decisions
main data groups
main actions
known constraints
```

If those are unknown, the wireframe will encode guesses as structure.

### Phase 2 — Choose the wireframe level

Select the smallest useful level:

```txt
region wireframe       → layout problem
interaction wireframe  → flow/focus/action problem
state wireframe        → data and feedback problem
responsive wireframe   → adaptation problem
component wireframe    → implementation decomposition problem
```

Do not generate all levels by default. Generate what the task needs.

### Phase 3 — Draw the default structure

Start with the dominant structure:

```txt
persistent regions
page-local regions
primary task area
secondary/supporting regions
action surfaces
```

Avoid visual styling. Labels should be semantic.

### Phase 4 — Annotate ownership

Add only load-bearing annotations:

```txt
scroll owner
focus owner
state owner
data owner
action owner
responsive behavior
unresolved risks
```

### Phase 5 — Add states

For each data-driven or interactive region, add state variants when they alter structure or available actions.

### Phase 6 — Add responsive decomposition

Represent wide/medium/narrow variants when responsive behavior is part of the task or likely to create implementation risk.

### Phase 7 — Review as a gate

Before generating visual design or implementation, review:

```txt
does every region trace to intent?
does every interaction have ownership?
does every data region have states?
does responsive behavior hold?
can a component tree be derived?
```

Only then proceed.

---

## §Prompt Patterns

### Prompt: produce a region wireframe

```txt
Create an ASCII region wireframe for this UI.

Do not style it.
Do not choose colors, typography, or final spacing.
Show persistent regions, page-local regions, primary actions, and scroll ownership.
Annotate unresolved structural questions with !.
```

### Prompt: produce an interaction wireframe

```txt
Create an ASCII interaction wireframe for this flow.

Show triggers, transitions, focus movement, dismissal behavior, and resulting state.
Use arrows for flow.
Annotate ownership with [owns: ...].
Do not generate implementation code yet.
```

### Prompt: produce responsive variants

```txt
Create wide, medium, and narrow ASCII wireframes.

For each variant, show what persists, what collapses, what becomes a sheet/modal, and what owns scrolling.
Do not assume the desktop layout simply stacks unless that is structurally justified.
```

### Prompt: review a wireframe

```txt
Review this ASCII wireframe as a structural artifact.

Score:
1. intent-to-structure traceability
2. hierarchy clarity
3. interaction ownership
4. state coverage
5. responsive decomposition
6. component mapping

Return critical gaps before minor polish.
```

### Prompt: convert wireframe to component plan

```txt
Convert this ASCII wireframe into a semantic component map.

Preserve region ownership.
Identify state owners, data owners, action owners, and scroll owners.
Do not introduce components that are not implied by the wireframe.
```

---

## §Multi-Agent Workflow

ASCII wireframes are useful coordination artifacts in multi-agent UI implementation.

A recommended division:

```txt
orchestrator agent
  → derives product intent and task decomposition
  → creates or requests the wireframe
  → reviews structure
  → splits implementation tasks by region/component ownership

wireframe agent
  → produces region/interaction/state/responsive wireframes
  → marks unresolved structural risks

design-system agent
  → maps wireframe regions to existing primitives and patterns
  → identifies missing components or token needs

implementation agents
  → implement assigned regions/components
  → preserve ownership boundaries from the wireframe

review agent
  → checks implementation against the wireframe and acceptance criteria
```

The key rule:

```txt
Do not assign implementation tasks until ownership boundaries are stable.
```

If component ownership is unclear in the wireframe, it will be worse in code.

---

## §Output Contract

A complete ASCII wireframe artifact should contain:

```yaml
intent: string
scope: region | interaction | state | responsive | component | mixed
known_inputs:
  - string
assumptions:
  - string
wireframes:
  - name: string
    diagram: text
annotations:
  ownership:
    - region: string
      owns: string[]
  states:
    - region: string
      variants: string[]
  responsive:
    - breakpoint: string
      behavior: string
risks:
  - string
open_questions:
  - string
component_mapping:
  - region: string
    component_candidate: string
    ownership: string[]
validation:
  passed: boolean
  issues:
    - severity: critical | major | minor
      finding: string
      suggested_fix: string
```

A smaller artifact can omit irrelevant fields, but the missing fields should be intentional.

---

## §Anti-patterns

### AP-01 — ASCII art as decoration

**Symptom**: the diagram is visually elaborate but structurally thin. It looks impressive but does not clarify hierarchy, ownership, or state.

**Root cause**: treating wireframing as presentation rather than reasoning.

**Correction**: reduce decoration. Add semantic labels, ownership annotations, and state boundaries.

---

### AP-02 — Pixel-thinking

**Symptom**: the agent spends effort aligning boxes, simulating shadows, or approximating final spacing.

**Root cause**: visual fidelity was mistaken for structural fidelity.

**Correction**: use coarse spatial relationships. Preserve visual decisions for the design phase.

---

### AP-03 — Generic dashboard skeleton

**Symptom**: the wireframe contains header, sidebar, KPI cards, chart, and table regardless of the actual task.

**Root cause**: pattern matching from prompt vocabulary to common layout templates.

**Correction**: force traceability from user decisions and data/action groups to regions.

---

### AP-04 — Missing state surfaces

**Symptom**: only the happy path is wireframed. Loading, empty, error, permission, and collapsed states are omitted.

**Root cause**: state was treated as implementation detail.

**Correction**: require states for every data-driven region before implementation.

---

### AP-05 — Ambiguous ownership

**Symptom**: controls are visible, but it is unclear who owns focus, selection, route changes, or mutation state.

**Root cause**: wireframe encodes shape but not behavior.

**Correction**: add ownership annotations to interactive regions and controls.

---

### AP-06 — Desktop-only false confidence

**Symptom**: a wide wireframe looks reasonable, but the layout has no narrow or medium strategy.

**Root cause**: responsive behavior was deferred despite being structurally relevant.

**Correction**: add responsive variants or mark responsive behavior as unresolved risk.

---

### AP-07 — Component collapse too early

**Symptom**: the agent names detailed components before validating layout and interaction structure.

**Root cause**: implementation vocabulary entered before spatial reasoning stabilized.

**Correction**: keep early wireframes semantic and regional. Map to components after review.

---

### AP-08 — Prose pretending to be wireframe

**Symptom**: the artifact is mostly explanatory prose with a small diagram. The spatial relationships remain unclear.

**Root cause**: the agent avoided committing to structure.

**Correction**: make the diagram the primary artifact. Use prose only for annotations and unresolved questions.

---

### AP-09 — Undiffable redraws

**Symptom**: every change redraws the whole wireframe, making review impossible.

**Root cause**: excessive alignment dependence and decorative spacing.

**Correction**: use stable, simple layouts and line-oriented annotations.

---

### AP-10 — Implementation drift from wireframe

**Symptom**: implementation agents ignore the wireframe and invent different ownership boundaries.

**Root cause**: wireframe was not a gate or output contract; it was reference material.

**Correction**: require implementation review against wireframe regions, ownership, and state coverage.

---

## §Hard Tests

1. **The region justification test**: choose every major region in the diagram. For each, identify the upstream task, decision, data group, or action group that requires it. Any unjustified region is a candidate for deletion.

2. **The second-agent component test**: hand the wireframe to a separate agent and ask it to derive a component tree. Compare to the intended component tree. Major differences mean hierarchy or ownership is underspecified.

3. **The focus test**: for every interactive surface, ask where focus starts, how it moves, how it exits, and what happens after action. Missing answers indicate interaction ownership gaps.

4. **The state test**: list every data-driven region. Confirm loading, empty, and error states are present or explicitly out of scope.

5. **The responsive collapse test**: take the densest wide layout and reduce it to narrow width. What stacks, hides, becomes a sheet, or becomes modal? If the answer is invented during review, the wireframe is incomplete.

6. **The dead-region test**: remove a region. Does any task, decision, or action become impossible? If not, the region was not justified.

7. **The diff test**: make one structural change and inspect the text diff. If most lines change, the wireframe is too fragile for agent/code review workflows.

8. **The implementation handoff test**: give the wireframe to an implementation agent without additional explanation. Can it produce a component plan that preserves ownership, states, and responsive behavior? If not, the artifact is not handoff-safe.

9. **The visual-collapse test**: scan the wireframe for color, typography, styling, and animation decisions. If those decisions are present before structural review, the artifact has collapsed too far downstream.

10. **The review-gate test**: identify at least one decision that could change after reviewing the wireframe. If no decision could change, the wireframe is not functioning as a gate.

---

## §Example: Good vs. Poor Wireframe

### Poor

```txt
+------------------------------------------------+
| Dashboard                                      |
+------------------------------------------------+
| Cards Cards Cards                              |
| Chart                                          |
| Table                                          |
+------------------------------------------------+
```

Problems:

```txt
no user task
no region ownership
no state model
no responsive behavior
no action surfaces
no semantic hierarchy
```

### Better

```txt
Intent: Help sales ops identify leads at risk and act before SLA breach.

WIDE
+--------------------------------------------------------------------------------+
| TopNav [owns: global-search user-menu]                                         |
+------------------+-------------------------------------------------------------+
| Sidebar          | Lead Operations                                             |
| [owns: nav]      |                                                             |
|                  | +----------------------+ +--------------------------------+ |
|                  | | SLA Risk Summary      | | Recommended Actions           | |
|                  | | {loading empty error} | | [owns: mutation queue]         | |
|                  | +----------------------+ +--------------------------------+ |
|                  |                                                             |
|                  | +---------------------------------------------------------+ |
|                  | | Lead Queue [owns: filters selection scroll]              | |
|                  | | [Filter] [Sort] [Bulk assign]                            | |
|                  | | Row...                                                   | |
|                  | +---------------------------------------------------------+ |
+------------------+-------------------------------------------------------------+

NARROW
+--------------------------------------------------------------------------------+
| TopBar [Menu] Lead Operations [Search]                                         |
+--------------------------------------------------------------------------------+
| SLA Risk Summary                                                               |
| Recommended Actions                                                            |
| Lead Queue [scroll: page]                                                      |
| Inspector opens as full-screen sheet                                           |
+--------------------------------------------------------------------------------+

! risk: bulk actions need permission model
! unresolved: should Recommended Actions persist above queue on narrow?
```

This version encodes intent, hierarchy, ownership, states, responsive behavior, risks, and open questions. It is still not visual design. That is the point.

---

## §Best-Practice Summary

A strong ASCII wireframe is:

```txt
semantic, not decorative
structural, not visual
diffable, not image-like
annotated, not verbose
state-aware, not happy-path-only
responsive, not desktop-only
handoff-safe, not author-dependent
```

The highest-value rule:

> Generate ASCII wireframes before visual design or implementation when the UI has meaningful layout, state, interaction, or responsive risk.

The second highest-value rule:

> Treat the wireframe as a gate. If downstream implementation can ignore it without failing review, it was not a contract.
