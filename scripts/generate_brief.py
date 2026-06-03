"""
Daily Ukraine-Russia War Analyst Brief Generator
OUSW Comptroller Program/Budget Office
Runs daily at 5:00 AM ET via GitHub Actions
"""

import os
import sys
import json
import datetime
import requests
from pathlib import Path

import anthropic

RECIPIENT_EMAIL = "ericjsanchez23@gmail.com"
REPORTS_DIR = Path(__file__).parent.parent / "reports"

SYSTEM_PROMPT = """You are a senior defense analyst supporting the Department of War / OUSW Comptroller
Program/Budget office. Your task is to produce a daily analyst-grade Ukraine-Russia War brief.

STRICT REQUIREMENTS:
- Every claim must have a source with a working web link.
- Clearly label claims as: Confirmed / Likely / Claimed but unverified / Disputed / Cannot confirm.
- Do not present unverified claims as fact.
- Label Russian and Ukrainian official statements as claims unless independently confirmed.
- No political commentary. No sensational language.
- The report must be useful for analysts supporting Congressional RFIs, defense articles,
  appropriations, budget execution, stockpile replenishment, U.S. readiness, and Ukraine aid.
- Structure: Part I (Senior Leader Snapshot) + Part II (Analyst Annex with all required sections).
- Keep it a 10-minute read. Use bullets and tables.
"""

USER_PROMPT_TEMPLATE = """Generate a complete Daily Ukraine–Russia War Analyst Brief for {date}.

The reporting window is the last 24–48 hours (June {date}).

Required sections — follow ALL of them:

PART I — SENIOR LEADER SNAPSHOT:
A. Bottom Line Up Front (3–5 sourced bullets)
B. Top Issues for OUSW Comptroller P/B Analysts (5–7 tagged bullets)
C. Watch Items for the Next 7 Days (5 items with sources)
D. Most Likely Congressional RFI Questions Today (5–10 questions)

PART II — ANALYST ANNEX:
1. Executive Summary (7–10 sourced bullets with tags)
2. Battlefield and Military Operations (with tables)
3. Defense Articles, Weapons, Stockpiles, and Munitions (with tables — Patriot, THAAD, HIMARS, ATACMS, 155mm, drones, etc.)
4. Defense Industrial Base and Production Capacity
5. Funding, Budget, Appropriations, and Congressional Relevance (PDA, USAI, FMF, supplementals)
6. Operation Epic Fury / Iran and Ukraine–Russia War Linkage (stockpile competition, drone linkage, Russia-Iran relationship, energy effects, strategic bandwidth)
7. Russia, Iran, China, North Korea, Belarus, and Sanctions-Evasion Networks
8. Escalation Risks and Warning Indicators (classified by Low/Medium/High)
9. Congressional RFI Readiness Section (table format: Question | Answer | Source | Confidence)
10. Delta From Prior Report
11. Analyst Assessment (Confirmed Facts / Analyst Judgment / Cannot Confirm)
12. Required News Article / Source Log (every source listed with link, date, confidence)
13. Confidence Matrix (table)

Use web search results below (search before generating). Every major claim requires:
- Source name
- Direct web link
- Confidence level (High/Medium/Low/Cannot confirm)

Write in markdown. Produce the complete report without truncation.
"""


def search_web(query: str, api_key: str) -> list[dict]:
    """Search using Brave Search API and return results."""
    if not api_key:
        return []
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {"q": query, "count": 5, "freshness": "pd"}  # past day
    try:
        resp = requests.get(
            "https://api.search.brave.com/res/web/search",
            headers=headers,
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        results = resp.json().get("web", {}).get("results", [])
        return [{"title": r.get("title"), "url": r.get("url"), "description": r.get("description")} for r in results]
    except Exception as e:
        print(f"Search error for '{query}': {e}", file=sys.stderr)
        return []


def gather_research(brave_key: str) -> str:
    """Run parallel searches and compile research context."""
    queries = [
        f"Ukraine Russia war frontline military developments {datetime.date.today().strftime('%B %Y')}",
        f"Ukraine US defense articles weapons Patriot Patriot interceptors {datetime.date.today().year}",
        f"Operation Epic Fury Iran status update {datetime.date.today().strftime('%B %Y')}",
        f"Ukraine USAI PDA appropriations Congress {datetime.date.today().year}",
        f"Russia Iran North Korea China weapons drones Ukraine {datetime.date.today().year}",
        f"US munitions stockpile depletion replenishment defense industrial base {datetime.date.today().year}",
        f"Strait of Hormuz oil energy prices Europe {datetime.date.today().year}",
    ]

    context_parts = []
    for query in queries:
        results = search_web(query, brave_key)
        if results:
            context_parts.append(f"\n### Search: {query}\n")
            for r in results:
                context_parts.append(f"- [{r['title']}]({r['url']})\n  {r.get('description', '')}")

    return "\n".join(context_parts) if context_parts else "No live search results available — use training knowledge and note this limitation."


def generate_brief(date_str: str, research_context: str) -> str:
    """Call Claude API to generate the full analyst brief."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user_message = USER_PROMPT_TEMPLATE.format(date=date_str)
    if research_context:
        user_message += f"\n\n---\n## WEB SEARCH RESULTS (use these as primary sources):\n{research_context}"

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text


def save_report(date_str: str, content: str) -> Path:
    """Save report as markdown file."""
    REPORTS_DIR.mkdir(exist_ok=True)
    filename = f"{date_str}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md"
    filepath = REPORTS_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    print(f"Report saved: {filepath}")
    return filepath


def main():
    date_str = datetime.date.today().isoformat()  # YYYY-MM-DD
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    brave_key = os.environ.get("BRAVE_API_KEY", "")

    if not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY is required.", file=sys.stderr)
        sys.exit(1)

    print(f"Generating brief for {date_str}...")
    print("Gathering web research...")
    research = gather_research(brave_key)

    print("Calling Claude API to generate report...")
    brief = generate_brief(date_str, research)

    filepath = save_report(date_str, brief)

    # Write filepath for downstream steps
    with open("brief_path.txt", "w") as f:
        f.write(str(filepath))

    print("Done.")


if __name__ == "__main__":
    main()
