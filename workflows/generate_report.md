# Generate Report Workflow

## Objective
Produce a branded XERXES AI PDF competitor analysis report from structured analysis data.

## Tool
`tools/generate_pdf_report.py`

## Prerequisites
- `.tmp/analysis.json` must exist (produced by `analyze_competitors.py`)
- `brand_assets/XERXES AI Logo.png` must exist
- `reports/` directory is created automatically if missing

## Usage
```
python tools/generate_pdf_report.py
```

## Report Structure
| Section | Content |
|---|---|
| Cover Page | XERXES AI logo, dark navy background, report title, date |
| Executive Summary | One-paragraph overview of the analysis scope |
| Competitor Breakdowns | Positioning, audience, services, pricing, strengths/weaknesses per competitor |
| Key Patterns & Themes | Recurring trends observed across competitors |
| Opportunities for XERXES AI | Specific gaps and differentiation angles |
| Actionable Recommendations | Numbered list of strategic actions |
| Ongoing Monitoring Plan | Monthly tracking schedule and what to watch |

## Brand Specifications Applied
| Element | Value |
|---|---|
| Background (cover) | Dark Navy `#0A247C` |
| Section headers | Dark Navy `#0A247C` with white text |
| Accent lines | Neon Blue `#000CFF` |
| Secondary accents | Deep Cyan `#0089FF` |
| Body text | Dark gray on white |
| Logo placement | Cover page (large) + every page header (small) |

## Output
`reports/competitor_analysis_YYYY-MM-DD.pdf`

Each run generates a new dated file — previous reports are not overwritten.

## Troubleshooting
| Issue | Fix |
|---|---|
| Logo not rendering | Confirm `brand_assets/XERXES AI Logo.png` exists and is a valid PNG |
| `reportlab` not found | Run `pip install reportlab pillow` |
| Blank sections in PDF | Inspect `.tmp/analysis.json` for missing or empty fields |
| PDF layout looks broken | Check that `A4` page size is set and margins are not over-specified |
