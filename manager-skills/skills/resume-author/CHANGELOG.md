# CHANGELOG — resume-author

## v1.0.0 (2026-05-15)

Initial release.

### Design decisions

- **JSON Resume as the typed source.** Chose JSON Resume (jsonresume.org) over
  HR-Open Standards Resume/CV or schema.org Person because it is candidate-facing,
  widely tooled, and minimal enough to be human-authored. HR-Open is the enterprise
  interop layer and isn't a candidate authoring format. schema.org Person is for
  web-page markup, not document authoring.

- **DOCX as the default submission artifact.** Per published 2026 testing across
  Workday, Greenhouse, Lever, Taleo, iCIMS, and SmartRecruiters, single-column DOCX
  scores ≥95% parse accuracy across all six. PDF is comparable on modern parsers
  (Greenhouse, Lever, Ashby) but measurably worse on Workday and Taleo.

- **Hybrid section order (Skills → Work Experience) as default.** Aligns with the
  2026 skills-first hiring trend without sacrificing reverse-chronological signal.
  Pure-functional resumes are explicitly forbidden in the anti-patterns because
  both ATS parsers and recruiters treat them as concealment signal.

- **X-Y-Z bullet form as the bullet standard.** Originally from Laszlo Bock; now the
  dominant 2026 standard. Co-locates outcome, metric, and method on a single line —
  robust to both parser extraction and AI semantic ranking.

- **Parse verification as a required step.** The plain-text round-trip check is the
  only inspectable evidence that the skill's parse-fidelity premise holds for any
  particular document. Treating it as optional makes the skill performative.

- **No hidden text / no prompt injection.** Detected by major vendors at rising
  rates (Greenhouse, ManpowerGroup), flagged as fraud in many pipelines, and exposed
  to the recruiter when the ATS strips formatting. The anti-pattern is explicit.

### Research sources

- jsonresume.org/schema and docs.jsonresume.org/schema — JSON Resume schema and
  field semantics.
- HR-Open Standards Resumé/CV Project — alternative enterprise interop standard
  (referenced but not adopted as the candidate-facing schema).
- Resume Optimizer Pro 2026 ATS testing matrices for Workday, Greenhouse, Lever,
  iCIMS — per-platform parser quirks and DOCX/PDF accuracy comparisons.
- ResumeAdapter 2026 ATS formatting rules — failure modes by layout choice.
- TheHireHub 2026 parser accuracy analysis — five-stage parser pipeline,
  where accuracy degrades, per-stratum F1 expectations.
- LinkedIn 2026 talent research — 93% of recruiters increasing AI use; AI
  prescreening prevalence.
- Greenhouse + ManpowerGroup hidden-text detection statistics — prompt-injection
  detection rates and consequences.
- OWASP 2025 Top 10 for LLM applications — prompt injection as the #1 risk in AI
  application security, providing context for vendor-side detection investment.

### Files

- `CHANGELOG.md`
- `SKILL.md`
- `skill.json`
- `references/json-resume-schema.md`
- `references/format-spec.md`
- `references/ats-platform-quirks.md`
- `references/content-patterns.md`
- `references/parse-verification.md`
- `scripts/render_docx.py`
- `scripts/extract_plaintext.py`
- `assets/example-resume.json`
