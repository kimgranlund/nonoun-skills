---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/invocation-flow.md
  - ../methodology/prompt-steelmanning.md
  - ../methodology/scoping-survey.md
primary_sources:
  - Internal observation — scoping-survey.md runs web research-survey without first taking inventory of base-model knowledge
---

# Concept matching against the training corpus

After a prompt has been steelmanned (see `prompt-steelmanning.md`), the meta-skill should do a **concept-matching pass** against the base model's training corpus. This is introspective inventory: what does the base model already know about the prompted domain, what does it know weakly, and what does it not know at all?

Concept matching calibrates three downstream decisions:

1. **How much WebSearch the scoping survey needs.** Dense base-model coverage → less search. Sparse coverage → heavy search.
2. **Where the produced skill should hedge.** Domains with weak base-model coverage need explicit uncertainty flags.
3. **What axes to propose.** The base model's natural decomposition is usually a good first approximation.

Without concept matching, the scoping survey runs blind — searching for things the base model already knows (wasteful) AND trusting search results in areas where the base model has strong priors to verify against (dangerous).

## What concept matching IS

An introspective pass in which the main thread asks itself: "For domain X, what do I (the base model) know?" The output is a **concept inventory**:

- Canonical figures, papers, books, products.
- Sub-fields and their structure.
- Methodological distinctions.
- Live controversies.
- Adjacent fields.
- Temporal coverage (does my knowledge skew 2015? 2022? 2024?).
- Confidence level per cluster.

Concept matching is NOT:
- **A web-search substitute** — it's a pre-search calibration. WebSearch still runs in the scoping survey.
- **An authoritative statement** — it's honest introspection about the base model's limits, not a claim that the introspection is perfect.
- **A replacement for expert review** — the base model has biases and gaps; concept matching surfaces them, doesn't eliminate them.

## Why it matters

Three failure modes that concept matching prevents:

### Failure 1: WebSearch waste

Scoping agent searches for "Pearl causal inference foundational papers" — a query the base model could answer directly. Time spent; cache not primed; no new information.

Concept matching first: "I know Pearl 1988 BN book, 1995 Biometrika DAG paper, 2009 Causality book, 2018 Book of Why, 2011 Turing Award." → scoping survey only needs to verify these + find what I don't know (recent 2024-2026 developments).

### Failure 2: Overconfident ingestion of search results

Scoping agent returns a web result claiming X. Base model accepts without challenge because it has no priors. But X is wrong — a crackpot site or a corporate-marketing puff piece.

Concept matching first: if base model HAS priors in this area, it can challenge the search result. If base model HAS NO priors, this gets flagged as heavy-WebSearch area where skill claims need extra hedging.

### Failure 3: Axis proposal misalignment

Scoping agent proposes axes based on surface-level web reads. Misses the field's actual structure because web search surfaces marketing terms, not disciplinary ones.

Concept matching first: the base model often knows the real disciplinary decomposition (e.g., "causal inference breaks into identification, estimation, and sensitivity analysis"). Propose axes from this internal structure, verify with WebSearch, not the reverse.

## The concept inventory protocol

When the steelmanning phase is complete and the domain is fixed, run:

### Step 1: List 15-25 expected concepts

For domain X, what canonical items would you expect?

- Named figures (theorists, practitioners, inventors)
- Landmark papers / books / talks
- Canonical tools / libraries / frameworks
- Sub-fields / named methodologies
- Live controversies
- Adjacent fields / peer domains
- Recent developments (last 2-3 years)

Write them down. Don't stop at 5 — push to 15-25. Thin lists signal weak base-model coverage.

### Step 2: Rate confidence per item

Four tiers:

| Tier | Meaning |
|---|---|
| **High** | "I can cite this with specifics. Author, year, core contribution." |
| **Medium** | "I know the name and general importance. Some gaps on specifics." |
| **Low** | "I've heard of this. Can't recall specifics." |
| **Unknown** | "I'd be guessing if I described this." |

Be honest. Inflating confidence here corrupts downstream decisions.

### Step 3: Cluster analysis

Look at the confidence distribution:

- **Mostly high** → base model has dense coverage. WebSearch mainly to verify recency + fill specific gaps.
- **Mixed high/medium** → solid base + blind spots. WebSearch for blind-spot clusters + verification.
- **Mostly low/unknown** → base model has sparse coverage. WebSearch is the primary source; hedge heavily in the produced skill.
- **High-but-dated** → base model knows 2015-2022 canon; doesn't know 2024-2026. WebSearch mandatory for recency.

### Step 4: Temporal analysis

Where in time does the base model's knowledge concentrate? Common patterns:

- **Pre-2023 canon-heavy**: classical fields (causal inference, formal logic, psychophysics).
- **2020-2023 surge**: recent rapid-moving fields (LLMs, AI safety).
- **Sparse post-2024**: nearly everything.
- **Older heavy, recent weak**: stable fields with occasional updates (clinical medicine, typography).

If the domain is fast-moving (ML, LLMs, crypto, web platform), the base model is reliably out of date on recent developments. Budget heavy WebSearch for 2024-2026 material.

### Step 5: Axis proposal

The concept inventory typically suggests a natural decomposition. Common structures:

- **Method / finding / debate** (Model C from `meta-theory-author/references/methodology/theoretical-axes.md`).
- **History / contemporary / techniques** (Model B-temporal).
- **Sub-problem 1 / sub-problem 2 / ...** (Model D).

Propose axes that cover the high-confidence clusters and leave room for the low-confidence ones to be filled by WebSearch.

## Worked example: causal-inference-expert

### Step 1: Concept list

```
Pearl J. (DAGs, do-calculus, Book of Why)
Rubin D. (potential outcomes, propensity scores)
Imbens G. (IV, potential-outcomes advocate)
Angrist J. (IV in econ, natural experiments)
Robins J. (g-methods, MSMs)
Hernán M. (g-methods, Causal Inference: What If)
VanderWeele T. (mediation, interaction)
Holland P. (No causation without manipulation)
Cartwright N. (RCT critique)
Deaton A. (RCT epistemology)
Back-door / front-door criteria
Propensity score matching
Difference-in-differences (Card-Krueger)
Regression discontinuity
Instrumental variables (Angrist lottery)
Double machine learning (Chernozhukov)
Causal forests (Athey-Wager)
Replication: LaLonde 1986 + Dehejia-Wahba
Contested: model-free DL causal methods (Louizos+)
Recent: Guido Imbens Nobel 2021, Angrist-Card-Imbens
```

### Step 2: Confidence rating

- **High** (11): Pearl, Rubin, Imbens, Angrist, Robins, Holland, back-door, propensity, DiD, RDD, IV.
- **Medium** (7): Hernán, VanderWeele, Cartwright, Deaton, double-ML, causal forests, LaLonde.
- **Low** (2): DL causal methods recent literature, specific 2024-2026 developments.
- **Unknown** (~): recent Judea Pearl work post-2020; causal inference in specific applied domains (genomics, policy).

### Step 3: Cluster analysis

**Mostly high with strong medium** → dense base-model coverage. WebSearch primarily to verify recent developments (post-2024 papers, any retractions, new methods) and fill the low-confidence clusters (applied-domain work, DL causal).

### Step 4: Temporal

Strong pre-2022 coverage. Thin post-2023 (Athey-Wager causal forests ~2019 is the most recent thing I can cite specifically). WebSearch mandatory for 2024-2026 frontiers.

### Step 5: Axis proposal

Three axes via Model C (methods / findings / debates):
- `methodologies/` — Pearl, Rubin, Imbens, Robins, Angrist. Strong coverage.
- `findings/` — LaLonde, Card-Krueger, Angrist-Vietnam. Strong coverage.
- `debates/` — Imbens-Pearl, Deaton-RCT. Strong coverage.

Plus a `recent/` axis for 2024-2026 developments, **flagged as high-WebSearch-dependency, lower-confidence**.

## When the base model's coverage is thin

If concept matching reveals mostly Low / Unknown:

1. **Flag this explicitly to the user.** "The base model has sparse coverage of this domain. WebSearch will be primary. Produced claims will have lower confidence than typical."
2. **Budget more WebSearch per wave.** Normally 20-30 queries in scoping; double it for thin domains.
3. **Use more agents per wave.** Heavier verification burden.
4. **Hedge aggressively in the produced skill.** Every factual claim gets an explicit confidence signal.
5. **Consider whether the domain is too niche for this method.** If the canon isn't web-searchable either, the skill will be bad regardless. Consider declining.

## When the base model's coverage is dense

If concept matching reveals mostly High:

1. **Consider skipping the scoping survey.** If you can reliably list 30 canonical items without searching, you've just done most of what the survey would do.
2. **Shorten Wave 1.** Start with recap of canon rather than discovery.
3. **WebSearch only to verify + recency.** Not for discovery.
4. **Produced skill can make stronger claims.** Base-model prior + WebSearch verification is more solid than either alone.

## Anti-patterns

### Overconfident inventory

Rating items "High" because you've heard of them isn't high confidence. High means "I can cite the author, year, and core claim." If you can't, it's Medium or Low.

### Retrofitting after WebSearch

Running WebSearch first, then "concept matching" by restating what search found. That's not introspection; it's post-hoc rationalization.

Concept match BEFORE searching. Then search fills the gaps.

### Treating the inventory as authoritative

The base model has biases — training-data cutoff, subject-matter skew, Western-canon bias, English-language bias. Concept matching is a first pass, not a conclusion.

If your inventory lists 15 names and they're all Western men born 1940-1980, your base model has a skew. The scoping survey should explicitly search for underrepresented contributors.

### Skipping concept matching for "obvious" domains

"It's typography, obviously I know it" — and then the produced skill misses CJK typography completely. Run the inventory even when confident; surfaces blind spots.

### Using concept matching to skip WebSearch entirely

Concept matching doesn't replace WebSearch. It calibrates how much search is needed. Even for dense-coverage domains, WebSearch verifies recency + specific dates + exact quotes. Don't cite from base-model memory alone.

## Reporting the inventory

After the concept-matching pass, surface to the user in one short block:

```
Concept inventory for [domain]:

- High-confidence clusters: [2-4 clusters named]
- Medium-confidence: [named]
- Low / unknown: [named]
- Temporal skew: [where in time is coverage concentrated]
- Recommended WebSearch budget: [light / medium / heavy]
- Hedging level in produced skill: [normal / elevated / very high]
- Proposed axes: [3-5 axis names with 1-line justification each]

Proceed with this shape + search budget?
```

Keep under 15 lines. The user should absorb the inventory in 10 seconds.

## Composition with steelmanning + scoping

Full invocation phase:

1. **Steelman** the prompt → propose stronger shape.
2. User confirms shape.
3. **Concept-match** the confirmed domain → produce inventory.
4. User confirms inventory + axis plan.
5. **Scoping survey** dispatches → fills gaps, verifies recency, produces file plan.
6. Wave 1 dispatches.

Three distinct reads on the user's request, each feeding the next:

- Steelmanning = what's the right output shape?
- Concept matching = what do I already know about that shape's content?
- Scoping = what's missing, what's current, what's canonical?

## One short invariant

**Concept-match before you search. Inventory honestly; calibrate accordingly; don't confuse priors with verification.**
