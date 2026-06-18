---
date: 2026-05-31
status: research-verified
coverage: canonical
version: "1.0.0"
primary_sources:
  - "Bertrand Meyer (1988). Object-Oriented Software Construction. Prentice Hall."
  - "Steve Yegge (2011). Stevey's Google Platforms Rant. https://gist.github.com/chitchcock/1281611"
  - "Wang et al. (2025). SoK: Agentic Skills — Beyond Tool Use in LLM Agents. arXiv:2602.20867"
  - "Zhang et al. (2025). Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward. arXiv:2602.12430"
  - "Liu et al. (2026). Skilldex: A Package Manager and Registry for Agent Skill Packages with Hierarchical Scope-Based Distribution. arXiv:2604.16911"
  - "Chen et al. (2025). SkillOps: Managing LLM Agent Skill Libraries as Self-Maintaining Software Ecosystems. arXiv:2605.13716"
  - "Peng et al. (2025). ToolRegistry: A Protocol-Agnostic Tool Management Library for Function-Calling LLMs. arXiv:2507.10593"
  - "Anthropic (2025). Building Effective Agents. https://www.anthropic.com/engineering/building-effective-agents"
  - "AIQuinta (2025). Versioning Agent Skills: SemVer, Compatibility, Deprecation. https://aiquinta.ai/blog/versioning-agent-skills-semver-compatibility-deprecation/"
---

# What Is Extensibility? — Foundational Knowledge Document

## The Core Claim

Extensibility in agentic LLM systems is the property that allows new capabilities to be added — new skills, tools, workflows, rubrics, evals — without requiring modification of existing, working components. This is Bertrand Meyer's Open-Closed Principle applied to systems that are non-deterministic by nature: every unit of capability must be designed as a stable interface that others can build on top of, not through. The fundamental insight is that the cost of extension should be proportional to the scope of new behavior, not to the age or size of the existing library.

The practical implication is severe: in LLM skill systems, extensibility is not a nice-to-have architectural virtue. It is the difference between a library that compounds value over time and one that collapses under its own weight. Because skills influence agent behavior through natural language descriptions — not typed contracts — the failure mode is silent. A new skill with an overlapping description does not throw an exception; it splits the agent's decision surface and degrades routing precision for every other skill in the library. An un-versioned interface change does not fail at compile time; it fails at runtime in a production workflow, invisibly. Extensibility discipline is the engineering practice that keeps this entropy at bay.

---

## The Open-Closed Principle Applied to Agent Systems

Meyer's 1988 formulation remains the correct anchor: "Software entities should be open for extension, but closed for modification." A module is open if it can be extended — new behavior added, new fields attached, new invocations wired in. A module is closed if its public interface is stable enough for other modules to depend on without requiring those dependents to change when internals evolve.

For LLM skill libraries, this translates to three concrete requirements:

**Closed interface = stable triggering contract.** A skill's `description` field in SKILL.md and `skill.json` is its public interface. The description tells the agent when to invoke the skill. Changing the description semantics — even without changing the underlying behavior — is a breaking change, because it alters which tasks route to this skill and which don't. The description must be treated with the same rigor as a public API signature.

**Open implementation = internal evolution without downstream impact.** The skill's references, scripts, and step-by-step instructions can evolve without signaling a breaking change, provided the triggering contract and output shape remain stable. Adding a new reference document, refining an execution step, or improving a rubric dimension are all patch-level changes.

**Composition not modification.** When a new capability is needed that overlaps with an existing skill, the correct response is to introduce a new, narrower skill — not to expand the existing one. Expanding a skill's scope is the cardinal extensibility violation: it changes the routing surface for all existing callers while adding capability for one new use case. Compose via the hierarchy (meta-skill → skill → tool); never mutate the stable boundary.

Yegge's platform rant makes the organizational corollary explicit: "You can't keep launching products and pretending you'll turn them into magical beautiful extensible platforms later; you have to start with a platform and then use it for everything." The Golden Rule for skill libraries is identical — every skill must be authored as a first-class library citizen from day one, not retrofitted into one after it has grown.

---

## Composability: The LEGO Architecture

Composability is the structural twin of extensibility. Where extensibility asks "can new capabilities be added without breaking existing ones?", composability asks "can existing capabilities be combined to produce novel behavior without building from scratch?"

The research survey by Wang et al. (SoK: Agentic Skills, 2025) formalizes the composability hierarchy. They define a skill formally as a four-tuple **S = (C, π, T, R)**:

- **C** (Applicability Condition): predicate over observations and current goal — when this skill applies
- **π** (Executable Policy): the actionable mechanism — what the skill does
- **T** (Termination Condition): when the skill has completed, successfully or not
- **R** (Reusable Interface): metadata and callable signature — how others invoke this skill

This formalization reveals the composability mechanism: skills compose vertically through hierarchies because one skill's **R** (interface) can satisfy another skill's **C** (applicability condition) when the output of the first becomes the precondition of the second. High-level skills invoke mid-level skills; mid-level skills invoke atomic tools. This mirrors reinforcement learning's options framework, where macro-actions are themselves composed of micro-actions.

The practical design pattern is **progressive disclosure** — the defining architectural insight of 2025-era skill systems. Zhang et al. (Agent Skills for LLMs, 2025) describe a three-level information loading model:

1. **Level 1 (Metadata)**: Only the SKILL.md frontmatter — name and description, dozens of tokens — loads at agent startup. This is the skill's triggering contract.
2. **Level 2 (Instructions)**: Full procedural guidance loads only when the skill is selected for execution.
3. **Level 3 (Resources)**: Technical scripts, appendices, and reference documents load on-demand within execution.

This architecture is what makes library-scale composability tractable. Without it, loading 73 skills at startup would consume tens of thousands of tokens on every agent invocation, regardless of which skills are needed. Progressive disclosure decouples discovery cost (near-zero) from execution cost (proportional to task complexity).

LangChain and LangGraph operationalize composability at the workflow level. LangGraph adds a graph abstraction for stateful multi-agent apps with explicit fork/join nodes, allowing independent subgraphs to execute concurrently subject to data dependencies. The key design property: because graphs are composable, LangChain agents created with high-level APIs can be dropped directly into custom LangGraph workflows as nodes — the abstraction levels interlock without forcing a choice between them.

AutoGen v0.4 takes the same pattern to the framework level through a three-layer architecture: Core (foundational event-driven primitives), AgentChat (high-level task-driven API), and Extensions (third-party integrations). Each layer is independently extensible — you can add a new extension without touching Core, or build a custom Core-level agent without disrupting the AgentChat surface. The event-driven, asynchronous communication model is the key — agents interact through messages, not direct calls, which means any agent can be swapped or extended without changing the agents it communicates with.

---

## Version Management: Semantic Versioning for Non-Deterministic Capabilities

Standard semantic versioning (major.minor.patch) applies to skill libraries, but with an LLM-specific wrinkle: the "interface" that other components depend on is partially semantic, not purely structural. A skill's description is part of its public API. Changing the description significantly — even without changing the behavior — constitutes a breaking change because it alters what the agent routes to this skill.

The versioning contract for skills (per AIQuinta, 2025):

**MAJOR bump — breaking changes:**

- Removing an existing parameter, renaming a required field, or changing a data type
- Restructuring output format in ways that break downstream parsing
- Semantic shifts in description that alter routing behavior (the LLM will invoke this skill in different scenarios)
- Removing a skill from the active registry

**MINOR bump — backward-compatible additions:**

- Adding new optional fields to the input schema with sensible defaults
- Expanding output payloads with new keys while preserving the existing structure
- Capability upgrades that handle legacy inputs identically

**PATCH bump — internal refinements:**

- Editing the description for concision without semantic change
- Performance optimization without interface changes
- Adding or improving reference documents
- Security hardening that doesn't break valid inputs

The non-deterministic challenge: modifying a description so that the LLM triggers the skill in meaningfully different scenarios constitutes a breaking change — but this judgment requires human review, not mechanical detection. This is why the AIQuinta framework mandates "HITL testing before classification": description changes must be evaluated against a routing corpus (set of representative task descriptions) to determine whether routing behavior has shifted before assigning a version bump level.

The research from NTU on versioning LLM-agent-based software identifies three components that must be versioned together: the semantic description, the input schema, and the output payload. Versions for all three must be tracked in sync. A version skew between description and schema — where the description implies capabilities the schema doesn't support, or vice versa — is a latent defect that surfaces unpredictably at runtime.

For skill libraries, the practical recommendation is: treat the `version` field in `skill.json` as load-bearing infrastructure, not decorative metadata. Every change to a skill that any other skill or workflow depends on requires a version assessment and an explicit CHANGELOG entry.

---

## The Skill Stewardship Loop: Evidence-Driven Evolution

Extensibility is not a static property — it must be maintained actively over a library's lifetime. The research consensus converges on a continuous stewardship loop that prevents capability creep, skill rot, and description drift. The loop has six phases:

**1. Observe**: Collect execution signals — utility logs, failure traces, body-hash collisions (identical implementations under different names), type mismatches at skill boundaries. SkillOps (Chen et al., 2025) demonstrates this can be done with nearly zero LLM calls at library time by relying on rule-based diagnosis over observable signals rather than semantic reasoning.

**2. Classify**: Diagnose health across five dimensions — utility (success rate of recent task calls), redundancy (cluster size of equivalent skills), compatibility (fraction of dependency edges also satisfying interface compatibility), failure-risk (empirical failure rate), and validation-gap (whether correctness validators exist). Each skill receives a health score.

**3. Place**: For new proposed skills, determine the correct scope level — global capability (cross-project), shared team convention, or project-specific customization. Skilldex's three-tier hierarchy (global → shared → project) with local-first precedence prevents scope pollution: a project-level skill overrides but does not contaminate the global or shared tiers.

**4. Verify**: Before promoting a skill from draft to stable, validate the format (YAML validity, description length, required fields, file structure), test routing on a representative corpus, and run behavioral evals. Skilldex implements a 0–100 conformance score across eight empirical checks — informational but not blocking, respecting author autonomy while surfacing quality signals.

**5. Monitor**: Track skill performance post-promotion. Detect drift — the accumulation of capability degradation without obvious failure signals. Self-evolving agents often experience non-monotonic capability changes where adapting to new task distributions degrades previously acquired capabilities (per the "Do Self-Evolving Agents Forget?" research, 2025). ContractGraph-Propagated Diagnosis (CGPD) in SkillOps preemptively flags downstream skills that inherit upstream risk.

**6. Prune / Promote / Mechanize**: Apply one of six typed maintenance actions — merge (collapse redundant skill pairs), retire (remove consistently failing skills), repair (rewrite using execution feedback), add_validator (insert missing correctness checks), add_adapter (create type-conversion shims for interface mismatches), or instantiate (bind task-specific arguments to parameterized skills). Promotion from draft → stable requires passing the verification gate. Mechanization means converting a human-reviewed practice into an automated gate in the validation pipeline.

This loop is the operationalization of the observe → evidence → action discipline that prevents a living skill library from degrading into an undifferentiated mass of overlapping, under-maintained capabilities.

---

## Extension Failure Modes

The four canonical failure modes of extensible agent systems:

**Capability creep**: Skills accumulate scope over time as maintainers add edge cases rather than creating new, narrower skills. The symptom is a skill whose description has grown to cover three distinct use cases, with routing ambiguity between all of them. The fix is decomposition — split into focused skills and let the routing mechanism do its job. Wang et al.'s empirical finding is striking: "skill selection accuracy degrades sharply beyond optimal library sizes" — there is a phase transition where adding more skills to a library begins actively harming routing precision.

**Description drift**: The description diverges from the actual implementation as behavior evolves through patch updates. The description implies the skill handles cases it no longer handles, or misses cases it now covers. This is an LLM-specific failure mode absent from typed systems — the natural language interface degrades silently. The remediation is treating description changes as first-class engineering work, not documentation cleanup.

**Version conflicts**: Multiple versions of a skill coexist in a library without explicit coordination — one workflow expects v1 output structure, another expects v2. The 60% production agent failure rate attributed to tool versioning (per 2025 industry data) reflects this failure mode. The prevention is strict semantic versioning with an explicit deprecation lifecycle: tag → monitor telemetry → soft-deprecate (warnings in output) → hard-deprecate (descriptive errors with recovery paths).

**Skill rot**: Skills accumulate in a library without maintenance — low utility, missing validators, stale implementations. SkillOps found that without active maintenance, retrieval baselines degrade significantly under larger, noisier libraries, while the SkillOps-maintained library remains stable as it grows from 200 to 2000 skills (79.5% → 83.8% task success). Skill rot is not a failure of authoring quality; it is a failure of lifecycle governance.

**Supply-chain risk**: The ClawHavoc attack documented by Wang et al. compromised ~1,200 malicious skills in a public marketplace, exfiltrating API keys and credentials. Marketplace distribution (Pattern-7 in the SoK taxonomy) introduces provenance verification requirements that file-system-local skill libraries avoid. Trust tiers — Tier-1 (metadata only) through Tier-4 (autonomous execution within permission boundaries) — are the governance mechanism.

---

## The Tool Registry Pattern: Protocol-Agnostic Extensibility

The ToolRegistry pattern (Peng et al., 2025) operationalizes open-closed design at the tool integration level. The core abstraction is a single `Tool` class with a stable unified interface: name, description, parameter schema, callable implementation, and metadata. Protocol-specific adapters — for MCP, OpenAPI, LangChain, native Python — each handle source-specific communication, authentication, and schema conversion, but present an identical Tool interface to the consuming agent.

This is the adapter pattern applied to solve the extensibility problem at the tool layer. Adding support for a new tool protocol requires implementing a new adapter class — it does not require modifying the core Tool abstraction or any existing adapters. The empirical benefit is substantial: 60-80% code reduction in tool integration versus manual implementations, with 1.8-3.1x throughput improvements through concurrent execution optimization.

The Anthropic Advanced Tool Use release (November 2025) extends this with a Tool Search Tool enabling programmatic discovery of relevant tools from large registries, reducing token overhead by up to 85% at scale. This is the progressive-disclosure pattern applied at the tool layer: the full tool library is available but only descriptions are loaded at startup; specific tools are fetched into context when selected.

---

## Implications for This Skill Library

This knowledge document maps directly to several existing gates and practices in the skill library's governance model.

**[gate] Format conformance is the closed interface.** The validation checklist — name matching, description ≤1024 chars, semver version, files[] completeness, ROADMAP.md three-section structure — enforces the stable interface contract. These are not bureaucratic requirements; they are the conditions under which other skills and workflows can depend on a skill without fragility.

**[gate] Version bump assessment before merge.** The CHANGELOG.md requirement for every version change enforces the versioning contract. A skill change that lacks a CHANGELOG entry is evidence of an unassessed interface change — it may be a breaking change that routes incorrectly in existing workflows.

**[review] ROADMAP.md as the deferred-scope container.** The three-section ROADMAP (Planned / Deferred / Out of scope) operationalizes the open-closed principle organizationally. Scope that belongs in a future version goes in Planned — it does not get added to the current skill's description. Scope that is explicitly excluded goes in Out of scope — preventing capability creep by documenting the boundary. Without this container, deferred scope accumulates in CHANGELOG comments, SKILL.md footnotes, and conversation context — all of which silently widen the skill's triggering surface.

**[hypothesis] Progressive disclosure reduces cold-start cost.** The three-level loading architecture (metadata at startup, instructions on trigger, resources on demand) is validated by the research. The skill library's current naming convention and description discipline implements Level 1 correctly. The question for measurement is whether Level 2 (instruction loading on trigger) is consistently scoped — skills whose full SKILL.md is too large to load efficiently in practice should be decomposed into narrower skills.

**[gate] §SelfAudit before promotion.** The SelfAudit pattern in SKILL.md — where a skill asserts its own compliance before reporting results — implements the Verify phase of the stewardship loop. It catches description drift, missing validators, and version skew at the source, before they propagate through dependent workflows.

**[review] Skillset coherence for related skills.** Skilldex's skillset abstraction — bundling related skills with shared vocabulary files stored at the skillset root — solves the implicit drift problem for skills that reference the same concepts. In this library, skills in the `ui-compose-*` family and the `plan-*` family share implicit vocabulary; a shared `references/` document owned by a skillset would prevent them from drifting apart silently.

**[hypothesis] The Skill Contract model for high-value skills.** SkillOps's (P,O,A,V,F) contract — preconditions, operations, artifacts, validators, failure modes — is a more rigorous version of what typed skills already implement through `schemas/input.json`, `schemas/output.json`, and the `## Typed Interface` section in SKILL.md. Extending the SKILL.md template to explicitly document known failure modes (the F component) would make the stewardship loop's repair and retire decisions more systematic.

---

## Source Citations

1. Bertrand Meyer (1988). _Object-Oriented Software Construction_. Prentice Hall. The origin of the Open-Closed Principle: "Software entities should be open for extension, but closed for modification."

2. Steve Yegge (2011). Stevey's Google Platforms Rant. https://gist.github.com/chitchcock/1281611 — The "Golden Rule of Platforms": start with extensible platform architecture from day one; retrofitting always costs 10x more.

3. Wang et al. (2025). SoK: Agentic Skills — Beyond Tool Use in LLM Agents. arXiv:2602.20867. https://arxiv.org/html/2602.20867v1 — Formal four-tuple definition S=(C,π,T,R); seven design patterns; five acquisition modes; four trust tiers; seven lifecycle stages; SkillsBench empirical finding: curated skills +16.2pp, self-generated skills -1.3pp.

4. Zhang et al. (2025). Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward. arXiv:2602.12430. https://arxiv.org/html/2602.12430v3 — Three-level progressive disclosure architecture; skill selection accuracy phase transition at optimal library size; MCP/skill orthogonality.

5. Liu et al. (2026). Skilldex: A Package Manager and Registry for Agent Skill Packages with Hierarchical Scope-Based Distribution. arXiv:2604.16911. https://arxiv.org/html/2604.16911v1 — Three-tier hierarchy (global/shared/project); format conformance scoring (0-100, eight empirical checks); skillset abstraction for shared-asset coherence.

6. Chen et al. (2025). SkillOps: Managing LLM Agent Skill Libraries as Self-Maintaining Software Ecosystems. arXiv:2605.13716. https://arxiv.org/html/2605.13716v1 — Skill Contract (P,O,A,V,F); HSEG with four typed edge types; five-dimensional health scoring; six maintenance operations; 79.5% task success vs +8.8pp over baseline; stable at 200-2000 skill scale; maintenance cost ~$0.0003 per pass.

7. Peng et al. (2025). ToolRegistry: A Protocol-Agnostic Tool Management Library for Function-Calling LLMs. arXiv:2507.10593. https://arxiv.org/html/2507.10593v2 — Adapter pattern for protocol-agnostic tool integration; unified Tool abstraction; 60-80% code reduction; 2.4-4.5x throughput improvement.

8. Anthropic (2025). Building Effective Agents. https://www.anthropic.com/engineering/building-effective-agents — Composability over complexity; progressive disclosure through skills; tool documentation as first-class engineering; Goldilocks Zone system prompt discipline.

9. Anthropic / AWS re:Invent (2025). What Anthropic Learned Building AI Agents in 2025 (AIM277). https://dev.to/kazuya_dev/aws-reinvent-2025-what-anthropic-learned-building-ai-agents-in-2025-aim277-16lc — Progressive skill disclosure in production; tool disambiguation; sub-agent composition for context efficiency; failure of over-specification.

10. AIQuinta (2025). Versioning Agent Skills: SemVer, Compatibility, Deprecation. https://aiquinta.ai/blog/versioning-agent-skills-semver-compatibility-deprecation/ — MAJOR/MINOR/PATCH bump criteria for skills; description semantic change as breaking change; four-phase deprecation lifecycle; HITL testing requirement for routing classification.
