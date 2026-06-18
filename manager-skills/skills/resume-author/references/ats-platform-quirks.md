# ATS Platform Quirks

Per-platform tuning for the six major ATS that screen the majority of US/EU
applications. Read this reference only when the target ATS is known (visible in the
application URL). When unknown, the conservative defaults in `format-spec.md` survive
all six.

## How to identify the ATS

Inspect the application URL. The domain or subdomain identifies the platform:

| URL pattern | ATS |
|---|---|
| `*.greenhouse.io`, `boards.greenhouse.io` | Greenhouse |
| `*.myworkdayjobs.com`, `*.wd1.myworkdayjobs.com` | Workday |
| `*.lever.co`, `jobs.lever.co` | Lever |
| `*.taleo.net`, `*.tal.net` | Oracle Taleo |
| `*.icims.com`, careers-*.icims.com` | iCIMS |
| `*.smartrecruiters.com` | SmartRecruiters |
| `*.ashbyhq.com` | Ashby |
| `*.workable.com` | Workable |

If the apply button opens a modal on the company's own site, view the modal's network
requests in browser dev tools — the ATS endpoint is usually visible.

---

## Workday

**Used by**: ~50% of Fortune 500 (IBM, JP Morgan, Salesforce, Adobe, Netflix, etc.).
Largest enterprise footprint.

**How it works**: Parses the resume into structured fields that pre-fill a
candidate-facing application form. The candidate reviews and corrects the form before
submitting. The recruiter then sees the structured fields plus the attached file.
Workday's Illuminate AI (launched Sept 2024) runs semantic skills matching against
its proprietary Skills Cloud ontology.

**Specific tuning**:

- **DOCX strongly preferred over PDF.** Workday's PDF parser drops measurable
  accuracy on PDFs with any non-trivial layout. DOCX with standard styles is the
  highest-accuracy combination.
- **Strict heading taxonomy.** Workday's parser expects exact heading strings:
  `Work Experience`, `Education`, `Skills`, `Certifications`. Variants like
  "Professional Experience" or "Technical Skills" parse correctly but generic
  custom headings drop section recognition.
- **Date format locked**: `Mon YYYY to Mon YYYY` or `Mon YYYY – Mon YYYY`. Workday's
  parser sometimes mishandles "Present" when joined with a hyphen variant — use
  ` – Present` with spaces and an en-dash, not `-Present`.
- **Job title is heavily weighted in scoring.** If the candidate's prior title doesn't
  map onto the target title's seniority level (e.g., "Engineer II" applying for
  "Staff Engineer"), score drops significantly regardless of bullet content. When
  feasible, use the normalized industry title alongside the internal one:
  `"Code Ninja (Senior Software Engineer)"`.
- **No columns. No tables. No graphics.** Workday's parser is among the strictest on
  this — multi-column layouts scramble section order more reliably here than in
  Greenhouse or Lever.

**What still breaks here in 2026**:
- Multi-column layouts
- Graphics-heavy templates
- Custom heading text
- Year-only date ranges

---

## Greenhouse

**Used by**: 8,500+ customers, ~18% of US mid-market ATS. Heavy in Series B+ tech
(Airbnb, DoorDash, Figma, Stripe, Notion, Reddit, HubSpot).

**How it works**: Parses the resume into the candidate profile but surfaces the
original PDF to the recruiter as the primary view; parsed fields appear as metadata
in a sidebar. Greenhouse AI (launched Sept 2025) summarizes the candidate and scores
match against the JD — but only reads the parsed text, not the original PDF.

**Specific tuning**:

- **Most forgiving of the big three.** Greenhouse's 2024 parser upgrade handles
  vector-text PDFs from design tools reliably, and hybrid layouts with a narrow left
  rail parse correctly ~80% of the time. Still: when in doubt, single-column DOCX.
- **PDF and DOCX both work** at near-equivalent accuracy. PDF preserves visual
  formatting for the recruiter's primary view, which is itself a Greenhouse-specific
  advantage; DOCX is still safer cross-platform.
- **Structured role-context lines help the scorecard parser.** Greenhouse's scorecard
  workflow benefits from a one-line summary under each job title describing scope
  ("Lead engineer for the payments fraud platform serving 12M MAU.") before the
  bullets.
- **Greenhouse AI semantic matching is good** — it bridges synonyms like React/JS or
  Postgres/PostgreSQL — but exact JD term match still scores higher.

**What still breaks here in 2026**:
- Text in images (still invisible)
- Multi-column layouts with shared horizontal lines spanning columns
- PDFs exported from web-based design tools with embedded webfont subsets that don't
  re-extract cleanly

---

## Lever

**Used by**: Mid-size tech and professional services. Owned by Employ Inc. since
2023; absorbed Gem's AI sourcing/ranking tech into LeverTRM.

**How it works**: Stores the parsed profile and the original file separately. The
parsed profile populates a recruiter-facing card view that is the recruiter's
primary view; the original PDF/DOCX is a secondary attachment.

**Specific tuning**:

- **Parse quality matters more here than in Greenhouse.** Because the recruiter sees
  the parsed card first, a corrupted parse means a corrupted first impression. The
  recruiter doesn't see the original document unless they click through.
- **No candidate-facing parse preview.** Workday and Greenhouse let candidates review
  parsed fields before submission in some configurations; Lever does not. What you
  submit is what the recruiter receives. Pre-submission parse-verification
  (`parse-verification.md`) is more important for Lever than for Greenhouse.
- **Full-text search over the candidate corpus.** Lever indexes the full resume text
  for recruiter Boolean search. Dense keyword coverage in the skills section pays off
  here — recruiters frequently filter by specific tool/skill keywords.
- **DOCX and PDF both work** at high accuracy. PDF is fine if it's vector-text.

**What still breaks here in 2026**:
- Text embedded as images (invisible)
- Tables, especially nested tables
- Non-standard fonts that don't subset cleanly into PDFs

---

## Oracle Taleo

**Used by**: Older enterprise, federal contractors, large healthcare systems, many
Fortune 500 still on legacy stacks. Declining share but still significant.

**How it works**: Older-generation parser using rule-based extraction. No semantic
matching by default — keyword matching is exact.

**Specific tuning**:

- **DOCX, always.** Taleo's PDF extraction is significantly weaker than its DOCX
  extraction. If you have a choice, choose DOCX.
- **ASCII-strict.** Smart quotes, em-dashes, and unusual Unicode characters
  occasionally corrupt the parse. When applying through Taleo, consider using
  straight quotes and ASCII hyphens in the rendered document.
- **Exact keyword match only.** Lacks the semantic matching that modern systems have.
  If the JD says "JavaScript" and your resume says "JS", you miss the keyword. Mirror
  JD vocabulary verbatim with extra discipline here.
- **Single column, no tables, no exceptions.** Taleo's parser is the least forgiving
  on layout violations of any of the six.
- **Standard section headings, no variants.** Stick to `Work Experience`,
  `Education`, `Skills`, `Certifications` — Taleo's heading-recognition list is
  smaller than modern parsers'.

**What still breaks here in 2026**:
- Multi-column layouts (20+ point parse-accuracy drop)
- Any PDF that wasn't generated from a word processor
- Unicode characters outside basic Latin
- Custom heading text

---

## iCIMS

**Used by**: 4,000+ employers, ~40% of Fortune 100 (IBM, Microsoft, Target, Uber,
UPS). Strong in retail, healthcare, hospitality, financial services.

**How it works**: Operates as a candidate profile system — the parsed version is the
recruiter's primary view. Boolean search over the full candidate index. iCIMS
Copilot (2024, GPT-4 via Azure OpenAI) layered on top for summarization and Role Fit
scoring; both layers read only the parsed output.

**Specific tuning**:

- **DOCX preferred.** iCIMS's PDF extraction has improved since 2024 but DOCX remains
  the safer choice for any document with non-trivial layout.
- **Exact terminology weights heavily** in iCIMS Copilot's Role Fit score. "JavaScript"
  and "JS" are scored differently. Mirror the posting verbatim.
- **Keyword density is more decisive** than in Greenhouse or Lever because of Boolean
  recruiter search over the full candidate corpus. A dense, well-grouped skills
  section helps significantly.
- **File size matters**: keep under 500 KB. Client-configured upload limits on iCIMS
  reject larger files silently — the candidate never knows the upload failed.

**What still breaks here in 2026**:
- Multi-column layouts
- Image-based PDFs (no OCR by default)
- Documents over 500 KB (silent rejection)
- iframe-rendered job listings causing data-extraction mismatches

---

## SmartRecruiters

**Used by**: Mid-market and enterprise, global. Common in Europe, retail, hospitality.

**How it works**: Modern parser, semantic matching, good multilingual support.
Generally forgiving on format.

**Specific tuning**:

- **DOCX or PDF both fine.** No strong preference; modern parser.
- **Multilingual posting**: SmartRecruiters handles non-English resumes well, but
  parsing accuracy still degrades on non-English documents. If applying through a
  non-English posting, submit in the JD's language and follow that locale's date
  format conventions.
- **Section heading flexibility**: handles "Professional Experience" /
  "Work History" / "Experience" interchangeably, unlike Taleo.

---

## Ashby

**Used by**: Modern tech startups (often Series A–C).

**How it works**: Modern parser, AI-native. Generally handles modern formatting well.

**Specific tuning**:

- DOCX or text-based PDF both fine.
- Particularly forgiving on hybrid layouts with sidebars (tested at ~85% accuracy on
  these).
- Still: single-column DOCX is the safe default.

---

## Cross-Platform Compatibility Matrix

When the target ATS is unknown, the format below scores ≥95% extraction accuracy on
all six major parsers in published 2026 testing:

```
Single-column DOCX
Calibri 11pt body, 14pt name, 12pt headings
0.75-1" margins
Standard section headings: Summary, Skills, Work Experience, Education, Certifications
Dates: Mon YYYY – Mon YYYY (Mon YYYY – Present for current)
Solid round bullets (•)
Contact block in body, no header/footer fields
No tables, no graphics, no text boxes
Filename: firstname-lastname-resume.docx
```

This is the default this skill produces when the target ATS is not specified.

## Per-Platform Adjustments Summary

| Platform | File | Critical adjustment |
|---|---|---|
| Workday | DOCX | Strict heading taxonomy; use ` – Present` with spaces; mirror target title for seniority |
| Greenhouse | DOCX or PDF | Add one-line role-context summary under each job title |
| Lever | DOCX or PDF | Run parse-verification before submitting — Lever doesn't show parse preview |
| Taleo | DOCX | ASCII-strict, exact-keyword-match, no exceptions on layout |
| iCIMS | DOCX | Mirror JD terminology exactly; keep under 500 KB |
| SmartRecruiters | DOCX or PDF | Match JD's locale conventions |
| Ashby | DOCX or PDF | Standard defaults work; hybrid layouts also fine |
