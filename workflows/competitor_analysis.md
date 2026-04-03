# Competitor Analysis Workflow

## Objective
Identify 3 relevant AI automation competitors targeting SMBs, analyze their positioning and offerings, and produce a branded XERXES AI PDF report.

## Trigger
Run on-demand or monthly for ongoing monitoring.

## Required Inputs
- `business_context.json` — XERXES AI's current positioning and service description
- `ANTHROPIC_API_KEY` in `.env` — required for the analysis step
- `brand_assets/XERXES AI Logo.png` — used in the PDF report

## Steps

### 1. Competitor Discovery
```
python tools/discover_competitors.py
```
- Searches DuckDuckGo for AI automation competitors targeting SMBs
- Outputs: `.tmp/competitors.json` with 3 competitors (name, URL, description)
- **If fewer than 3 found:** Check internet connection; adjust search queries in `discover_competitors.py`

### 2. Website Scraping
Run for each competitor in `.tmp/competitors.json`:
```
python tools/scrape_website.py <url> "<competitor_name>"
```
Or let the full pipeline handle this automatically (Step 5).

- Scrapes homepage, pricing, services, and about pages
- Outputs: `.tmp/<slug>_data.json` per competitor
- **If a page fails:** Script logs a warning and continues — partial data is still usable
- **Rate limits:** 1-second pause between subpage requests; increase `time.sleep()` if blocked

### 3. AI Analysis
```
python tools/analyze_competitors.py
```
- Requires `ANTHROPIC_API_KEY` in `.env`
- Sends all competitor data to Claude and returns structured insights
- Outputs: `.tmp/analysis.json`
- **If no API key:** Add `ANTHROPIC_API_KEY=your_key` to `.env` and re-run

### 4. PDF Report Generation
```
python tools/generate_pdf_report.py
```
- Reads `.tmp/analysis.json`
- Applies XERXES AI branding (dark navy, neon blue accents, logo)
- Outputs: `reports/competitor_analysis_YYYY-MM-DD.pdf`

### 5. Full Pipeline (Recommended)
```
python tools/run_analysis.py
```
Runs all 4 steps in sequence with error handling. Start here unless debugging a specific step.

## Outputs
| File | Description |
|---|---|
| `reports/competitor_analysis_YYYY-MM-DD.pdf` | Final branded report |
| `.tmp/competitors.json` | Discovered competitor list |
| `.tmp/<slug>_data.json` | Raw scraped data per competitor |
| `.tmp/analysis.json` | Structured AI analysis |

## Ongoing Monitoring
Re-run monthly:
```
python tools/run_analysis.py
```
Each run produces a new dated PDF in `reports/`. Compare month-over-month to track market changes.

## Edge Cases
| Issue | Resolution |
|---|---|
| Competitor site blocks scraping | Retry after 24h; note known data manually in `business_context.json` |
| DuckDuckGo returns irrelevant results | Edit search queries in `discover_competitors.py` |
| Claude API rate limit hit | Wait 60 seconds and re-run `analyze_competitors.py` |
| PDF logo not rendering | Confirm `brand_assets/XERXES AI Logo.png` exists and is a valid PNG |
| Fewer than 3 competitors scraped | Check `.tmp/competitors.json` manually and re-run scraper for missing ones |
