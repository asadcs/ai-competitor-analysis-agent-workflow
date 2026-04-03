#!/usr/bin/env python3
"""
Analyze competitor data using Claude API and produce structured insights.
Requires: ANTHROPIC_API_KEY in .env
Input:    .tmp/competitors.json + .tmp/*_data.json
Output:   .tmp/analysis.json
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP_DIR = ROOT / ".tmp"
BUSINESS_CONTEXT_FILE = ROOT / "business_context.json"

MODEL = "claude-sonnet-4-6"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def build_competitor_text(comp_data):
    text = f"\n### Competitor: {comp_data['name']}\n"
    for page_name, page in comp_data.get("pages", {}).items():
        text += f"\n**{page_name.upper()}**\n"
        text += f"Title: {page.get('title', '')}\n"
        text += f"Meta:  {page.get('meta_description', '')}\n"
        headings = " | ".join(page.get("headings", [])[:10])
        text += f"Headings: {headings}\n"
        text += f"Content: {page.get('body_text', '')[:600]}\n"
    return text


def build_prompt(context, competitors_data):
    context_str = json.dumps(context, indent=2)
    competitors_str = "".join(build_competitor_text(c) for c in competitors_data)

    return f"""You are a strategic business analyst specializing in the AI automation space.

Analyze the following competitor data for {context['company_name']}, which provides {context['service']} to {context['target_market']}.

## Our Business Context
{context_str}

## Competitor Data
{competitors_str}

## Your Task
Return a JSON object with this exact structure. Be specific and actionable — avoid generic filler.

{{
  "competitors": [
    {{
      "name": "Company Name",
      "url": "https://...",
      "positioning": "How they position themselves in 1-2 sentences",
      "target_audience": "Who they specifically target",
      "services": ["service 1", "service 2", "service 3"],
      "pricing": "Pricing model description or 'Not publicly disclosed'",
      "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
      "weaknesses": ["specific weakness 1", "specific weakness 2"]
    }}
  ],
  "patterns": [
    "Recurring pattern 1 observed across competitors",
    "Recurring pattern 2",
    "Recurring pattern 3"
  ],
  "opportunities": [
    "Specific opportunity for XERXES AI based on competitor gaps",
    "Opportunity 2",
    "Opportunity 3"
  ],
  "recommendations": [
    "Actionable recommendation 1 with clear rationale",
    "Recommendation 2",
    "Recommendation 3"
  ],
  "monitoring_plan": "Description of what specific things to track monthly and why"
}}

Return only valid JSON. No markdown, no commentary outside the JSON object."""


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in .env")
        print("Add your key: ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed.")
        print("Run: pip install anthropic")
        sys.exit(1)

    print("Loading business context...")
    context = load_json(BUSINESS_CONTEXT_FILE)

    competitors_file = TMP_DIR / "competitors.json"
    if not competitors_file.exists():
        print("ERROR: .tmp/competitors.json not found.")
        print("Run: python tools/discover_competitors.py")
        sys.exit(1)

    competitors_list = load_json(competitors_file)
    competitors_data = []

    print("Loading scraped competitor data...")
    for comp in competitors_list:
        slug = slugify(comp["name"])
        data_file = TMP_DIR / f"{slug}_data.json"
        if data_file.exists():
            competitors_data.append(load_json(data_file))
            print(f"  ✓ {comp['name']}")
        else:
            print(f"  ✗ {comp['name']} — no scraped data found (run scrape_website.py first)")

    if not competitors_data:
        print("\nERROR: No competitor data files found in .tmp/")
        print("Run scrape_website.py for each competitor, or use run_analysis.py for the full pipeline.")
        sys.exit(1)

    print(f"\nSending {len(competitors_data)} competitors to Claude ({MODEL}) for analysis...")

    client = anthropic.Anthropic(api_key=api_key)
    prompt = build_prompt(context, competitors_data)

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    try:
        analysis = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                analysis = json.loads(match.group())
            except json.JSONDecodeError:
                print("ERROR: Could not parse Claude's response as JSON.")
                raw_path = TMP_DIR / "raw_analysis.txt"
                raw_path.write_text(raw, encoding="utf-8")
                print(f"Raw response saved to {raw_path} for inspection.")
                sys.exit(1)
        else:
            print("ERROR: Claude returned no valid JSON.")
            raw_path = TMP_DIR / "raw_analysis.txt"
            raw_path.write_text(raw, encoding="utf-8")
            print(f"Raw response saved to {raw_path}")
            sys.exit(1)

    analysis["generated_at"] = str(date.today())
    analysis["business_context"] = context

    out_path = TMP_DIR / "analysis.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(f"\nAnalysis complete.")
    print(f"  Competitors analyzed: {len(analysis.get('competitors', []))}")
    print(f"  Patterns found:       {len(analysis.get('patterns', []))}")
    print(f"  Opportunities:        {len(analysis.get('opportunities', []))}")
    print(f"  Recommendations:      {len(analysis.get('recommendations', []))}")
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
