#!/usr/bin/env python3
"""
Scrape a competitor website and extract key content.
Usage:  python tools/scrape_website.py <url> "<competitor_name>"
Output: .tmp/<slug>_data.json

See workflows/scrape_website.md for full documentation.
"""

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP_DIR = ROOT / ".tmp"
TMP_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 15
CRAWL_DELAY = 1  # seconds between requests (polite crawling)
MAX_BODY_CHARS = 3000
SUBPAGE_KEYWORDS = ["pricing", "services", "about", "solutions", "how-it-works", "features", "plans"]


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def fetch_page(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  Warning: could not fetch {url} — {e}")
        return None


def extract_content(html, url):
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "aside", "form", "noscript"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else ""

    meta_desc = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        meta_desc = meta.get("content", "")

    headings = [
        h.get_text(strip=True)
        for h in soup.find_all(["h1", "h2", "h3"])
        if h.get_text(strip=True)
    ][:20]

    body_text = " ".join(soup.get_text(separator=" ").split())[:MAX_BODY_CHARS]

    return {
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "headings": headings,
        "body_text": body_text,
    }


def find_subpages(base_url, html):
    soup = BeautifulSoup(html, "lxml")
    domain = urlparse(base_url).netloc
    found = {}

    for a in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a["href"])
        if urlparse(full_url).netloc != domain:
            continue
        path = urlparse(full_url).path.lower().strip("/")
        for kw in SUBPAGE_KEYWORDS:
            if kw in path and kw not in found:
                found[kw] = full_url

    return found


def scrape_competitor(url, name):
    print(f"Scraping: {name}")
    print(f"  URL: {url}")

    homepage_html = fetch_page(url)
    if not homepage_html:
        print(f"  ERROR: Could not reach homepage.")
        return None

    data = {"name": name, "pages": {}}
    data["pages"]["homepage"] = extract_content(homepage_html, url)
    print(f"  ✓ homepage")

    subpages = find_subpages(url, homepage_html)
    for page_type, page_url in subpages.items():
        time.sleep(CRAWL_DELAY)
        html = fetch_page(page_url)
        if html:
            data["pages"][page_type] = extract_content(html, page_url)
            print(f"  ✓ {page_type}")

    return data


def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/scrape_website.py <url> <competitor_name>")
        sys.exit(1)

    url = sys.argv[1]
    name = sys.argv[2]
    slug = slugify(name)

    data = scrape_competitor(url, name)
    if not data:
        print(f"ERROR: Failed to scrape {url}")
        sys.exit(1)

    out_path = TMP_DIR / f"{slug}_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    pages_scraped = list(data["pages"].keys())
    print(f"\nPages scraped: {', '.join(pages_scraped)}")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
