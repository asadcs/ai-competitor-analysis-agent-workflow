#!/usr/bin/env python3
"""
Discover top 3 competitors for XERXES AI using DuckDuckGo search.
Input:  business_context.json
Output: .tmp/competitors.json
"""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP_DIR = ROOT / ".tmp"
TMP_DIR.mkdir(exist_ok=True)
BUSINESS_CONTEXT_FILE = ROOT / "business_context.json"

TARGET_COUNT = 3
EXCLUDE_DOMAINS = {"xerxesai.com", "linkedin.com", "youtube.com", "facebook.com", "twitter.com", "reddit.com"}


def load_business_context():
    with open(BUSINESS_CONTEXT_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def clean_title(raw_title):
    for sep in [" - ", " | ", " — ", " :: "]:
        if sep in raw_title:
            return raw_title.split(sep)[0].strip()
    return raw_title.strip()[:60]


def discover_competitors(context):
    queries = [
        "AI automation agency for small businesses",
        "AI workflow automation SMB consulting services",
        "AI business automation tools small medium business",
    ]

    results = []
    seen_domains = set()

    with DDGS() as ddgs:
        for query in queries:
            if len(results) >= TARGET_COUNT:
                break
            print(f"  Searching: {query}")
            try:
                for r in ddgs.text(query, max_results=10):
                    domain = get_domain(r.get("href", ""))
                    if (
                        domain
                        and domain not in seen_domains
                        and domain not in EXCLUDE_DOMAINS
                        and len(results) < TARGET_COUNT
                    ):
                        seen_domains.add(domain)
                        results.append({
                            "name": clean_title(r.get("title", domain)),
                            "url": r.get("href", ""),
                            "description": r.get("body", "")[:300],
                        })
            except Exception as e:
                print(f"  Warning: search query failed — {e}")
                continue

    return results[:TARGET_COUNT]


def main():
    print("Loading business context...")
    context = load_business_context()
    print(f"Company: {context['company_name']}")
    print(f"Service: {context['service']}")
    print(f"Target:  {context['target_market']}")
    print()

    print(f"Discovering {TARGET_COUNT} competitors via DuckDuckGo...")
    competitors = discover_competitors(context)

    if not competitors:
        print("ERROR: No competitors found. Check your internet connection or adjust search queries.")
        sys.exit(1)

    out_path = TMP_DIR / "competitors.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(competitors, f, indent=2, ensure_ascii=False)

    print(f"\nFound {len(competitors)} competitors:")
    for c in competitors:
        print(f"  • {c['name']}")
        print(f"    {c['url']}")
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
