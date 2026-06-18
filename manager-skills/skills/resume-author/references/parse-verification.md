# Parse Verification

The plain-text round-trip check that turns the parse-fidelity premise of this skill
from an assertion into an inspectable guarantee. Cheap (60 seconds), catches the
majority of preventable parser failures, and is required before delivery.

## The Round-Trip

What the parser sees is approximately what a plain-text extraction sees. If you can
copy/paste the rendered DOCX or PDF into a plain text editor and read it cleanly,
the parser can probably extract it cleanly too. If the extraction is scrambled, the
parser will scramble it too.

### Method 1: Copy/paste (manual, no tools needed)

1. Open the rendered DOCX in Word, LibreOffice, or Google Docs (or the PDF in any
   viewer).
2. Select all (Cmd/Ctrl+A).
3. Copy (Cmd/Ctrl+C).
4. Paste into a plain text editor — TextEdit (in Plain Text mode), Notepad, VS Code
   with an empty `.txt` file, or `pbpaste > parse-check.txt` on macOS.
5. Read the result top to bottom.

### Method 2: Scripted extraction

Use the bundled script (works on DOCX and text-based PDF):

```bash
python scripts/extract_plaintext.py firstname-lastname-resume.docx
# writes firstname-lastname-parse-check.txt
```

The scripted method is preferred because it deterministically produces the file the
candidate should review, and it skips the clipboard layer that can add formatting
on some platforms.

## What to Inspect

Walk the extracted text top-to-bottom and check each row:

| Inspection | What clean output looks like | What failure looks like |
|---|---|---|
| **Reading order** | Top of document → bottom, left-to-right within lines | Sections appear out of order, or contact info appears mid-document |
| **Contact block** | Name, target role label, email, phone, location, links — all on the first 3–5 lines | Missing email or phone, name on a different line than expected, links lost |
| **Section headings** | "Summary", "Skills", "Work Experience", "Education" present as their own lines | Headings merged into adjacent text, or missing entirely |
| **Job titles + employers + dates** | All three on adjacent lines per role | Job title separated from its employer or its dates by an unrelated line |
| **Date format** | `Mar 2022 – Apr 2025` style, with "Present" for current role | Just years, garbled hyphens, or `Mar 2022\nApr 2025` (split across lines) |
| **Skills section** | Flat readable list, comma-separated, category labels intact | Skills scrambled with employer names, or categories lost |
| **Bullets** | `•` character preserved at the start of each bullet, OR clearly indented runs | `?` or `\u2022` literal text, or bullets running together as one paragraph |
| **Special characters** | Em-dashes, smart quotes, accented characters render correctly | Garbage characters (`?`, `\xc2`, mojibake) or missing punctuation |

## Failure-Mode Diagnostics

Each scramble pattern points to a specific format problem. Fix the source, re-render,
re-verify.

### "Sections appear out of order"

**Cause**: Multi-column layout, table-based layout, or text boxes / sidebars in the
source DOCX.

**Fix**: Move to a single-column layout. Replace tables with paragraph styles.
Inline anything that was in a sidebar.

### "Contact info is missing from the extracted text"

**Cause**: Contact block lives in the document's header or footer region, not the
body.

**Fix**: Move all contact information into the document body (the first 3 lines of
content), even if visually it looks like a header. The DOCX `header` and `footer`
regions are different objects from the body and get dropped by many parsers.

### "Bullets show up as `?` or garbage characters"

**Cause**: A decorative bullet glyph (Wingdings character, emoji, custom symbol)
that doesn't round-trip through plain text.

**Fix**: Use the standard `•` (U+2022) solid round bullet. Replace any decorative
bullets globally in the source.

### "Skills section is scrambled or fused with the next section"

**Cause**: Skills laid out as a table or in multiple columns, OR section heading is
non-standard (`"My Toolkit"` instead of `"Skills"`) and the parser doesn't recognize
the boundary.

**Fix**: Render skills as a single-column block with a standard `Skills` heading.
Use comma-separated lists, not table cells.

### "Dates appear on a different line than the job title"

**Cause**: Date positioned with a right-tab to the far right of the line, or in a
right-aligned column. Plain-text extraction loses the visual alignment and the date
ends up on the next line.

**Fix**: Place the date inline on the same line as employer + title, with a
consistent delimiter — `Senior Engineer, FinTech Co | Mar 2022 – Apr 2025` reads
cleanly. Or use a separate dedicated line for the date that's visually clearly
attached to its role.

### "Smart quotes / em-dashes turn into `?` or garbled characters"

**Cause**: Encoding mismatch between the DOCX/PDF and the plain-text export. Usually
harmless for the recruiter but indicates the parser may also struggle, especially
older parsers (Taleo, legacy iCIMS).

**Fix**: For Taleo targets specifically, switch to ASCII characters (straight
quotes, ASCII hyphens). For modern targets, this is usually cosmetic.

### "Job title and employer have merged together"

**Cause**: No clear delimiter between the two — they're in adjacent text boxes, or
on the same line with no separator.

**Fix**: Use a clear visual + textual separator: `Senior Software Engineer · FinTech
Co` or place each on its own line.

### "Headings have been swallowed into adjacent paragraphs"

**Cause**: Heading style not applied; the text is just bold body text on a line.
Some parsers detect heading-vs-body based on the DOCX paragraph style, not visual
weight.

**Fix**: Apply the DOCX "Heading 2" or "Heading 3" style to section headings, not
just bold text. The script `render_docx.py` does this automatically.

## What Clean Output Looks Like

A passing parse-check.txt should read like a tidy outline of the candidate. Here is
an abbreviated example of clean output:

```
Jane Q. Candidate
Senior Software Engineer
jane.candidate@example.com | +1 415 555 0123 | San Francisco, CA
linkedin.com/in/janecandidate | github.com/janecandidate | jane.dev

SUMMARY
Senior software engineer with 9 years building distributed data infrastructure.
Strong in Python, Go, and Kafka/Flink streaming systems; previously lead engineer
on a real-time fraud platform serving 12M MAU. Reduced fraud false-positive rate
from 8.2% to 2.1% over two years.

SKILLS
Languages: Python, Go, SQL, TypeScript, Bash
Distributed: Apache Kafka, Apache Flink, Apache Spark, Redis, PostgreSQL, Cassandra
Cloud & Infra: AWS (EC2, S3, EKS, RDS, Kinesis), Terraform, Docker, Kubernetes
ML & Observability: scikit-learn, XGBoost, Datadog, OpenTelemetry, Grafana

WORK EXPERIENCE

Senior Software Engineer | FinTech Co | Mar 2022 – Apr 2025
San Francisco, CA
Lead engineer for the real-time payments fraud detection platform serving 12M monthly active users.
• Reduced fraud false-positive rate from 8.2% to 2.1% (measured by 90-day chargeback rate) by replacing rule-based scoring with a gradient-boosted model on a 200-feature training set.
• Shipped event-streaming pipeline (Kafka, Apache Flink) handling 2B events/day, cutting end-to-end fraud-decision latency from 1.4s to 180ms.
• Led a team of 5 engineers and ran the on-call rotation; reduced P1 incidents by 60% over 18 months through runbook standardization and observability work (Datadog, OpenTelemetry).

[...]

EDUCATION

Master of Science, Computer Science | Stanford University | Sep 2014 – Jun 2016
GPA: 3.9/4.0
Relevant coursework: Distributed Systems, Machine Learning
```

If this is roughly what the candidate's extracted text looks like, the parse is
clean. Deliver the document.

## When the Round-Trip Fails Repeatedly

If multiple iterations of format fixes still produce a scrambled parse-check, the
source document has structural problems too deep to fix in place. Two options:

1. **Re-render from the JSON Resume source using `scripts/render_docx.py`.** The
   script enforces the format spec by construction; it won't produce a layout that
   fails the round-trip if the JSON is valid.
2. **Start the DOCX from a known-good template** (a previously-passing document)
   and copy content over as plain text, then re-apply styles. Faster than
   debugging a problem template.

Never deliver a resume whose parse-check is visibly broken. The check is the only
inspectable evidence the parse-fidelity premise of this skill holds for this
particular document.
