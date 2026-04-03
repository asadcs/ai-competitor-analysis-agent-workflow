# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Purpose

This is a **competitor analysis and research system** built on the WAT framework. The goal is to:

1. Accept business context from the user (industry, target audience, positioning)
2. Identify and research relevant competitors
3. Analyze positioning, pricing, messaging, strengths, and weaknesses
4. Produce a **branded PDF report** with insights, patterns, gaps, and recommendations
5. Maintain an ongoing competitor monitoring system

Final outputs are branded using assets in `brand_assets/` (logo, color palette, typography, brand guidelines).

---

## The WAT Architecture

The WAT framework (Workflows, Agents, Tools) separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution.

### Layer 1: Workflows (`workflows/`)
Markdown SOPs defining the objective, required inputs, which tools to use, expected outputs, and edge case handling. Written in plain language. **Do not create or overwrite workflows unless explicitly instructed** — these are long-lived instructions that should be preserved and refined.

### Layer 2: Agents (This role)
Intelligent coordination: read the relevant workflow, run tools in the correct sequence, handle failures gracefully, ask clarifying questions when needed. Connect intent to execution without doing everything directly.

> Example: To pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, determine inputs, then execute `tools/scrape_single_site.py`.

### Layer 3: Tools (`tools/`)
Python scripts for deterministic execution — API calls, data transformations, file operations. Credentials go in `.env` only.

**Why this separation matters:** If each step is 90% accurate, chaining 5 steps gives 59% end-to-end success. Offloading execution to deterministic scripts keeps the agent focused on orchestration.

---

## How to Operate

### Before writing any new code
Check `tools/` for existing scripts that match what your workflow requires. Only create new tools when nothing exists for the task.

### When errors occur
1. Read the full error message and trace
2. Fix the script and retest (check whether the script uses paid API calls before re-running)
3. Document what you learned in the relevant workflow (rate limits, timing quirks, unexpected behavior)

### Keeping workflows current
When you find better methods, discover constraints, or encounter recurring issues — update the workflow. This is how the system improves over time.

---

## File Structure

```
brand_assets/        # Logo, color palette, typography, brand guidelines (read-only reference)
tools/               # Python scripts for deterministic execution
workflows/           # Markdown SOPs
.tmp/                # Temporary files (scraped data, intermediate exports) — disposable, regenerate as needed
.env                 # API keys and credentials (never store secrets elsewhere)
credentials.json     # Google OAuth (gitignored)
token.json           # Google OAuth (gitignored)
```

**Core principle:** Local files are for processing only. Final deliverables go to cloud services (Google Sheets, Slides, etc.) or are exported as branded PDFs.

---

## Branding Requirements

All final outputs (especially PDFs) must:
- Include the company logo from `brand_assets/`
- Match the brand colors and typography defined in `brand_assets/`
- Follow the style in the brand guidelines
- Look client-ready and professional

---

## Running Python Tools

```bash
# Run a tool directly
python tools/<script_name>.py

# Install dependencies (if requirements.txt exists)
pip install -r requirements.txt

# Environment variables are loaded from .env automatically via python-dotenv
```
