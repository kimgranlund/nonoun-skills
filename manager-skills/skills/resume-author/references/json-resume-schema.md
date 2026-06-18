# JSON Resume Schema (Authoring Reference)

The typed source of truth for every resume produced by this skill. JSON Resume is an
open standard with a public JSON Schema (https://jsonresume.org/schema/). This
reference covers the subset of fields this skill uses, with authoring conventions
specific to AI-screening-optimized output.

The artifact is disposable. The JSON is durable. Keep it under version control or in
a personal cloud doc; re-render the DOCX for each role.

## Top-Level Structure

```json
{
  "$schema": "https://jsonresume.org/schema/1.0.0/resume.json",
  "basics": { ... },
  "work": [ ... ],
  "education": [ ... ],
  "skills": [ ... ],
  "projects": [ ... ],
  "certificates": [ ... ],
  "publications": [ ... ],
  "languages": [ ... ],
  "awards": [ ... ],
  "volunteer": [ ... ]
}
```

Only `basics`, `work`, `education`, and `skills` are required for an AI-screening
context. The rest are optional and only included when they add ranking signal for the
target role.

## `basics`

```json
{
  "basics": {
    "name": "Jane Q. Candidate",
    "label": "Senior Software Engineer",
    "email": "jane.candidate@example.com",
    "phone": "+1 415 555 0123",
    "url": "https://jane.dev",
    "summary": "Senior software engineer with 9 years building distributed data infrastructure. Shipped real-time pipeline (Kafka, Flink) processing 2B events/day at scale. Strong in Python, Go, and SQL; previously lead engineer at FinTech Co.",
    "location": {
      "city": "San Francisco",
      "region": "CA",
      "countryCode": "US"
    },
    "profiles": [
      { "network": "LinkedIn", "url": "https://linkedin.com/in/janecandidate" },
      { "network": "GitHub", "url": "https://github.com/janecandidate" }
    ]
  }
}
```

**Authoring notes:**

- `name`: Full legal first + last name as it appears on professional records. No
  nicknames in the canonical record (you can use a nickname when rendering for casual
  contexts).
- `label`: The role title the candidate is targeting — not necessarily their current
  one. This becomes the line under the name on the rendered DOCX; parsers often
  extract it as "current title" if not explicitly told otherwise.
- `email`: Lowercased, professional domain. Avoid `firstname123@gmail.com` — the
  email field is one of the highest-priority parser fields.
- `phone`: E.164 format with country code (`+1 415 555 0123`). Parsers handle this
  most reliably across regions.
- `summary`: 2–3 lines, 30–60 words. Pattern: role + years + 2–3 anchor skills +
  one quantified outcome. Mirror the JD's role title here verbatim when possible.
- `location`: City and region/state are sufficient. Full street address is no longer
  recommended (privacy, no parsing benefit). Include `countryCode` (ISO-3166-1
  alpha-2) for international applications.
- `profiles`: LinkedIn is mandatory. GitHub for engineering roles. Personal site if
  it has substance. Skip Twitter/X unless the role is in social/content.

## `work[]`

Reverse-chronological array. Each entry:

```json
{
  "name": "FinTech Co",
  "position": "Senior Software Engineer",
  "url": "https://fintech.example",
  "startDate": "2022-03",
  "endDate": "2025-04",
  "summary": "Lead engineer for the real-time payments fraud detection platform serving 12M monthly active users.",
  "highlights": [
    "Reduced fraud false-positive rate from 8.2% to 2.1% (measured by 90-day chargeback rate) by replacing rule-based scoring with a gradient-boosted model on a 200-feature training set.",
    "Shipped event-streaming pipeline (Kafka, Apache Flink) handling 2B events/day, cutting end-to-end fraud-decision latency from 1.4s to 180ms.",
    "Led a team of 5 engineers and ran the on-call rotation; reduced P1 incidents by 60% over 18 months through runbook standardization and observability work (Datadog, OpenTelemetry)."
  ],
  "location": "San Francisco, CA"
}
```

**Authoring notes:**

- `name` (employer): Official company name as it appears in business records and on
  LinkedIn. Parsers cross-reference. "FinTech Co" not "FinTech" or "FinTech Co, Inc."
  unless the formal entity name is needed.
- `position` (title): Match the official internal title from offer letter / LinkedIn.
  If the internal title was non-standard (e.g., "Code Ninja"), include a normalized
  version in parentheses: `"Code Ninja (Senior Software Engineer)"`.
- `startDate` / `endDate`: ISO 8601 format. Use `YYYY-MM` precision (month + year) —
  the rendering step converts to `Mon YYYY`. For current roles, omit `endDate` or use
  `"Present"`. Never use year-only precision (`"2022"`) — parsers may compute tenure
  as 1 day.
- `summary` (role context, optional): One-line scope statement — what the role
  was, scale, team size, business context. Helps the parser and human reader frame
  the highlights.
- `highlights[]`: Bullets in X-Y-Z form (see `content-patterns.md`). 3–5 per role for
  recent roles; 2–3 for older roles. Lead with the strongest quantified outcome.

## `education[]`

```json
[
  {
    "institution": "Stanford University",
    "area": "Computer Science",
    "studyType": "Master of Science",
    "startDate": "2014-09",
    "endDate": "2016-06",
    "score": "3.9/4.0",
    "courses": ["Distributed Systems", "Machine Learning"]
  }
]
```

**Authoring notes:**

- `studyType`: Full degree name (`"Bachelor of Science"`, not `"BS"`). Acronyms can
  follow in parentheses if useful. Older parsers do not always expand abbreviations.
- `score` (GPA): Include only if 3.5+ or if the field is required. Always show the
  scale (`"3.9/4.0"`), never the bare number.
- `courses`: Include only when the courses match JD-mentioned topics. Pad keyword
  lists go in the `skills` section, not here.
- For ongoing degrees, set `endDate` to the expected completion (`"2026-06"`) and
  add a clarifying note in the rendered DOCX ("Expected June 2026").

## `skills[]`

Grouped by category, each entry carries explicit keywords:

```json
[
  {
    "name": "Languages",
    "keywords": ["Python", "Go", "SQL", "TypeScript", "Bash"]
  },
  {
    "name": "Distributed Systems",
    "keywords": ["Apache Kafka", "Apache Flink", "Apache Spark", "Redis", "PostgreSQL", "Cassandra"]
  },
  {
    "name": "Cloud & Infrastructure",
    "keywords": ["AWS (EC2, S3, EKS, RDS, Kinesis)", "Terraform", "Docker", "Kubernetes"]
  },
  {
    "name": "Observability & ML",
    "keywords": ["Datadog", "OpenTelemetry", "Grafana", "scikit-learn", "XGBoost"]
  }
]
```

**Authoring notes:**

- **One keyword = one searchable term.** Don't bundle ("Python/Go/SQL") — the parser
  may index the whole bundle as a single token. Always individual strings.
- **Dual-encode acronyms** within a keyword: `"AWS (EC2, S3, EKS)"` indexes both
  "AWS" and the service names. `"Project Management Professional (PMP)"` indexes
  both forms.
- **Group by category** with named groupings — improves recruiter scan time and
  signals depth in a domain (5 distributed-systems keywords reads stronger than 5
  random tools).
- **Mirror JD terminology exactly** for every required and preferred skill the
  candidate has. If the JD says "JavaScript," don't write "JS." If it says
  "Postgres," consider both "Postgres" and "PostgreSQL."
- **No `level` field** unless the candidate is willing to defend it (parsers and AI
  rankers don't weight self-reported levels heavily, and inflated levels hurt
  credibility in interviews).

## `projects[]` (optional, but high-value for engineering roles)

```json
[
  {
    "name": "ratelimit-rs",
    "description": "Open-source distributed rate limiter in Rust, 2.3K GitHub stars",
    "url": "https://github.com/janecandidate/ratelimit-rs",
    "startDate": "2023-06",
    "endDate": "2024-12",
    "highlights": [
      "Implemented token-bucket and sliding-window algorithms with Redis backend; benchmarked at 180K req/s on a single node.",
      "Cited in two Rust ecosystem talks at RustConf 2024."
    ],
    "keywords": ["Rust", "Redis", "Distributed Systems"]
  }
]
```

Include when the project demonstrates a skill mentioned in the JD that isn't covered
in `work[]`, or when open-source / personal work is itself a hiring signal.

## `certificates[]`

```json
[
  { "name": "AWS Certified Solutions Architect – Professional", "date": "2024-08", "issuer": "Amazon Web Services", "url": "https://aws.amazon.com/verification/..." }
]
```

Include if the certification appears in the JD's "preferred" or "required" list, or
is a domain credential (CFA, CPA, PMP, security certs). Skip vendor-specific certs
for tools no longer in use.

## `publications[]`, `awards[]`, `languages[]`, `volunteer[]`

Include only when relevant to the target role or when filling space for a candidate
with limited work history. None of these are weighted heavily by parsers; they're
human-reader signals.

## Validation

The JSON Resume schema can be validated against the official JSON Schema document at
`https://jsonresume.org/schema/1.0.0/resume.json`. Before rendering, validate the
document — schema errors typically indicate misnamed fields or wrong types, which
will silently break downstream rendering.

```bash
# Quick local validation with ajv-cli
npx ajv-cli validate -s schema.json -d resume.json
```

## What This Skill Adds Beyond the Base Schema

JSON Resume's schema is intentionally minimal. This skill enforces additional
discipline beyond what the schema requires:

- `startDate` / `endDate` precision must be `YYYY-MM`, not `YYYY`.
- `summary` (in `basics`) is mandatory; it's the first 30 seconds for the recruiter.
- `skills[]` must be grouped, not a flat list.
- `highlights[]` must be in X-Y-Z form (see `content-patterns.md`).
- `position` titles must match the JD's title where the role is comparable.

The base schema does not enforce these, but this skill's render and verification
steps assume them.
