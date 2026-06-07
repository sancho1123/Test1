#!/usr/bin/env python3
"""
Daily Ukraine–Russia War Analyst Brief Generator
OUSW Comptroller Program/Budget Office
Runs via GitHub Actions at 5:00 AM ET daily.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import anthropic
import markdown2


REPORT_SYSTEM_PROMPT = """You are a senior intelligence analyst supporting the Department of War /
OUSW Comptroller Program-Budget office. You produce daily analyst-grade briefs on the
Ukraine–Russia War. Your audience is P/B analysts who respond to Congressional RFIs,
senior leader questions, and budget/execution inquiries.

Rules you must follow:
- Every major claim must be sourced with a direct URL.
- Clearly distinguish: Confirmed / Likely / Claimed but unverified / Disputed / Cannot confirm.
- Label Russian and Ukrainian official claims as claims unless independently confirmed.
- Do not speculate without evidence. Do not use sensational language.
- If a claim cannot be confirmed, state "I cannot confirm this."
- Write for a 10-minute read. Use bullets, tables, and short paragraphs."""


def build_research_prompt(report_date: str, search_results: list[dict]) -> str:
    search_context = "\n\n".join(
        f"SOURCE {i+1}: {r.get('title','')}\nURL: {r.get('url','')}\nDate: {r.get('published_date','')}\n{r.get('content','')[:2000]}"
        for i, r in enumerate(search_results)
        if r.get("content")
    )

    return f"""Today is {report_date}. Generate the full daily Ukraine–Russia War Analyst Brief.

RESEARCH SOURCES RETRIEVED (use these as your primary evidence base):
{search_context}

---

Produce the complete report in the following structure. Every claim must cite a source from above.
If a topic has no sourced information today, write "No confirmed reporting in this window."

═══════════════════════════════════════════════════════════
DAILY UKRAINE–RUSSIA WAR ANALYST BRIEF
Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury Cross-Theater Impacts
Date: {report_date}
Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY
Prepared for: OUSW Comptroller Program-Budget Office
═══════════════════════════════════════════════════════════

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART I — SENIOR LEADER SNAPSHOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A. BOTTOM LINE UP FRONT (3–5 bullets)
[What changed in last 24–48 hrs | What matters most | U.S. defense/funding impact | Epic Fury overlap]
Each bullet: finding + Source: [Name, Title, Date, URL] + Confidence: [High/Medium/Low]

B. TOP ISSUES FOR OUSW COMPTROLLER P/B ANALYSTS (5–7 tagged bullets)
Tags: [Funding] [Appropriations] [Execution] [PDA] [USAI] [Defense Articles] [Stockpiles] [Replenishment] [Congressional RFI] [Readiness] [Epic Fury / Iran Linkage]
Each bullet: What happened | Why it matters | Likely congressional question | Source URL

C. WATCH ITEMS — NEXT 7 DAYS (5 items)
Each: Indicator | Why it matters | Budget/defense article implication | Source URL if available

D. MOST LIKELY CONGRESSIONAL RFI QUESTIONS TODAY (5–10 questions)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART II — ANALYST ANNEX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. EXECUTIVE SUMMARY (7–10 bullets)
Tags: [Military] [Funding] [Appropriations] [Defense Articles] [Stockpiles] [DIB] [Replenishment] [Readiness] [Congressional Interest] [Epic Fury / Iran Linkage] [Escalation Risk] [Sanctions] [Energy]
Format: Tag | One-sentence summary | Why it matters | Source | URL | Confidence

2. BATTLEFIELD AND MILITARY OPERATIONS
For each event: Event | Location | Date/Timeframe | Source | URL | Confidence | Significance
Cover: frontline changes, Russian offensives, Ukrainian counteroffensives, missile/drone strikes,
air defense, Black Sea, Crimea, force posture, territorial changes, casualty reporting (if credible)

3. DEFENSE ARTICLES, WEAPONS, STOCKPILES, AND MUNITIONS

A. U.S.-PROVIDED DEFENSE ARTICLES
Track: Patriot/interceptors, NASAMS, HIMARS, ATACMS, GMLRS, Javelins, Stingers, 155mm/105mm ammo,
Bradley, Abrams, Strykers, MRAPs, air defense radars, counter-UAS, drones/UAVs, EW systems,
F-16 support, spare parts, sustainment, training
For each: Article | Status (transferred/requested/depleted/delayed/replenished/produced) |
Source | URL | Confidence | Battlefield impact | U.S. readiness impact | Congressional interest |
Appropriations implication

B. ALLIED / PARTNER DEFENSE ARTICLES
NATO, UK, Germany, France, Poland, Baltics, Nordics, Canada, Australia, Japan, South Korea

C. STOCKPILE AND READINESS ISSUES
Depletions, interceptor shortages, ammo shortages, missile availability, drone availability,
spare parts, maintenance, replenishment delays, production constraints, multi-theater demand

D. DEFENSE ARTICLE ANALYSIS TABLE
| Article | Status | Source | URL | Confidence | Battlefield Impact | Readiness Impact |

4. DEFENSE INDUSTRIAL BASE AND PRODUCTION CAPACITY
Company/entity | System/munition | Production issue or improvement | Ukraine impact |
U.S./allied readiness impact | Source | URL | Confidence

5. FUNDING, BUDGET, APPROPRIATIONS, AND CONGRESSIONAL RELEVANCE
| Funding Item | Account/Mechanism | Amount (if sourced) | Source | URL | Confidence | Comptroller Relevance | Potential RFI |
Cover: new aid packages, PDA, USAI, FMF, supplementals, reprogramming, apportionment,
coalition contributions, frozen assets, GAO/CRS/IG findings

6. OPERATION EPIC FURY / IRAN AND UKRAINE–RUSSIA WAR LINKAGE

A. Weapons and Stockpile Competition
Are both conflicts drawing from the same inventory? Supply priority? Replenishment timelines?
Systems: Patriot interceptors, THAAD, SM variants, NASAMS, counter-drone, PGMs, air-to-air/ground,
long-range strike, ISR, naval air defense, EW, spare parts

B. Drone and Missile Warfare Linkage
Russian use of Iranian drones | Iranian activity related to Epic Fury | Shared technology patterns |
Shahed-type systems | Ballistic/cruise missile threats | Low-cost drone saturation

C. Russia–Iran Relationship
Does Epic Fury weaken/strengthen/complicate Russia–Iran cooperation?
Iranian weapons to Russia | Russian support to Iran | Drone/missile/air defense cooperation |
Technology transfers | Sanctions evasion | Energy/financial networks

D. Energy and Economic Effects
Oil prices | LNG flows | Hormuz risk | Black Sea energy | European energy security |
Russian energy revenue | Sanctions enforcement | Ukraine funding impact

E. Strategic Bandwidth and Force Allocation
CENTCOM vs EUCOM prioritization | Congressional Ukraine appetite | Allied burden sharing |
Indo-Pacific readiness | Naval deployments | Missile defense posture
Label: Confirmed evidence / Credible reporting / Analyst judgment

7. RUSSIA, IRAN, CHINA, NORTH KOREA, BELARUS, SANCTIONS-EVASION NETWORKS
Actor | Assistance type | Source | URL | Confidence | Ukraine war impact | Congressional/budget relevance
Cover: missiles, drones, ammo, artillery shells, electronics, dual-use components,
financial channels, oil/energy trade, shipping, crypto, front companies, export-control evasion

8. ESCALATION RISKS AND WARNING INDICATORS
| Indicator | Risk Level (Low/Medium/High) | Source | URL | Confidence | Why it matters | Policy/budget implication |
Cover: nuclear signaling, Belarus involvement, attacks near NATO territory, cyber on infrastructure,
nuclear facilities, Black Sea, new weapons, Iranian/NK/China expansion, U.S./NATO posture changes

9. CONGRESSIONAL RFI READINESS
| Likely RFI Question | Short Answer | Source Links | Confidence |
Include answers to: 24-48hr changes, defense articles needed, U.S./allied stockpile status,
Ukraine/Epic Fury competition, air defense support status, U.S. readiness risk, funding streams,
supplemental/reprogramming likelihood, foreign support to Russia, sanctions effectiveness, DIB constraints

10. DELTA FROM PRIOR REPORT
New developments | Changed assessments | Escalated/de-escalated risks |
New funding implications | New defense article issues | New Epic Fury/Ukraine overlap
(State "No prior report available for comparison" if applicable)

11. ANALYST ASSESSMENT
What matters most today | Watch items next 7 days | Potential congressional issue |
Budget execution impact | Defense article/stockpile replenishment risk | U.S. readiness impact |
Most important cross-theater linkage
Label clearly: Confirmed Facts | Analyst Judgment | Cannot Confirm

12. SOURCE LOG
| # | Source | Title | Date Published | URL | Topic | Confidence | Notes |
Every source must have a direct URL. Note: paywalled / official source / analysis / Russian claim / Ukrainian claim

13. CONFIDENCE MATRIX
| Claim / Topic | Confidence | Reason |

─────────────────────────────────────────────────────────────
END OF BRIEF
File: {report_date}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB
─────────────────────────────────────────────────────────────"""


def run_tavily_searches(report_date: str) -> list[dict]:
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    except (ImportError, KeyError):
        print("Tavily not available — skipping web search, Claude will use training knowledge.")
        return []

    date_minus1 = (datetime.strptime(report_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")

    queries = [
        f"Ukraine Russia war frontline battlefield operations {report_date} site:understandingwar.org OR site:kyivindependent.com OR site:reuters.com OR site:bbc.com",
        f"Ukraine defense articles weapons stockpiles U.S. aid Patriot HIMARS ATACMS {report_date} site:defensenews.com OR site:breakingdefense.com OR site:reuters.com",
        f"Ukraine war funding PDA USAI appropriations budget Congress {report_date} site:defensenews.com OR site:politico.com OR site:congress.gov OR site:csis.org",
        f"Operation Epic Fury Iran Ukraine Russia weapons competition Patriot interceptors CENTCOM EUCOM {report_date}",
        f"Russia Iran China North Korea Belarus weapons drones ammunition sanctions Ukraine war {report_date} site:reuters.com OR site:wsj.com OR site:rusi.org OR site:csis.org",
    ]

    results = []
    for q in queries:
        try:
            r = client.search(query=q, max_results=5, include_raw_content=False, days=3)
            results.extend(r.get("results", []))
        except Exception as e:
            print(f"Search error for query '{q[:60]}...': {e}", file=sys.stderr)

    seen = set()
    deduped = []
    for r in results:
        url = r.get("url", "")
        if url and url not in seen:
            seen.add(url)
            deduped.append(r)

    return deduped[:20]


def generate_report(report_date: str, search_results: list[dict]) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = build_research_prompt(report_date, search_results)

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        system=REPORT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def convert_to_html(markdown_text: str, report_date: str) -> str:
    body_html = markdown2.markdown(
        markdown_text,
        extras=["tables", "fenced-code-blocks", "header-ids", "break-on-newline"],
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ukraine–Russia War Daily Analyst Brief — {report_date}</title>
  <style>
    body {{ font-family: Arial, sans-serif; font-size: 13px; line-height: 1.5;
           max-width: 960px; margin: 0 auto; padding: 20px; color: #1a1a1a; }}
    h1 {{ font-size: 18px; color: #1a1a2e; border-bottom: 2px solid #c0392b; padding-bottom: 6px; }}
    h2 {{ font-size: 15px; color: #1a1a2e; border-bottom: 1px solid #bbb; padding-bottom: 4px;
          margin-top: 24px; }}
    h3 {{ font-size: 13px; color: #2c3e50; margin-top: 16px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 12px; }}
    th {{ background: #2c3e50; color: #fff; padding: 6px 8px; text-align: left; }}
    td {{ border: 1px solid #ccc; padding: 5px 8px; vertical-align: top; }}
    tr:nth-child(even) td {{ background: #f9f9f9; }}
    blockquote {{ border-left: 4px solid #c0392b; margin: 10px 0; padding: 4px 12px;
                  background: #fef9f9; }}
    a {{ color: #2980b9; }}
    code {{ background: #f4f4f4; padding: 1px 4px; border-radius: 3px; font-size: 11px; }}
    .header-bar {{ background: #1a1a2e; color: #fff; padding: 12px 16px; margin-bottom: 20px;
                   border-left: 6px solid #c0392b; }}
    .header-bar p {{ margin: 2px 0; font-size: 12px; color: #ccc; }}
    .unclass {{ font-size: 11px; color: #888; text-align: center; margin: 4px 0; }}
  </style>
</head>
<body>
  <div class="unclass">UNCLASSIFIED // FOR OFFICIAL USE ONLY</div>
  <div class="header-bar">
    <strong>DAILY UKRAINE–RUSSIA WAR ANALYST BRIEF</strong>
    <p>Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury Cross-Theater Impacts</p>
    <p>Date: {report_date} | Prepared for: OUSW Comptroller Program-Budget Office</p>
  </div>
  {body_html}
  <hr>
  <div class="unclass">UNCLASSIFIED // FOR OFFICIAL USE ONLY — {report_date}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB</div>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate Ukraine–Russia War Daily Analyst Brief")
    parser.add_argument("--date", default=datetime.utcnow().strftime("%Y-%m-%d"), help="Report date YYYY-MM-DD")
    parser.add_argument("--output", default="/tmp/brief.md", help="Output markdown path")
    parser.add_argument("--html-output", default="/tmp/brief.html", help="Output HTML path")
    args = parser.parse_args()

    print(f"[{datetime.utcnow().isoformat()}] Generating brief for {args.date}")

    print("  Running web searches via Tavily...")
    search_results = run_tavily_searches(args.date)
    print(f"  Retrieved {len(search_results)} sources.")

    print("  Calling Claude API to generate report...")
    report_text = generate_report(args.date, search_results)

    Path(args.output).write_text(report_text, encoding="utf-8")
    print(f"  Markdown saved to {args.output}")

    html = convert_to_html(report_text, args.date)
    Path(args.html_output).write_text(html, encoding="utf-8")
    print(f"  HTML saved to {args.html_output}")

    print(f"[{datetime.utcnow().isoformat()}] Brief generation complete.")


if __name__ == "__main__":
    main()
