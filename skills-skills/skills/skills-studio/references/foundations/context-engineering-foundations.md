---
date: 2026-05-31
status: research-verified
coverage: canonical
version: "1.0.0"
primary_sources:
  - "Anthropic Engineering (2025). Effective Context Engineering for AI Agents. anthropic.com/engineering/effective-context-engineering-for-ai-agents"
  - "Willison, Simon (2025). Context Engineering. simonwillison.net/2025/jun/27/context-engineering/"
  - "LangChain (2025). Context Engineering for Agents. langchain.com/blog/context-engineering-for-agents"
  - "Schmid, Philipp (2025). The New Skill in AI is Not Prompting, It's Context Engineering. philschmid.de/context-engineering"
  - "Paulsen et al. (2025). The Maximum Effective Context Window for Real-World Tasks. arXiv:2509.21361"
  - "Morph (2025). Context Rot: Why LLMs Degrade as Context Grows. morphllm.com/context-rot"
  - "Alzahrani et al. (2025). Contextual Drag: How Errors in the Context Affect LLM Reasoning. arXiv:2602.04288"
  - "Chatterjeesaurabh et al. (2024). Contextual RAG System with Hybrid Search and Reranking. analyticsvidhya.com/blog/2024/12/contextual-rag-systems"
  - "Peng et al. (2025). Agentic Context Engineering: Evolving Contexts for Self-Improving LLMs. arXiv:2510.04618"
  - "Zou et al. (2025). PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation. USENIX Security 2025"
---

# What Is Context Engineering? — Foundational Knowledge Document

## The Core Claim

In agentic LLM systems, behavior is determined less by the model than by the context surface constructed around it. The task framing, user intent, retrieved knowledge, tool affordances, intermediate state, constraints, examples, prior decisions, and output schemas — together these form the context that the model reasons over. Swap a weaker model into a well-engineered context and it often outperforms a stronger model in a poorly-engineered one. This is the central empirical finding of the field: the model is not the locus of reliability. The context is.

Context engineering is therefore the discipline of selecting, structuring, compressing, retrieving, and presenting intentional context so that agents reason over the right information and produce reliable outcomes. It subsumes prompt engineering — instruction-wording is one input to the context surface — but extends to every token the model sees before it responds: system prompts, conversation history, retrieved documents, tool schemas, output format specifications, memory summaries, and intermediate state. Andrej Karpathy called it "the delicate art and science of filling the context window with just the right information for the next step." Shopify's Tobi Lutke defined it as "the art of providing all the context for the task to be plausibly solvable by the LLM." Simon Willison endorsed the term because, unlike "prompt engineering," its inferred meaning is close to what the work actually involves.

---

## Why Most Agent Brittleness Is Context Failure

The prevailing misdiagnosis of agent failure is model inadequacy: the model was not smart enough, the model hallucinated, the model ignored instructions. The evidence contradicts this. Anthropic's engineering team reports that agents fail primarily because the context they operate in is incomplete, stale, noisy, conflicting, excessive, or wrongly shaped — not because the underlying model lacks capability. LangChain identifies four specific failure modes directly traceable to context quality: context poisoning (bad information enters and is trusted), context distraction (overwhelming or irrelevant information degrades signal), context confusion (contradictory information forces arbitrary resolution), and context clash (incompatible information from different sources creates irreconcilable conflicts). Enterprises in 2025 attributed 65% of agent failures to context drift — stale, incomplete, or wrongly ordered context — rather than to model limitations.

This has a hard architectural implication: you cannot fix context failures by upgrading the model. Context rot is architecture-level brittleness. Morph's 2025 research tested 18 frontier models including GPT-4.1, Claude Opus 4, and Gemini 2.5 and found every single one degraded as input length increased. Paulsen et al. (2025) measured effective context windows against advertised limits and found "all models fell far short of their Maximum Context Window by as much as 99 percent." A model advertising a 200K-token window may become unreliable at 130K, with sudden performance cliffs rather than gradual degradation. The lesson: context management cannot be deferred to the model. It must be engineered.

---

## The Context Surface: What It Contains

Context engineering begins with an accurate inventory of everything the model sees. The full context surface for an agentic LLM has seven distinct layers:

**1. System instructions** — The foundational framing: role, behavioral norms, constraints, escalation rules. Anthropic's guidance: be specific enough to guide behavior, flexible enough to let the model apply strong heuristics. Avoid both over-specified if-else brittle logic and vague guidance that assumes false shared context.

**2. Tool affordances** — Tool schemas define what the model can do. This is structural context, not prose context. A well-designed tool schema is self-documenting: descriptive parameter names, unambiguous function signatures, and no overlapping tool functionality that forces the model to guess which tool applies. Bloated tool sets create ambiguous decision points: if engineers cannot definitively identify which tool to use in a situation, agents cannot either. Tool schemas are context that shapes behavior more predictably than prose instructions — they encode the action space.

**3. Retrieved knowledge** — Documents, facts, and data fetched from external sources (databases, vector stores, web search) and injected into the context window. Quality of retrieval directly determines quality of context. This layer is where RAG architecture lives, and where retrieval failures (wrong documents, stale documents, missing documents) produce the most insidious agent failures — the model reasons confidently over wrong premises.

**4. Conversation history** — The accumulated record of prior turns in the session. Useful early; progressively harmful as it grows. History that contains failed attempts, superseded decisions, and abandoned branches gives them equal weight to current decisions unless explicitly managed. The model cannot distinguish "this decision was later reversed" from "this decision is current" without structural help.

**5. Intermediate state and tool results** — The outputs of tool calls made during the current task: command outputs, search results, file contents, API responses. This is the most volatile layer: it changes on every turn, must reflect current reality, and accumulates fastest during multi-step agentic tasks. Unmanaged tool result accumulation is the primary driver of context rot in long-running agents.

**6. Examples (few-shot)** — Demonstrations of desired input-output behavior. The most potent per-token investment in the context budget. Examples function as executable specifications: they show rather than tell. Selection quality dominates; see the In-Context Learning section below.

**7. Output schemas** — The structured format the model is expected to produce. Output schemas are context that constrains the generation space before the model begins. Constrained decoding via JSON schema or Pydantic models converts probabilistic text generation into reliable structured output. This is structural context engineering: the schema is not documentation about what you want — it is a hard constraint on what the model can produce.

---

## Retrieval: Where Context Quality Is Won or Lost

Retrieval-Augmented Generation (RAG) is the dominant pattern for injecting knowledge into agent context, and retrieval quality is the primary determinant of context quality in knowledge-intensive tasks. Poor retrieval produces context that is worse than no context: the model receives confident wrong premises and reasons from them. Good retrieval produces context the model can reason over reliably.

### The Retrieval Failure Taxonomy

Naive RAG fails in five specific ways identified by freecodecamp.org's 2025 analysis:

1. **Pronoun ambiguity**: "It increased by 40%" — a chunk retrieved without its referent. The chunk is factually correct but contextually meaningless.
2. **Orphaned comparisons**: "This is 3x faster" — context stripped of what it's being compared to.
3. **Broken procedures**: sequential steps scattered across chunks, retrieved non-contiguously.
4. **Temporal loss**: "As of last quarter" — relative temporal references stripped of their anchor.
5. **Missing prerequisites**: references to concepts defined elsewhere in the same document, but not retrieved.

Each failure is a chunking or retrieval failure, not a model failure. The model reasons correctly from the bad premises it was given.

### The Retrieval Architecture That Works

Three improvements combined address the failure taxonomy:

**Contextual embeddings**: rather than embedding isolated chunks, prepend an LLM-generated summary explaining each chunk's purpose and document location before embedding. This encodes both content and context into the vector representation. Studies show a 67% reduction in retrieval failures when contextual retrieval is combined with reranking (Anthropic/Chatterjeesaurabh research).

**Hybrid search**: combine BM25 keyword matching with dense vector search via Reciprocal Rank Fusion (RRF). Vector-only retrieval is semantic and misses exact tokens, rare strings, and proper nouns. BM25-only retrieval misses paraphrase and semantic variation. Hybrid catches both. For agent systems handling code, configuration values, version numbers, and named entities, hybrid search is non-negotiable.

**Reranking**: retrieve 20 candidates; rerank by cross-encoder relevance (not the initial query embedding). Cross-encoders process query and document together, enabling far more nuanced relevance scoring than bi-encoders. The top 5 after reranking substantially outperform the initial top 5.

### Retrieval as Dynamic Context Construction

The right mental model is not "fetch documents and inject them." It is "construct context on demand from the retrieval layer, incrementally, as the task progresses." Anthropic's just-in-time loading pattern: represent large knowledge bases as lightweight identifiers (file paths, stored query keys, document IDs) in the initial context, and load content dynamically at the moment it is needed. This mirrors human cognition — retrieve on demand rather than memorize in advance. Claude Code exemplifies this: CLAUDE.md loads at session start; glob and grep tools enable just-in-time navigation into the codebase without pre-loading hundreds of files.

---

## Context Window Management: The Physics of Attention

Model vendors advertise context windows of 200K–1M tokens. These numbers are misleading. The maximum context window (MCW) is the architectural limit. The maximum effective context window (MECW) is the limit at which the model's reasoning on your specific task type remains reliable. Paulsen et al. found that MECW varies by problem type and falls far below MCW — some models experiencing severe degradation by 1,000 tokens on complex reasoning tasks. The gap is not linear; it appears as sudden cliff drops at task-specific thresholds.

### Context Rot: The Three Mechanisms

Context rot — degraded output quality as context length grows — has three compounding causes:

**Lost-in-the-middle**: transformer attention follows a U-shaped pattern. Information at the beginning and end of context receives disproportionate attention. Information in the middle is systematically underweighted. Performance drops by more than 30% when the relevant document appears in positions 5–15 compared to position 1 or 20, across multi-document QA tasks (Morph, 2025). Placement of critical information is not cosmetic; it determines whether the model sees it.

**Attention dilution**: transformer self-attention grows quadratically with token count. At 100K tokens, the model tracks approximately 10 billion pairwise relationships, with each token's attention score softmax-normalized across the full context. Individual token significance decreases as context grows, even when the token is highly relevant.

**Distractor interference**: semantically similar but irrelevant content actively misleads models. This is worse than irrelevant content in a different domain — the model pattern-matches against the similar content and retrieves wrong inferences. Code search returning plausible-but-wrong files is a canonical example: four distractors degrade performance more than one, non-uniformly. Chroma's 2025 study found that semantically similar irrelevant content causes degradation beyond what context length alone explains.

### Management Strategies

**Compaction**: at context-window limits, summarize the session and reinitiate with the compressed summary. Preserve architectural decisions and unresolved constraints; discard redundant tool outputs and abandoned branches. Morph's FlashCompact approach and Anthropic's native compaction API are production implementations.

**Observation masking**: replace older environment observations with structured placeholders rather than full text. JetBrains research found observation masking matched or exceeded LLM summarization in task solve rate while being 52% cheaper, because summarization inadvertently extended agent trajectories by 13–15% by obscuring natural stopping signals.

**Anchored iterative summarization**: maintain a structured "memory anchor" with key facts, file paths, error messages, and decisions, updated at checkpoints. Zylos research found this achieved the highest technical accuracy (4.04 vs. Anthropic API compaction's 3.74) for preserving cross-turn context across long sessions.

**Multi-agent isolation**: specialized sub-agents receive clean context windows focused on subtasks, returning condensed summaries (1,000–2,000 tokens) to the coordinator. Context isolation rather than expansion is the scaling strategy. Anthropic's multi-agent system outperformed a single Opus 4 agent by 90.2% on benchmark tasks through this mechanism.

The rule of thumb: nearly 65% of enterprise AI failures in 2025 were attributed to context drift or memory loss during multi-step reasoning, not raw context exhaust. The problem is not hitting the limit — it is losing coherence well before the limit.

---

## Context Failure Modes: A Diagnostic Taxonomy

Context failures are systematic. Naming them precisely enables targeted diagnosis rather than generic "make the prompt better" interventions.

**Missing context**: the agent lacks information required to complete the task. It defaults to internalized priors, which may be outdated, domain-inappropriate, or simply wrong. Symptom: the agent behaves plausibly but incorrectly, without signaling uncertainty.

**Stale context**: retrieved or static documents describe a prior state of the world. APIs change, file paths move, configurations evolve. The agent reasons correctly from correct-but-outdated premises. Symptom: correct historical reasoning, wrong current-state conclusions. Atlan's 2025 enterprise analysis found that freshness is "the hardest layer in enterprise LLM deployments."

**Noisy context**: retrieved documents include irrelevant content that competes with relevant content for the model's attention. Distractor interference amplifies this. Symptom: correct answers buried in incorrect context produce incorrect synthesis.

**Conflicting context**: multiple sources disagree. The model must pick one or average them; neither is reliable without domain knowledge the model may not have. Symptom: output that is internally consistent but selectively ignores correct information.

**Excessive context**: context stuffing — loading everything that might be relevant because the context window is large. Large does not mean free. Every irrelevant token competes with relevant ones. Context rot begins. Symptom: accuracy on well-scoped tasks degrades as document count grows.

**Wrongly-shaped context**: correct information in the wrong format. A well-structured table presented as prose, a structured error message embedded mid-paragraph, examples formatted inconsistently with production inputs. The model cannot efficiently route to the relevant content. Symptom: correct information present but consistently unused.

**Contextual drag** (Alzahrani et al., 2025): errors in context propagate. When incorrect information appears early in the context, it "drags" the model toward flawed conclusions in downstream reasoning — anchoring effect at scale. Error impact compounds in multi-step reasoning tasks. Symptom: early context errors appear in output even when the correct information appears later.

---

## Adversarial Context: Poisoning and Manipulation

Context integrity is a security concern, not only a quality concern. Two attack categories are operationally relevant:

**PoisonedRAG** (Zou et al., USENIX Security 2025): attackers inject a small number of malicious passages into a RAG knowledge base. Each malicious passage satisfies two conditions: a retrieval condition (it is retrieved for target queries) and a generation condition (it causes the LLM to produce attacker-chosen output). The attack achieves a 90% success rate by inserting only five poisoned texts into a knowledge base of millions of clean texts. The attack succeeds because retrieval is similarity-based, not truth-based: a well-crafted adversarial document ranks highly for target queries and overwrites correct context with attacker-controlled premises.

**Prompt injection via retrieved content**: malicious instructions embedded in retrieved documents instruct the LLM to take unauthorized actions. A retrieved web page, email, or document can contain natural-language instructions that the model treats as legitimate directives. This is structurally unsolvable by the model alone — it requires retrieval-layer defenses (source validation, content sanitization, output review before action execution).

The implication for agentic design: do not give agents unrestricted retrieval from untrusted sources combined with unrestricted action capabilities. The combination is a prompt injection attack surface. Either restrict the retrieval source space, or require human review before executing actions that could be attacker-induced. Source validation, context provenance tagging, and skeptical re-prompting are current mitigations; none are complete defenses.

---

## In-Context Learning: Examples as Executable Specifications

Few-shot examples are the highest-leverage per-token investment in the context budget. They function as executable specifications: they demonstrate desired behavior in a form the model can generalize from, without requiring the model to parse abstract descriptions of the same behavior. Anthropic's guidance: "examples are the pictures worth a thousand words."

The critical finding: example selection quality dominates example count. Research shows up to a 16.3% performance gap between the worst and best example selections for the same task. Static examples are expensive — five examples of 200 tokens each add 1,000 tokens to every request. Treating example selection as a one-time setup rather than a per-query decision is a systematic underoptimization.

**Skill-KNN** (Peng et al., EMNLP 2023): generates skill-based descriptions for each test case and candidate example, stripping irrelevant surface linguistic features before embedding. Selects examples by skill similarity to the current input rather than surface similarity. Significantly outperforms embedding-similarity selection across five cross-domain semantic parsing benchmarks. The mechanism: removing surface features that bias embeddings (syntax, length, phrasing) while preserving task-relevant features (the underlying skill being demonstrated).

Four principles for example selection:

1. **Diversity**: cover different aspects of the task space, not just easy cases.
2. **Task-skill similarity**: match the skill required, not the surface form.
3. **Clarity**: unambiguous demonstrations; edge-case examples confuse rather than clarify when not accompanied by annotation.
4. **Balance**: for classification tasks, equal representation of output categories unless the task distribution is itself skewed.

The ACE framework (Peng et al., 2025) extends this to self-improving contexts: treat contexts as evolving playbooks that accumulate, refine, and curate strategies through generate-reflect-curate cycles. ACE achieved +10.6% on agent benchmarks and +8.6% on finance reasoning without fine-tuning, purely through iterative context refinement. This is the research direction pointing toward contexts that improve themselves based on execution feedback.

---

## Structured Context: Schemas as Context Engineering

The most underused lever in context engineering is structure. Prose context requires the model to parse, extract, and route before reasoning. Structured context (JSON, YAML, typed schemas, XML sections, tables) enables the model to navigate directly to the relevant field.

Anthropic's guidance recommends using XML tags or Markdown headers to organize system prompts (background_information, instructions, tool guidance, output description). This is not stylistic preference — it is routing architecture. A model reading 2,000 tokens of structured context can locate the relevant section efficiently. A model reading 2,000 tokens of unstructured prose must parse the entire thing before knowing where the answer is.

Output schemas are the strongest form of structured context. Constrained decoding via JSON Schema or Pydantic converts probabilistic text generation into validated structured output. The model is not writing "whatever seems like valid JSON" — the schema is enforced at generation time, preventing malformed output before it reaches downstream systems. This shifts the engineering contract from "prompt the model carefully and hope the output is parseable" to "declare the output type and receive a valid instance." Pydantic AI implements three approaches: tool output (schema as tool parameter), native output (model produces schema-compliant text), and prompted output (schema injected into prompt). Tool output and native output are structurally enforced; prompted output is not.

Tool affordances as context: the tool schema is context that shapes the model's action space. Each tool description is a specification the model reasons over to select the appropriate action. Overlapping tools, ambiguous parameter names, and inconsistent naming conventions produce the same failures in tool selection as ambiguous instructions produce in text generation. The 12-Factor Agent principle applies: "own your context window" — consciously curate all inputs including tool schemas, which are a form of context the model reads on every turn.

---

## Context Freshness: Staleness as Structural Failure

Context has a decay rate. A system prompt accurate at authoring time will be misleading within months as the underlying system changes. Retrieved documents accurate at indexing time will be wrong when the source changes but re-indexing has not occurred. Conversation history accurate at turn 5 will be superseded by turn 25. Context engineering must treat freshness as a continuous maintenance discipline, not a one-time design decision.

The freshness principles from enterprise deployments (Atlan, 2025):

1. **Completeness**: all required information is present.
2. **Parsimony**: nothing irrelevant is present.
3. **Freshness**: the context reflects current state, not historical state.
4. **Authority**: when sources conflict, the resolution is principled and consistent.
5. **Permission-awareness**: context is scoped to what the current user is authorized to see.

Staleness is particularly dangerous because it is silent. A stale API reference produces confident incorrect output without signaling that the source is outdated. The mitigation requires operational infrastructure: source change detection (subscribe to catalog change events), TTL policies per context type, staleness alerts injected into the pipeline, and re-indexing triggers on schema changes and major updates. "Last validated" frontmatter in loaded documentation provides a mechanical freshness signal at load time.

Context drift kills agents before context limits do: 65% of enterprise agent failures attributed to context drift versus raw context exhaust (Zylos research, 2025). The session that exceeds the context limit is recoverable with compaction. The session that reasons from a stale API reference for 40 turns produces output that is wrong in ways that are hard to detect and harder to trace.

---

## Implications for This Skill Library

Context engineering is not a topic alongside skill engineering — it is the foundational mechanism through which skills function. Every SKILL.md is a context document. Every reference file is context loaded on demand. The harness is a context architecture. The conventions below translate foundational theory into library-specific practice.

**[gate] Minimum effective dose as a load test**: for every skill, the question is not "is this information relevant?" but "is this information needed in the next 5 turns?" The context engineering minimum-dose principle — the smallest possible set of high-signal tokens that maximize desired outcome — applies to every reference file in every skill. References loaded unconditionally should be flagged as candidates for on-demand loading.

**[gate] Output schema as a contract, not a suggestion**: skills that declare output formats in SKILL.md as prose descriptions are weaker than skills that declare structured output schemas in `schemas/output.json`. The schema is enforced context; the prose description depends on the model's interpretation. Typed skills with `schemas/` subdirectories implement the stronger contract. The rubric in `context-engineering.md` Dimension 6 (verification context) is only achievable when the expected output structure is defined structurally, not as prose.

**[gate] Retrieval architecture for reference loading**: skills that load all references unconditionally have a flat retrieval architecture. Skills with routing tables in SKILL.md that specify which references apply to which modes implement just-in-time loading. The difference is context stuffing vs. contextual retrieval. References that are never accessed in typical sessions are dead context — documented in `context-engineering.md` AP-01.

**[review] Staleness audit as a maintenance obligation**: every claim in every SKILL.md and reference file has a decay rate. The `last_validated:` frontmatter convention is a mechanical freshness signal. Skills without version-dated content claims cannot be audited for staleness. The `context-engineering.md` rubric Dimension 3 (freshness and drift prevention) operationalizes the quarterly audit cadence.

**[review] Example diversity in evals/**: skill evaluation datasets are examples used for in-context learning and offline evaluation. Skill-KNN principles apply: examples should be selected for skill diversity, not surface similarity. A routing corpus of 12 trigger examples that all look alike provides less coverage than 8 diverse examples spanning different task phrasings and user types.

**[review] Structured sections as routing architecture**: SKILL.md files organized with explicit Markdown headers (## Invocation, ## Modes, ## Output Contract) enable faster model navigation than prose skill files. The structured context routing principle applies: the model can locate the relevant section without reading the full document.

**[hypothesis] Contextual drag in multi-skill sessions**: when multiple skills are loaded or referenced in a single session, early skill activations may introduce contextual drag that biases subsequent reasoning. An agent that routes through `plan-prd` in turn 1 and `arch-pattern` in turn 15 may carry forward PRD-mode framing that inappropriately anchors the architecture discussion. This is an open research question for the skill library; the mitigation hypothesis is explicit mode-reset context injected at skill handoff points.

**[hypothesis] ACE-style context refinement for skill evals**: if skill evaluation datasets (evals/\*.json) are treated as evolving playbooks rather than static fixtures — accumulating new routing examples from production sessions, reflecting them on failure patterns, curating the resulting updates — the routing corpus could improve without manual authoring. This maps directly to the ACE generate-reflect-curate cycle applied to skill context rather than task context.

The companion rubric `context-engineering.md` in `references/rubrics/` operationalizes these principles as scored dimensions. This document provides the foundational rationale for why those prescriptions exist and what the research evidence supporting them is.

---

## Source Citations

1. Anthropic Engineering (2025). "Effective Context Engineering for AI Agents." anthropic.com. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

2. Willison, Simon (2025). "Context Engineering." simonwillison.net. https://simonwillison.net/2025/jun/27/context-engineering/

3. LangChain (2025). "Context Engineering for Agents." langchain.com. https://www.langchain.com/blog/context-engineering-for-agents

4. Schmid, Philipp (2025). "The New Skill in AI is Not Prompting, It's Context Engineering." philschmid.de. https://www.philschmid.de/context-engineering

5. Paulsen, A. et al. (2025). "The Maximum Effective Context Window for Real-World Tasks." arXiv:2509.21361. https://arxiv.org/abs/2509.21361

6. Morph (2025). "Context Rot: Why LLMs Degrade as Context Grows." morphllm.com. https://www.morphllm.com/context-rot

7. Alzahrani, N. et al. (2025). "Contextual Drag: How Errors in the Context Affect LLM Reasoning." arXiv:2602.04288. https://arxiv.org/pdf/2602.04288

8. Chatterjeesaurabh (2024). "Contextual RAG System with Hybrid Search and Reranking." analyticsvidhya.com. https://www.analyticsvidhya.com/blog/2024/12/contextual-rag-systems-with-hybrid-search-and-reranking/

9. Peng, B. et al. (2023). "Skill-Based Few-Shot Selection for In-Context Learning." EMNLP 2023. arXiv:2305.14210. https://arxiv.org/abs/2305.14210

10. Peng, B. et al. (2025). "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models." arXiv:2510.04618. https://arxiv.org/abs/2510.04618

11. Zou, W. et al. (2025). "PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models." USENIX Security 2025. https://www.usenix.org/conference/usenixsecurity25/presentation/zou-poisonedrag

12. Zylos Research (2025). "AI Agent Context Compression: Strategies for Long-Running Sessions." zylos.ai. https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies/

13. JetBrains Research (2025). "Cutting Through the Noise: Smarter Context Management for LLM-Powered Agents." blog.jetbrains.com. https://blog.jetbrains.com/research/2025/12/efficient-context-management/

14. Atlan (2025). "How to Build Context for LLMs in Enterprise: 5-Layer Guide." atlan.com. https://atlan.com/know/how-to-build-context-for-llms-enterprise/

15. freecodecamp.org (2025). "How Contextual Embeddings and Hybrid Search Fix Retrieval Failures." freecodecamp.org. https://www.freecodecamp.org/news/how-contextual-embeddings-and-hybrid-search-fix-retrieval-failures
