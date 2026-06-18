# Format Specification (DOCX/PDF)

The strict rules the rendered artifact must follow to survive the parser stage of
modern AI hiring pipelines. These rules are not aesthetic preferences — each one
maps to a documented parser failure mode in at least one major ATS (Workday,
Greenhouse, Lever, Taleo, iCIMS, SmartRecruiters).

## File Format

| Format | When to use | Why |
|---|---|---|
| **DOCX** | Default, and always when the posting doesn't specify. | Parsed most reliably across all six major ATS, especially Workday and Taleo. Recruiters can also annotate it directly. |
| **PDF** | Only when the posting explicitly requires it, or when sending to a human contact who'll forward it. | Modern parsers handle text-based PDFs at ~96% accuracy, but Workday and Taleo measurably lose section-extraction accuracy on PDFs vs. DOCX. Must be a native vector-text PDF — never a scanned/image PDF. |
| **TXT, RTF, ODT, HTML, Pages** | Never, unless explicitly requested. | Parser support is inconsistent or absent. |

**Filename**: `firstname-lastname-resume.docx` — lowercase, hyphenated, no spaces, no
version suffixes (`_FINAL_v3`, `_NEW`, `_updated`). Some ATS upload validators reject
filenames with special characters or excessive length.

**File size**: Under 500 KB. iCIMS in particular has client-configured upload limits
that reject larger files silently.

## Page Geometry

- **Margins**: 0.75" on all sides minimum, 1" preferred when the content fits.
  Narrower than 0.5" looks cluttered and can cause page-break confusion on some
  rendering engines.
- **Page size**: US Letter (8.5" × 11") for North American applications; A4 for
  everywhere else.
- **Page count**: 1 page if the candidate has under 8 years of relevant experience,
  2 pages otherwise. Senior/executive roles can justify 2 pages; never 3+ outside
  academic or federal contexts.
- **Orientation**: Portrait. Always.

## Layout

- **Single column.** Every section, every line. No multi-column layouts even when
  modern parsers handle them — Taleo and iCIMS drop parse accuracy by 20+ percentage
  points on multi-column documents.
- **No tables.** Use plain paragraphs with appropriate spacing. Tables — including
  invisible-border tables used for alignment — get serialized in unpredictable order
  by some parsers, scrambling section sequence.
- **No text boxes, sidebars, floating frames, or grouped objects.** Anything not
  inline in the document flow is at risk of being skipped or reordered.
- **No images, logos, photos, or graphics.** Including profile photos, company logos,
  decorative dividers, and icons. Image-embedded text is invisible to text parsers
  and OCR is unreliable on layered PDFs.
- **No headers or footers** containing extractable fields (name, contact info,
  dates). Many parsers drop header/footer content entirely. If a page number is
  needed on page 2, put it in the footer and accept that it may be dropped — it's
  not extractable signal anyway.

## Typography

- **Font family**: Calibri, Arial, Helvetica, Georgia, Times New Roman, or Lato.
  These ship with every operating system and PDF renderer; every parser handles
  them. Default to Calibri 11pt.
- **Font size**: Body 10–12pt; section headings 12–14pt; candidate name 14–18pt.
  Below 10pt is unparseable risk; above 12pt body wastes space.
- **Font weight**: Bold for the candidate name, section headings, employer names,
  and job titles. Use sparingly — bolding everything bolds nothing.
- **Italic**: For company taglines or role context where useful; not required.
- **No colored text** for body content. A single conservative accent color
  (navy `#1a3a5c`, dark grey `#333333`) on headings is acceptable but unnecessary.
  No yellow, no pastels, no gradients.
- **Underline**: Only for hyperlinks (LinkedIn, GitHub, personal site URLs).

## Section Headers (Exact Strings)

The parser segments the document on these heading keywords. Use them verbatim:

| Use | Acceptable variants |
|---|---|
| Summary | "Summary", "Professional Summary", "Profile" |
| Skills | "Skills", "Technical Skills", "Core Competencies" |
| Work Experience | "Work Experience", "Professional Experience", "Experience" |
| Education | "Education" |
| Certifications | "Certifications", "Licenses & Certifications" |
| Projects | "Projects", "Selected Projects" |
| Publications | "Publications" |
| Awards | "Awards", "Honors & Awards" |

**Never use**: "My Journey," "Where I've Been," "What I Do," "About Me," "Career
Story," or any narrative-style heading. Parsers classify those as biography blocks
and drop the contained keywords from the searchable index.

## Date Format

- **Format**: `Mon YYYY – Mon YYYY` with an en-dash or hyphen.
  Examples: `Mar 2022 – Apr 2025`, `Jan 2020 – Present`.
- **Current role**: Use the literal word `Present`. Avoid `Current` or `Now`;
  some parsers don't recognize them.
- **Never** use year-only ranges (`2022 – 2023`). Parsers acting conservatively
  may credit the tenure as 1 day, which then fails experience-threshold filters.
- **Never** use full numeric dates (`03/15/2022 – 04/30/2025`) — internationalization
  ambiguity (DD/MM vs. MM/DD) reduces parse reliability.
- **Locale**: Use the locale of the target region. North American applications:
  `Mar 2022`. European applications: `March 2022` or `03.2022`.

## Contact Block

The first ~3 lines of the document body (not header), in this order:

```
Jane Q. Candidate
Senior Software Engineer
jane.candidate@example.com  |  +1 415 555 0123  |  San Francisco, CA
linkedin.com/in/janecandidate  |  github.com/janecandidate  |  jane.dev
```

- **Name**: Bold, 14–18pt, first line.
- **Target role label**: Below the name, regular weight. This becomes the parser's
  best guess at "current desired role." Mirror the JD's role title here when honestly
  applicable.
- **Contact line**: Email, phone, location separated by pipes (`|`) or middle dots
  (`·`). All three on one line if they fit; two lines otherwise.
- **Links line**: LinkedIn, GitHub (if applicable), personal site. Display as
  `linkedin.com/in/handle` not the full `https://www.linkedin.com/in/handle/` — the
  full URL doesn't add parsing signal and clutters the line.
- **Hyperlinks**: Active hyperlinks on the URLs. Some parsers index the hyperlink
  target separately from the display text — both should point to the same place.

## Bullet Characters

- **Default**: Solid round bullet `•` (U+2022). Universally parsed.
- **Acceptable alternates**: Solid square `▪` (U+25AA), en-dash `–` (U+2013).
- **Never use**: Decorative symbols (✓, ★, ➤, →, ⚡, custom icons), Wingdings,
  Webdings, or icon-font characters. They render as garbage characters in plain-text
  extraction and break the bullet-list semantic in DOCX.

## Spacing

- **Line spacing**: 1.0–1.15 within paragraphs.
- **Section spacing**: 6–10pt before each section heading.
- **Bullet spacing**: 2–4pt between bullets within a role.
- **No blank lines** between bullets of the same role; use paragraph spacing instead.
  Blank lines confuse some parsers about whether the next line continues the bullet
  or starts a new section.

## Hyperlinks and Special Characters

- **Hyperlinks**: All URLs in the contact block should be active hyperlinks. URLs in
  the body (project links, publication DOIs) should also be active.
- **Email obfuscation**: Do not obfuscate (`jane [at] example [dot] com`). Parsers
  expect a standard `name@domain.tld` pattern and may fail extraction otherwise.
- **Smart quotes** ("curly quotes") render fine but can occasionally cause encoding
  issues in legacy ATS. If you see scrambled punctuation in the parse-check output,
  replace with straight quotes (`"`, `'`).
- **Em-dash, en-dash, ellipsis**: Use the actual Unicode characters (—, –, …) not
  ASCII approximations (--, ...). Modern parsers handle them; the rendered DOCX looks
  more professional.

## Structural Order (Default Hybrid)

1. **Contact block** (lines 1–3)
2. **Summary** (2–3 lines, no heading needed if the contact block is clearly
   delineated above — though a "Summary" heading is safer for parsers)
3. **Skills** (grouped by category, 4–6 groups)
4. **Work Experience** (reverse-chronological)
5. **Education**
6. **Certifications** (if any)
7. **Projects** (engineering roles only, if any)
8. **Publications / Awards / Languages** (only if relevant)

The skills-before-experience order ("hybrid") aligns with 2026 skills-first hiring
trends. Pure-chronological (Experience before Skills) is also fine. Functional
(Skills with no reverse-chronological history) is forbidden — see SKILL.md
anti-patterns.

## Locale Variations

- **US/Canada**: No photo, no date of birth, no marital status. Date format `Mon YYYY`.
- **UK/Ireland**: No photo, no date of birth. Date format `Month YYYY`. CV term used
  interchangeably with resume.
- **Continental Europe / EU**: Some countries still expect photo + DOB; check the
  posting. Europass format is sometimes requested explicitly — use it then.
- **Germany**: Often expects a photo, DOB, and signature. Check the posting.
- **Japan**: Rirekisho format is its own standard, not covered by this skill.

## Final Render Checklist

Before delivery, verify:

- [ ] Single column, no tables, no text boxes
- [ ] Contact info in the body, not header/footer
- [ ] Standard section headings, exact strings
- [ ] All dates in `Mon YYYY – Mon YYYY` format
- [ ] Solid round bullets, no decorative symbols
- [ ] Standard font (Calibri/Arial/Helvetica), 10–12pt body
- [ ] No images, logos, or graphics
- [ ] Filename in `firstname-lastname-resume.docx` form
- [ ] Under 500 KB
- [ ] Parse-verification round-trip clean (see `parse-verification.md`)
