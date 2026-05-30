#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief Generator
Calls Anthropic API with web-search tool use to research and generate
the OUSW Comptroller P/B daily brief.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
import anthropic

SYSTEM_PROMPT = """You are a senior Department of War analyst supporting the OUSW Comptroller
Program-Budget office. Your task is to generate a daily analyst-grade brief on the
Ukraine-Russia War covering: battlefield developments, defense articles and stockpiles,
U.S. funding and appropriations, Operation Epic Fury / Iran cross-theater impacts,
and congressional RFI readiness.

Write in direct, professional analyst language. No political commentary. No speculation
without evidence. Clearly label every claim as Confirmed, Likely, Claimed, or
Cannot Confirm. Every major finding must cite a source with a web link.

Structure:
PART I — SENIOR LEADER SNAPSHOT (executive bullets, ~1 page)
  A. Bottom Line Up Front (3-5 bullets)
  B. Top Issues for OUSW Comptroller P/B Analysts (5-7 tagged bullets)
  C. Watch Items — Next 7 Days (5 items)
  D. Most Likely Congressional RFI Questions Today (5-10 questions)

PART II — ANALYST ANNEX (detailed, sourced)
  1. Executive Summary
  2. Battlefield and Military Operations
  3. Defense Articles, Weapons, Stockpiles, and Munitions
  4. Defense Industrial Base and Production Capacity
  5. Funding, Budget, Appropriations, and Congressional Relevance
  6. Operation Epic Fury / Iran and Ukraine-Russia War Linkage
  7. Russia, Iran, North Korea, China, and Sanctions-Evasion Networks
  8. Escalation Risks and Warning Indicators
  9. Congressional RFI Readiness Section
  10. Delta From Prior Report
  11. Analyst Assessment
  12. Source Log (every source with link)
  13. Confidence Matrix

Format output as clean HTML suitable for email."""

USER_PROMPT = """Today is {date}. Research and generate the daily Ukraine-Russia War
Analyst Brief for OUSW Comptroller P/B analysts. Cover the last 24-48 hours of
developments. Search for:
1. Latest Ukraine-Russia battlefield developments and frontline changes
2. U.S. and allied defense articles, weapons transfers, and stockpile status
3. Operation Epic Fury / Iran linkage and shared munitions demand
4. U.S. Ukraine funding — PDA, USAI, supplementals, appropriations
5. Russia/Iran/North Korea/China support networks
6. Escalation indicators and nuclear signaling
7. Congressional activity and likely RFIs

Provide a complete, sourced, analyst-grade brief. Every major claim must include
the source name and a direct web link. Label unverified claims clearly."""


def generate_brief(output_path: str) -> None:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"Generating brief for {today}...")

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": USER_PROMPT.format(date=today),
            }
        ],
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
            }
        ],
    )

    brief_html = ""
    for block in response.content:
        if hasattr(block, "text"):
            brief_html += block.text

    # Wrap in full HTML document
    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ukraine-Russia War Daily Analyst Brief — {today}</title>
<style>
  body {{ font-family: Arial, sans-serif; font-size: 13px; line-height: 1.6;
          color: #1a1a1a; max-width: 900px; margin: 0 auto; padding: 20px; }}
  h1 {{ background: #1a3a6b; color: white; padding: 12px 16px; font-size: 16px; }}
  h2 {{ background: #2c5f9e; color: white; padding: 8px 12px; font-size: 14px; margin-top: 20px; }}
  h3 {{ color: #1a3a6b; border-bottom: 2px solid #1a3a6b; padding-bottom: 4px; }}
  .bluf-box {{ background: #f0f4ff; border-left: 4px solid #1a3a6b; padding: 12px; margin: 10px 0; }}
  .warning {{ background: #fff3cd; border-left: 4px solid #ff8c00; padding: 10px; margin: 8px 0; }}
  .critical {{ background: #ffe0e0; border-left: 4px solid #cc0000; padding: 10px; margin: 8px 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 12px; }}
  th {{ background: #1a3a6b; color: white; padding: 8px; text-align: left; }}
  td {{ border: 1px solid #ccc; padding: 6px 8px; vertical-align: top; }}
  tr:nth-child(even) td {{ background: #f5f5f5; }}
  .tag {{ display: inline-block; background: #e0e7ff; color: #1a3a6b;
           padding: 1px 6px; border-radius: 3px; font-size: 11px; font-weight: bold; }}
  .confidence-high {{ color: #006400; font-weight: bold; }}
  .confidence-med {{ color: #8B6914; font-weight: bold; }}
  .confidence-low {{ color: #cc0000; font-weight: bold; }}
  .footer {{ background: #f0f0f0; padding: 10px; font-size: 11px; margin-top: 20px;
              border-top: 2px solid #1a3a6b; }}
  a {{ color: #1a3a6b; }}
</style>
</head>
<body>
{brief_html}
<div class="footer">
  UNCLASSIFIED // FOR OFFICIAL USE ONLY<br>
  Report Date: {today} | Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}<br>
  Department of War / OUSW Comptroller Program-Budget Office<br>
  Daily Ukraine-Russia War Analyst Brief
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Brief written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/tmp/brief.html")
    args = parser.parse_args()
    generate_brief(args.output)
