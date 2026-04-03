#!/usr/bin/env python3
"""
Generate a branded XERXES AI competitor analysis PDF report.
Input:  .tmp/analysis.json
Output: reports/competitor_analysis_YYYY-MM-DD.pdf

See workflows/generate_report.md for full documentation.
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP_DIR = ROOT / ".tmp"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)
BRAND_DIR = ROOT / "brand_assets"

# ── Brand Colors ──────────────────────────────────────────────────────────────
try:
    from reportlab.lib import colors

    DARK_NAVY = colors.HexColor("#0A247C")
    NEON_BLUE = colors.HexColor("#000CFF")
    DEEP_CYAN = colors.HexColor("#0089FF")
    WHITE = colors.white
    LIGHT_GRAY = colors.HexColor("#F5F7FA")
    DARK_GRAY = colors.HexColor("#2D3748")
    MID_GRAY = colors.HexColor("#718096")
    RED_ACCENT = colors.HexColor("#C53030")
except ImportError:
    print("ERROR: reportlab is not installed.")
    print("Run: pip install reportlab pillow")
    sys.exit(1)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_logo_path():
    for fname in ["XERXES AI Logo.png", "XERXESAI Logo.png", "logo.png"]:
        p = BRAND_DIR / fname
        if p.exists():
            return str(p)
    return None


# ── Cover Page Flowable ───────────────────────────────────────────────────────

class CoverPage(Flowable):
    def __init__(self, title, subtitle, report_date, logo_path):
        Flowable.__init__(self)
        self.title = title
        self.subtitle = subtitle
        self.report_date = report_date
        self.logo_path = logo_path
        self.width = PAGE_WIDTH
        self.height = PAGE_HEIGHT

    def draw(self):
        c = self.canv
        w, h = PAGE_WIDTH, PAGE_HEIGHT

        # Dark navy full-page background
        c.setFillColor(DARK_NAVY)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # Top accent bar
        c.setFillColor(NEON_BLUE)
        c.rect(0, h - 8 * mm, w, 8 * mm, fill=1, stroke=0)

        # Bottom accent bar
        c.setFillColor(DEEP_CYAN)
        c.rect(0, 0, w, 6 * mm, fill=1, stroke=0)

        # Logo
        if self.logo_path and os.path.exists(self.logo_path):
            img_w, img_h = 110 * mm, 55 * mm
            x = (w - img_w) / 2
            y = h * 0.54
            c.drawImage(
                self.logo_path, x, y,
                width=img_w, height=img_h,
                preserveAspectRatio=True, mask="auto",
            )

        # Divider line under logo
        c.setStrokeColor(DEEP_CYAN)
        c.setLineWidth(1.5)
        c.line(MARGIN, h * 0.50, w - MARGIN, h * 0.50)

        # Report title
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(w / 2, h * 0.42, self.title)

        # Subtitle
        c.setFillColor(DEEP_CYAN)
        c.setFont("Helvetica", 13)
        c.drawCentredString(w / 2, h * 0.36, self.subtitle)

        # Meta line
        c.setFillColor(colors.HexColor("#A0AEC0"))
        c.setFont("Helvetica", 10)
        c.drawCentredString(w / 2, h * 0.22, f"Prepared by XERXES AI  •  {self.report_date}")
        c.drawCentredString(w / 2, h * 0.18, "Confidential — For Internal Use Only")


# ── Styles ────────────────────────────────────────────────────────────────────

def build_styles():
    return {
        "h1": ParagraphStyle(
            "h1", fontName="Helvetica-Bold", fontSize=17,
            textColor=DARK_NAVY, spaceAfter=4, spaceBefore=10,
        ),
        "h2": ParagraphStyle(
            "h2", fontName="Helvetica-Bold", fontSize=12,
            textColor=WHITE, backColor=DARK_NAVY,
            spaceAfter=4, spaceBefore=8,
            leftIndent=8, rightIndent=8, leading=20,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=10,
            textColor=DARK_GRAY, spaceAfter=4, leading=15,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=10,
            textColor=DARK_GRAY, spaceAfter=3, leading=14, leftIndent=14,
        ),
        "label": ParagraphStyle(
            "label", fontName="Helvetica-Bold", fontSize=8,
            textColor=DEEP_CYAN, spaceAfter=2, spaceBefore=4,
        ),
    }


# ── Page Header / Footer ──────────────────────────────────────────────────────

def make_header_footer(logo_path):
    def header_footer(canvas, doc):
        canvas.saveState()

        # Header bar
        canvas.setFillColor(DARK_NAVY)
        canvas.rect(0, PAGE_HEIGHT - 16 * mm, PAGE_WIDTH, 16 * mm, fill=1, stroke=0)

        if logo_path and os.path.exists(logo_path):
            canvas.drawImage(
                logo_path, MARGIN, PAGE_HEIGHT - 13 * mm,
                width=28 * mm, height=9 * mm,
                preserveAspectRatio=True, mask="auto",
            )

        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(
            PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 10 * mm,
            "Competitor Analysis Report — Confidential",
        )

        # Footer bar
        canvas.setFillColor(DARK_NAVY)
        canvas.rect(0, 0, PAGE_WIDTH, 10 * mm, fill=1, stroke=0)

        canvas.setFillColor(DEEP_CYAN)
        canvas.rect(0, 0, PAGE_WIDTH, 2 * mm, fill=1, stroke=0)

        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(PAGE_WIDTH / 2, 3.5 * mm, f"XERXES AI  •  Page {doc.page}")

        canvas.restoreState()

    return header_footer


# ── Content Builders ──────────────────────────────────────────────────────────

def bullet_items(items, styles):
    return [Paragraph(f"•  {item}", styles["bullet"]) for item in items]


def section_header(title, styles):
    return [Spacer(1, 4 * mm), Paragraph(title, styles["h2"]), Spacer(1, 3 * mm)]


def competitor_section(comp, styles):
    elements = []
    elements += section_header(comp.get("name", "Unknown Competitor"), styles)

    url = comp.get("url", "")
    if url:
        elements.append(Paragraph(f"<b>Website:</b> {url}", styles["body"]))
        elements.append(Spacer(1, 2 * mm))

    for field, label in [
        ("positioning", "POSITIONING"),
        ("target_audience", "TARGET AUDIENCE"),
        ("pricing", "PRICING"),
    ]:
        value = comp.get(field, "")
        if value:
            elements.append(Paragraph(label, styles["label"]))
            elements.append(Paragraph(value, styles["body"]))
            elements.append(Spacer(1, 2 * mm))

    services = comp.get("services", [])
    if services:
        elements.append(Paragraph("SERVICES", styles["label"]))
        elements += bullet_items(services, styles)
        elements.append(Spacer(1, 2 * mm))

    strengths = comp.get("strengths", [])
    weaknesses = comp.get("weaknesses", [])

    if strengths or weaknesses:
        col_w = (PAGE_WIDTH - 2 * MARGIN - 4 * mm) / 2

        header_row = [
            Paragraph("STRENGTHS", ParagraphStyle("sh", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
            Paragraph("WEAKNESSES", ParagraphStyle("wh", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
        ]
        rows = [header_row]

        for i in range(max(len(strengths), len(weaknesses))):
            s = Paragraph(f"+ {strengths[i]}", styles["bullet"]) if i < len(strengths) else Paragraph("", styles["body"])
            w = Paragraph(f"− {weaknesses[i]}", styles["bullet"]) if i < len(weaknesses) else Paragraph("", styles["body"])
            rows.append([s, w])

        table = Table(rows, colWidths=[col_w, col_w])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), DARK_NAVY),
            ("BACKGROUND", (1, 0), (1, 0), RED_ACCENT),
            ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 4 * mm))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0")))
    return elements


def monitoring_table(styles):
    col_w = PAGE_WIDTH - 2 * MARGIN - 4 * mm
    rows = [
        [Paragraph("<b>Frequency</b>", styles["body"]), Paragraph("<b>Action</b>", styles["body"])],
        [Paragraph("Monthly", styles["body"]), Paragraph("Re-run full competitor analysis pipeline", styles["body"])],
        [Paragraph("Monthly", styles["body"]), Paragraph("Check competitor pricing pages for updates", styles["body"])],
        [Paragraph("Monthly", styles["body"]), Paragraph("Review new messaging and service offerings", styles["body"])],
        [Paragraph("Quarterly", styles["body"]), Paragraph("Expand competitor list to capture new market entrants", styles["body"])],
    ]
    table = Table(rows, colWidths=[col_w * 0.22, col_w * 0.78])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


# ── Main Builder ──────────────────────────────────────────────────────────────

def build_report(analysis, output_path, logo_path):
    styles = build_styles()
    ctx = analysis.get("business_context", {})
    report_date = analysis.get("generated_at", str(date.today()))

    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=22 * mm,
        bottomMargin=16 * mm,
    )

    cover_frame = Frame(0, 0, PAGE_WIDTH, PAGE_HEIGHT, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    cover_template = PageTemplate(id="cover", frames=[cover_frame])

    content_frame = Frame(MARGIN, 12 * mm, PAGE_WIDTH - 2 * MARGIN, PAGE_HEIGHT - 30 * mm)
    content_template = PageTemplate(
        id="content",
        frames=[content_frame],
        onPage=make_header_footer(logo_path),
    )

    doc.addPageTemplates([cover_template, content_template])

    story = []

    # Cover
    story.append(CoverPage(
        title="Competitor Analysis Report",
        subtitle=f"AI Automation Market  |  SMB Segment  |  {report_date}",
        report_date=report_date,
        logo_path=logo_path,
    ))
    story.append(NextPageTemplate("content"))
    story.append(PageBreak())

    # Executive Summary
    story.append(Paragraph("Executive Summary", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=NEON_BLUE, spaceAfter=6))
    story.append(Paragraph(
        f"This report provides a competitive landscape analysis for <b>{ctx.get('company_name', 'XERXES AI')}</b>, "
        f"which provides {ctx.get('service', 'AI automation services')} to {ctx.get('target_market', 'SMBs')}. "
        f"Three key competitors were identified and analyzed across positioning, services, pricing, strengths, and weaknesses. "
        f"Strategic opportunities and actionable recommendations are included.",
        styles["body"],
    ))
    story.append(Spacer(1, 6 * mm))

    # Competitor Breakdowns
    story.append(Paragraph("Competitor Breakdowns", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=NEON_BLUE, spaceAfter=6))
    for comp in analysis.get("competitors", []):
        story += competitor_section(comp, styles)
        story.append(Spacer(1, 4 * mm))

    story.append(PageBreak())

    # Key Patterns
    story.append(Paragraph("Key Patterns & Themes", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=NEON_BLUE, spaceAfter=6))
    story.append(Paragraph("Recurring patterns observed across the competitive landscape:", styles["body"]))
    story += bullet_items(analysis.get("patterns", []), styles)
    story.append(Spacer(1, 6 * mm))

    # Opportunities
    story.append(Paragraph("Opportunities for XERXES AI", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=NEON_BLUE, spaceAfter=6))
    story.append(Paragraph("Areas where XERXES AI can differentiate and capture market share:", styles["body"]))
    story += bullet_items(analysis.get("opportunities", []), styles)
    story.append(Spacer(1, 6 * mm))

    # Recommendations
    story.append(Paragraph("Actionable Recommendations", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=NEON_BLUE, spaceAfter=6))
    for i, rec in enumerate(analysis.get("recommendations", []), 1):
        story.append(Paragraph(f"{i}.  {rec}", styles["bullet"]))
        story.append(Spacer(1, 2 * mm))
    story.append(Spacer(1, 6 * mm))

    # Monitoring Plan
    story.append(Paragraph("Ongoing Monitoring Plan", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=NEON_BLUE, spaceAfter=6))
    plan_text = analysis.get("monitoring_plan", "Re-run this analysis monthly to track competitor changes.")
    story.append(Paragraph(plan_text, styles["body"]))
    story.append(Spacer(1, 4 * mm))
    story.append(monitoring_table(styles))

    doc.build(story)
    print(f"Report saved to: {output_path}")


def main():
    analysis_path = TMP_DIR / "analysis.json"
    if not analysis_path.exists():
        print("ERROR: .tmp/analysis.json not found.")
        print("Run: python tools/analyze_competitors.py")
        sys.exit(1)

    analysis = load_json(analysis_path)
    logo_path = get_logo_path()

    if not logo_path:
        print("Warning: Logo not found in brand_assets/. Report will be generated without logo.")

    report_date = analysis.get("generated_at", str(date.today()))
    out_path = REPORTS_DIR / f"competitor_analysis_{report_date}.pdf"

    print("Generating branded PDF report...")
    build_report(analysis, out_path, logo_path)


if __name__ == "__main__":
    main()
