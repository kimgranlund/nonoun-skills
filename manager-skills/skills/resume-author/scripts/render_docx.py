#!/usr/bin/env python3
"""
render_docx.py — Render a JSON Resume document to a parser-friendly DOCX.

Produces a single-column DOCX that follows the format-spec.md rules by
construction:
  - Single column, no tables, no text boxes
  - Contact info in the document body (not header/footer)
  - Standard section headers (Summary, Skills, Work Experience, Education, ...)
  - Calibri 11pt body, 14pt name, 12pt section headings
  - 0.75" margins
  - Mon YYYY – Mon YYYY date format
  - Solid round bullet (U+2022)
  - Filename: firstname-lastname-resume.docx

Usage:
    python render_docx.py resume.json [output.docx]

Requires:
    python-docx (pip install python-docx)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx", file=sys.stderr)
    sys.exit(1)


# --- Format constants (match format-spec.md) ---

FONT_FAMILY = "Calibri"
BODY_SIZE = Pt(11)
NAME_SIZE = Pt(16)
LABEL_SIZE = Pt(12)
HEADING_SIZE = Pt(12)
JOB_TITLE_SIZE = Pt(11)
MARGIN = Inches(0.75)
BULLET_CHAR = "•"
DATE_SEPARATOR = " – "   # en-dash with spaces
SECTION_BEFORE = Pt(10)
SECTION_AFTER = Pt(4)
BULLET_AFTER = Pt(2)


# --- Date formatting ---

def format_date(iso_date: str | None, is_current: bool = False) -> str:
    """Convert a YYYY-MM (or YYYY-MM-DD) ISO date to 'Mon YYYY' format.

    Returns 'Present' if is_current is True and iso_date is missing.
    """
    if is_current and not iso_date:
        return "Present"
    if not iso_date:
        return ""
    # Try YYYY-MM-DD first, then YYYY-MM, then YYYY
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            d = datetime.strptime(iso_date, fmt)
            if fmt == "%Y":
                # Year-only is a parse risk; warn but render as 'Jan YYYY'
                print(f"Warning: year-only date '{iso_date}' renders ambiguously; "
                      f"use YYYY-MM precision.", file=sys.stderr)
                return d.strftime("%b %Y")
            return d.strftime("%b %Y")
        except ValueError:
            continue
    return iso_date  # Fall through: render as-is


def format_date_range(start: str | None, end: str | None) -> str:
    """Format a date range. End=None or 'present' becomes 'Present'."""
    is_current = (end is None) or (isinstance(end, str) and end.lower() == "present")
    start_str = format_date(start)
    end_str = "Present" if is_current else format_date(end)
    if start_str and end_str:
        return f"{start_str}{DATE_SEPARATOR}{end_str}"
    return start_str or end_str or ""


# --- Document helpers ---

def set_margins(doc: Document) -> None:
    for section in doc.sections:
        section.left_margin = MARGIN
        section.right_margin = MARGIN
        section.top_margin = MARGIN
        section.bottom_margin = MARGIN


def add_run(p, text: str, *, bold: bool = False, size: Pt | None = None,
            italic: bool = False) -> None:
    run = p.add_run(text)
    run.font.name = FONT_FAMILY
    # Ensure Calibri is set for East Asian + complex scripts too
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:eastAsia"), FONT_FAMILY)
    run.font.size = size or BODY_SIZE
    run.bold = bold
    run.italic = italic


def add_paragraph(doc: Document, *, space_before: Pt | None = None,
                  space_after: Pt | None = None, alignment=None):
    p = doc.add_paragraph()
    if space_before is not None:
        p.paragraph_format.space_before = space_before
    if space_after is not None:
        p.paragraph_format.space_after = space_after
    if alignment is not None:
        p.alignment = alignment
    return p


def add_section_heading(doc: Document, text: str) -> None:
    p = add_paragraph(doc, space_before=SECTION_BEFORE, space_after=SECTION_AFTER)
    add_run(p, text.upper(), bold=True, size=HEADING_SIZE)
    # Add a bottom border under the heading
    pPr = p._element.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "808080")
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_bullet(doc: Document, text: str) -> None:
    p = add_paragraph(doc, space_after=BULLET_AFTER)
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    add_run(p, f"{BULLET_CHAR}  {text}")


# --- Section renderers ---

def render_basics(doc: Document, basics: dict) -> None:
    """Contact block: name, target role, contact line, links line."""
    # Name
    p = add_paragraph(doc, space_after=Pt(0))
    add_run(p, basics.get("name", ""), bold=True, size=NAME_SIZE)

    # Target role label (sub-line under name)
    label = basics.get("label")
    if label:
        p = add_paragraph(doc, space_after=Pt(4))
        add_run(p, label, size=LABEL_SIZE)

    # Contact line: email | phone | location
    contact_parts = []
    if basics.get("email"):
        contact_parts.append(basics["email"])
    if basics.get("phone"):
        contact_parts.append(basics["phone"])
    location = basics.get("location") or {}
    if location:
        loc_str = ", ".join(filter(None, [location.get("city"), location.get("region")]))
        if loc_str:
            contact_parts.append(loc_str)
    if contact_parts:
        p = add_paragraph(doc, space_after=Pt(2))
        add_run(p, "  |  ".join(contact_parts))

    # Links line: profiles + url
    link_parts = []
    if basics.get("url"):
        # Strip protocol for compactness; parsers still index it
        link_parts.append(basics["url"].replace("https://", "").replace("http://", ""))
    for profile in basics.get("profiles", []) or []:
        url = profile.get("url", "")
        if url:
            link_parts.append(url.replace("https://", "").replace("http://", ""))
    if link_parts:
        p = add_paragraph(doc, space_after=Pt(2))
        add_run(p, "  |  ".join(link_parts))

    # Summary
    summary = basics.get("summary")
    if summary:
        add_section_heading(doc, "Summary")
        p = add_paragraph(doc, space_after=Pt(4))
        add_run(p, summary)


def render_skills(doc: Document, skills: list) -> None:
    if not skills:
        return
    add_section_heading(doc, "Skills")
    for group in skills:
        name = group.get("name", "")
        keywords = group.get("keywords") or []
        if not keywords:
            continue
        p = add_paragraph(doc, space_after=Pt(2))
        if name:
            add_run(p, f"{name}: ", bold=True)
        add_run(p, ", ".join(keywords))


def render_work(doc: Document, work: list) -> None:
    if not work:
        return
    add_section_heading(doc, "Work Experience")
    for role in work:
        # Title line: Position | Employer | Date range
        p = add_paragraph(doc, space_before=Pt(4), space_after=Pt(0))
        position = role.get("position", "")
        employer = role.get("name", "")
        dates = format_date_range(role.get("startDate"), role.get("endDate"))
        title_parts = [t for t in [position, employer, dates] if t]
        if title_parts:
            # Position + employer bold; date plain
            if position:
                add_run(p, position, bold=True, size=JOB_TITLE_SIZE)
            if employer:
                add_run(p, "  |  ", size=JOB_TITLE_SIZE)
                add_run(p, employer, bold=True, size=JOB_TITLE_SIZE)
            if dates:
                add_run(p, "  |  ", size=JOB_TITLE_SIZE)
                add_run(p, dates, size=JOB_TITLE_SIZE)

        # Optional location line
        location = role.get("location")
        if location:
            p = add_paragraph(doc, space_after=Pt(2))
            add_run(p, location, italic=True)

        # Role summary (one-line context)
        summary = role.get("summary")
        if summary:
            p = add_paragraph(doc, space_after=Pt(2))
            add_run(p, summary)

        # Highlights (bullets)
        for highlight in role.get("highlights") or []:
            add_bullet(doc, highlight)


def render_education(doc: Document, education: list) -> None:
    if not education:
        return
    add_section_heading(doc, "Education")
    for edu in education:
        p = add_paragraph(doc, space_before=Pt(2), space_after=Pt(0))
        degree = " ".join(filter(None, [edu.get("studyType", ""), edu.get("area", "")])).strip()
        institution = edu.get("institution", "")
        dates = format_date_range(edu.get("startDate"), edu.get("endDate"))
        if degree:
            add_run(p, degree, bold=True)
        if institution:
            add_run(p, "  |  ")
            add_run(p, institution, bold=True)
        if dates:
            add_run(p, "  |  ")
            add_run(p, dates)
        if edu.get("score"):
            p = add_paragraph(doc, space_after=Pt(2))
            add_run(p, f"GPA: {edu['score']}")
        if edu.get("courses"):
            p = add_paragraph(doc, space_after=Pt(2))
            add_run(p, "Relevant coursework: ", bold=True)
            add_run(p, ", ".join(edu["courses"]))


def render_projects(doc: Document, projects: list) -> None:
    if not projects:
        return
    add_section_heading(doc, "Projects")
    for proj in projects:
        p = add_paragraph(doc, space_before=Pt(4), space_after=Pt(0))
        if proj.get("name"):
            add_run(p, proj["name"], bold=True)
        dates = format_date_range(proj.get("startDate"), proj.get("endDate"))
        if dates:
            add_run(p, "  |  ")
            add_run(p, dates)
        if proj.get("description"):
            p = add_paragraph(doc, space_after=Pt(2))
            add_run(p, proj["description"])
        if proj.get("url"):
            p = add_paragraph(doc, space_after=Pt(2))
            url = proj["url"].replace("https://", "").replace("http://", "")
            add_run(p, url)
        for highlight in proj.get("highlights") or []:
            add_bullet(doc, highlight)
        keywords = proj.get("keywords") or []
        if keywords:
            p = add_paragraph(doc, space_after=Pt(2))
            add_run(p, "Keywords: ", bold=True)
            add_run(p, ", ".join(keywords))


def render_certificates(doc: Document, certificates: list) -> None:
    if not certificates:
        return
    add_section_heading(doc, "Certifications")
    for cert in certificates:
        p = add_paragraph(doc, space_after=Pt(2))
        if cert.get("name"):
            add_run(p, cert["name"], bold=True)
        if cert.get("issuer"):
            add_run(p, f"  |  {cert['issuer']}")
        if cert.get("date"):
            add_run(p, f"  |  {format_date(cert['date'])}")


# --- Main ---

def render(resume: dict, output_path: Path) -> None:
    doc = Document()
    set_margins(doc)

    # Set default style to Calibri
    style = doc.styles["Normal"]
    style.font.name = FONT_FAMILY
    style.font.size = BODY_SIZE

    render_basics(doc, resume.get("basics") or {})
    render_skills(doc, resume.get("skills") or [])
    render_work(doc, resume.get("work") or [])
    render_education(doc, resume.get("education") or [])
    render_certificates(doc, resume.get("certificates") or [])
    render_projects(doc, resume.get("projects") or [])

    doc.save(str(output_path))


def default_output_path(resume: dict, input_path: Path) -> Path:
    name = (resume.get("basics") or {}).get("name", "")
    if name:
        slug = "-".join(name.lower().replace(".", "").split())
        return input_path.parent / f"{slug}-resume.docx"
    return input_path.with_suffix(".docx")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    input_path = Path(argv[1])
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        return 1
    resume = json.loads(input_path.read_text(encoding="utf-8"))
    output_path = Path(argv[2]) if len(argv) >= 3 else default_output_path(resume, input_path)
    render(resume, output_path)
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
