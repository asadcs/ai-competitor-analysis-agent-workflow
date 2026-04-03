#!/usr/bin/env python3
"""
Master orchestrator for the XERXES AI competitor analysis pipeline.
Runs all steps in sequence: discover → scrape → analyze → report.

Usage: python tools/run_analysis.py

See workflows/competitor_analysis.md for full documentation.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TMP_DIR = ROOT / ".tmp"
TMP_DIR.mkdir(exist_ok=True)

STEPS = {
    "discover": "Competitor Discovery",
    "scrape": "Website Scraping",
    "analyze": "AI Analysis (Claude)",
    "report": "PDF Report Generation",
}


def run_script(script_name, *args, label=""):
    script_path = ROOT / "tools" / script_name
    cmd = [sys.executable, str(script_path)] + list(args)
    label = label or script_name

    print(f"\n{'─' * 55}")
    print(f"  {label}")
    print(f"{'─' * 55}")

    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"\n✗  {label} failed (exit code {result.returncode})")
        print("   Fix the issue above, then re-run this script.")
        sys.exit(result.returncode)

    print(f"✓  {label} complete")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main():
    print("=" * 55)
    print("  XERXES AI — Competitor Analysis Pipeline")
    print("=" * 55)

    # Step 1: Discover competitors
    run_script("discover_competitors.py", label=STEPS["discover"])

    # Step 2: Scrape each discovered competitor
    competitors_file = TMP_DIR / "competitors.json"
    with open(competitors_file, encoding="utf-8") as f:
        competitors = json.load(f)

    for comp in competitors:
        run_script(
            "scrape_website.py",
            comp["url"],
            comp["name"],
            label=f"Scraping: {comp['name']}",
        )

    # Step 3: Analyze with Claude
    run_script("analyze_competitors.py", label=STEPS["analyze"])

    # Step 4: Generate branded PDF
    run_script("generate_pdf_report.py", label=STEPS["report"])

    print(f"\n{'=' * 55}")
    print("  Pipeline complete!")
    print(f"  Report saved in: reports/")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()
