# Content Patterns

The patterns that determine whether the legitimate signal in a candidate's history
lands with the AI ranker and the recruiter. Format gets the resume parsed; content
patterns get it ranked.

## The X-Y-Z Bullet Form

Originally surfaced by Laszlo Bock (former SVP People Operations at Google), the
X-Y-Z form is now the dominant 2026 standard because it co-locates outcome, metric,
and method on a single line — robust to both parser extraction and AI semantic
ranking.

```
Accomplished [X] as measured by [Y], by doing [Z].
```

- **X (outcome)**: what changed in the world. Past-tense action verb + object.
- **Y (metric)**: how the change was measured. The number, percentage, time period,
  scale, or comparison that anchors the claim.
- **Z (method)**: what the candidate actually did to cause X. Tools, techniques,
  scope.

### Good vs. weak

**Weak**: "Responsible for improving customer retention."
**Why weak**: No outcome (X is vague), no metric (Y is missing), no method (Z is
missing). A parser indexes "customer retention" and nothing else.

**Good**: "Reduced customer churn from 8.2% to 5.1% (90-day cohort retention) by
shipping a predictive churn-risk model and a targeted re-engagement workflow in
Braze."
**Why good**: Outcome quantified (`8.2% → 5.1%`), metric defined (`90-day cohort
retention`), method named (`predictive churn-risk model`, `Braze`). Parser indexes
all five searchable terms.

### Verb bank (lead each bullet with one)

**Built / shipped**: Built, shipped, launched, deployed, implemented, developed,
architected, designed, engineered, prototyped.

**Improved / changed**: Reduced, increased, accelerated, doubled, halved, cut, raised,
streamlined, optimized, eliminated.

**Led / coordinated**: Led, managed, directed, coached, mentored, coordinated, drove,
ran, established.

**Analyzed / researched**: Analyzed, evaluated, audited, modeled, forecasted,
benchmarked, A/B-tested, validated.

**Resolved / fixed**: Diagnosed, debugged, resolved, fixed, recovered, remediated.

Avoid: "Responsible for," "Assisted with," "Helped to," "Worked on," "Tasked with."
These hide agency and signal weakness to AI rankers trained on quantified
achievement language.

### When the candidate doesn't have a metric (the X-Z fallback)

Not every meaningful contribution has a clean number attached. When the candidate
genuinely doesn't have a Y, write the bullet as X-Z — never fabricate a metric.

**X-Z form**: "Shipped event-streaming pipeline (Kafka, Apache Flink) replacing the
batch ETL job, enabling real-time fraud decisions and cutting per-decision latency
from sub-second batch to sub-200ms streaming."

Note: the *direction* of improvement (`from batch to streaming`, `cutting latency`)
still anchors the claim even without a single number. Direction + named tools is
acceptable when no clean metric exists.

## Summary (the first 30 seconds)

The 2–3 lines under the candidate's name and target role. Pattern:

```
[Seniority + Role] with [X years] [domain experience]. [Anchor skill 1, anchor skill 2,
anchor skill 3]. [One quantified outcome OR one signature accomplishment].
```

### Example

> Senior software engineer with 9 years building distributed data infrastructure.
> Strong in Python, Go, and Kafka/Flink streaming systems; previously lead engineer
> on a real-time fraud platform serving 12M MAU. Reduced fraud false-positive rate
> from 8.2% to 2.1% over two years.

### Pitfalls

- **Don't open with "passionate," "results-driven," "team player," or any other
  buzzword adjective.** They are universally ignored by parsers and discounted by
  recruiters; they signal weakness, not strength.
- **Don't write a "career objective" stating what you want from the employer.** That
  format died in 2010. Lead with what you offer.
- **Mirror the JD's role title and 2–3 of its top required skills.** The summary is
  where exact-keyword-match scoring is highest because parsers weight terms near the
  top of the document.

## Skills Section

Grouped by category, every keyword as an individual searchable term. Match the
candidate's actual JSON Resume `skills[]` block (see `json-resume-schema.md`).

### Rendered example

```
SKILLS

Languages          Python, Go, SQL, TypeScript, Bash
Distributed        Apache Kafka, Apache Flink, Apache Spark, Redis, PostgreSQL, Cassandra
Cloud & Infra      AWS (EC2, S3, EKS, RDS, Kinesis), Terraform, Docker, Kubernetes
ML & Observability scikit-learn, XGBoost, Datadog, OpenTelemetry, Grafana
```

### Authoring rules

- **One keyword = one searchable term.** "Python, Go, SQL" is three terms;
  "Python/Go/SQL" is one bundled token. Always separate with commas, not slashes.
- **Dual-encode acronyms inside one keyword**: `AWS (EC2, S3, EKS)` indexes both
  `AWS` and the service names. `Project Management Professional (PMP)` indexes both
  full form and acronym. The parser tokenizes both ways.
- **Group by domain**, with named categories (`Languages`, `Distributed`, `Cloud`,
  `Tooling`). Grouped skills signal depth (5 distributed-systems tools reads stronger
  than 5 unrelated tools) and reduce recruiter scan time.
- **Mirror JD terminology exactly**. If the JD says "Postgres," list "Postgres" — or
  better, "Postgres / PostgreSQL" to cover both forms.
- **Don't list skills the candidate cannot defend in a 5-minute interview.** AI
  screeners increasingly cross-check stated skills against bullet evidence; humans do
  too. Five real skills beats fifteen padded ones.
- **No `level` field** (Expert / Intermediate / Beginner). Self-assessed levels are
  not weighted by rankers and hurt credibility — they're either inflated (most
  candidates) or sandbagged (some), and there's no objective external reference.

## Work Experience Bullets

3–5 bullets per recent role; 2–3 per older roles. Lead with the strongest quantified
outcome (the recruiter's first 6–8 seconds land on the top of each role).

### Bullet ordering within a role

1. Strongest quantified outcome ("$X impact, Y% improvement").
2. Largest-scope technical accomplishment (system shipped, scale achieved).
3. Leadership or cross-functional impact (team led, partners worked with).
4. Process or tooling improvement.
5. (Optional) Domain-specific accomplishment relevant to the target role.

### Quantification (the Y in X-Y-Z)

The candidate's Y can be any of:

- **Percentage change**: "Reduced X by 18%."
- **Absolute change**: "Cut latency from 1.4s to 180ms."
- **Multiple**: "3× the prior baseline."
- **Throughput or scale**: "2B events per day," "12M MAU."
- **Time saved**: "Eliminated 15 hours/week of manual reconciliation."
- **Revenue or cost**: "$2.3M ARR pipeline," "Saved $450K/year in vendor costs."
- **Team or scope**: "Led 5 engineers," "Owned the 4 services responsible for ..."
- **Comparison**: "Top performer of 8 SDRs in Q2 (152% quota)."

When the candidate cannot recall a precise number, an approximate is better than
none ("~$2M ARR," "roughly 15 hours/week"). When even the direction is fuzzy, fall
back to X-Z form.

## Education Bullets

- **No GPA** unless it's 3.5+ or the field is required by the JD/posting.
- **Coursework**: list only when the courses match JD-mentioned topics; otherwise
  skip. Padding with generic coursework dilutes signal.
- **Thesis / capstone**: include if it demonstrates a directly relevant skill.
- **Honors**: list at the degree level (`magna cum laude`); award details go in an
  `Awards` section if substantial.

## Projects (engineering / data roles)

Include projects when they demonstrate a JD-mentioned skill not covered in
`work[]`, or when open-source / personal work is itself a hiring signal.

Each project: name, one-line description, URL, dates, 1–2 bullets, keywords.

```
ratelimit-rs                                              2023 – 2024
Open-source distributed rate limiter in Rust, 2.3K GitHub stars
github.com/janecandidate/ratelimit-rs
• Implemented token-bucket and sliding-window algorithms with Redis backend; benchmarked
  at 180K req/s on a single node.
• Cited in two Rust ecosystem talks at RustConf 2024.
Keywords: Rust, Redis, Distributed Systems
```

## Vocabulary Anchoring (Principle 4 in practice)

Before writing, build a keyword map from the JD:

1. Copy the JD's "Requirements" and "Preferred Qualifications" sections.
2. Extract every named tool, skill, methodology, certification, and domain term.
3. For each, mark whether the candidate has it (yes / partially / no).
4. For each "yes," ensure the exact term appears at least once in the resume —
   ideally in the skills section AND in at least one bullet.
5. For each "partially," include the partial experience honestly (don't claim full
   mastery of something you've used once).
6. Skip the "no" terms entirely. Fabricating is the worst possible move; AI
   screeners and recruiters both check.

The keyword-map exercise typically reveals 8–15 specific terms to mirror. Done well,
this single step often moves the application from "below threshold" to "above
threshold" without changing the candidate's substance at all.

## Anti-Pattern: AI-Generated Generic Bullets

LLMs default to bullet patterns like:

> "Leveraged cross-functional collaboration to drive impactful results in a fast-paced
> environment."

Every word in that sentence is a discount signal: "leveraged," "cross-functional,"
"impactful," "fast-paced." The bullet conveys no information, fails the X-Y-Z test
entirely, and AI screeners trained on quantified-achievement language give it near
zero ranking weight.

The fix: every bullet must answer "what specifically changed, by how much, and how
did you cause it?" If the bullet can't answer all three (or two with X-Z fallback),
delete it.
