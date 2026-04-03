# Scrape Website Workflow

## Objective
Scrape a single competitor website to extract positioning, messaging, services, and pricing information for analysis.

## Tool
`tools/scrape_website.py`

## Usage
```
python tools/scrape_website.py <url> "<competitor_name>"
```

Example:
```
python tools/scrape_website.py https://example.com "Example Agency"
```

## What It Scrapes
| Page | Content Extracted |
|---|---|
| Homepage | Title, meta description, H1–H3 headings, body text (3,000 chars) |
| Pricing | Pricing model, plan names, price points |
| Services | Service list, descriptions |
| About | Company background, team, mission |

Sub-pages are discovered automatically via nav links. Pages not found in navigation are skipped.

## Output
`.tmp/<slug>_data.json` — structured JSON with content per page.

Example output shape:
```json
{
  "name": "Example Agency",
  "pages": {
    "homepage": { "url": "...", "title": "...", "meta_description": "...", "headings": [...], "body_text": "..." },
    "pricing":  { "url": "...", "title": "...", ... }
  }
}
```

## Limitations
- JavaScript-rendered content is not captured (static HTML only)
- Body text capped at 3,000 characters per page
- Sites behind Cloudflare, login walls, or bot detection may return empty content

## Known Issues & Fixes
| Issue | Fix |
|---|---|
| Site consistently blocks scraping | Note known information manually; pass it via `business_context.json` |
| Pricing table uses dynamic JS | Pricing field will appear empty; record manually if available |
| Too many requests error | Increase `time.sleep()` delay in `scrape_website.py` |
