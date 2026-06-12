"""
Daily Ukraine-Russia War Analyst Brief Generator
OUSW Comptroller Program-Budget Analysts
Runs via GitHub Actions at 5:00 AM Eastern daily.
Calls the Anthropic API with web_search enabled to research and generate the report.
"""

import anthropic
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

EASTERN = timezone(timedelta(hours=-5))  # EST; GitHub Actions adjusts cron for DST separately

REPORT_PROMPT = """You are a senior defense analyst supporting the Department of War / OUSW Comptroller Program-Budget office. Generate a daily analyst-grade report on the Ukraine-Russia War for {date}.

The report is for analysts who need to respond to Congressional RFIs, senior leader questions, budget and execution inquiries, defense article and stockpile questions, Ukraine aid questions, and cross-theater impact questions involving Operation Epic Fury / Iran.

## RESEARCH REQUIRED — Search for ALL of the following:

1. **BATTLEFIELD & MILITARY OPERATIONS (last 24-48 hours):** Frontline changes, Russian offensives, Ukrainian counteroffensives, missile attacks, drone attacks, air defense activity, cyber operations, Black Sea activity, Crimea-related activity, Russian and Ukrainian force posture, territorial changes, casualty reporting (credible sources only).

2. **DEFENSE ARTICLES, WEAPONS, STOCKPILES & MUNITIONS:** U.S.-provided defense articles (Patriot systems/interceptors, NASAMS, HIMARS, GMLRS, ATACMS, Javelins, Stingers, 155mm/105mm artillery rounds, Bradley Fighting Vehicles, Abrams tanks, F-16 support, counter-UAS, drones/UAVs, electronic warfare, sustainment). Allied/partner defense articles. Stockpile depletion, readiness issues, replenishment delays, production constraints, multi-theater demand.

3. **DEFENSE INDUSTRIAL BASE & PRODUCTION:** U.S. defense contractors, NATO defense production, ammunition manufacturing, missile production, air defense production, drone production, production line expansion, emergency procurement, multi-year procurement, replenishment funding.

4. **FUNDING, BUDGET, APPROPRIATIONS & CONGRESSIONAL:** New aid packages, supplemental appropriations, Presidential Drawdown Authority (PDA), Ukraine Security Assistance Initiative (USAI), Foreign Military Financing (FMF), replenishment funding, reprogramming actions, apportionment issues, budget execution concerns, coalition contributions, EU/NATO burden sharing, frozen Russian assets, sanctions, Congressional oversight, GAO/CRS/IG findings.

5. **OPERATION EPIC FURY / IRAN – UKRAINE-RUSSIA WAR LINKAGE:** Weapons and stockpile competition between both conflicts (Patriot, THAAD, Standard Missiles, NASAMS, counter-drone systems). Drone and missile warfare linkage (Iranian-origin drones, Shahed-type systems). Russia-Iran relationship. Energy and economic effects (oil prices, LNG, Hormuz, Black Sea). Strategic bandwidth (CENTCOM vs EUCOM prioritization, congressional appetite for Ukraine funding).

6. **RUSSIA-IRAN-CHINA-NORTH KOREA-BELARUS ASSISTANCE NETWORKS:** Missiles, drones, ammunition, artillery shells, electronics, dual-use components, financial channels, oil trade, shipping networks, sanctions evasion.

7. **ESCALATION RISKS & WARNING INDICATORS:** Russian nuclear signaling, Belarus involvement, attacks near/on NATO territory, cyber attacks, nuclear facility attacks, use of new weapons systems, expanded Iranian/North Korean/Chinese involvement.

## REQUIRED REPORT STRUCTURE

Produce a complete report with:

### PART I — SENIOR LEADER SNAPSHOT (fits ~1 page)

**A. BOTTOM LINE UP FRONT (BLUF)**
- 3-5 bullets covering: What changed, What matters most, What affects U.S. funding/defense articles/stockpiles/readiness, Any Ukraine-Russia/Epic Fury overlap
- Each bullet: Source name, direct URL, Confidence level (High/Medium/Low)

**B. TOP ISSUES FOR OUSW COMPTROLLER P/B ANALYSTS**
- 5-7 bullets tagged: [Funding] [Appropriations] [Execution] [PDA] [USAI] [Defense Articles] [Stockpiles] [Replenishment] [Congressional RFI] [Readiness] [Epic Fury / Iran Linkage]
- Each: What happened, Why it matters, What Congress/senior leaders may ask

**C. WATCH ITEMS — NEXT 7 DAYS**
- 5 items: Indicator, Why it matters, Budget/defense article/congressional implication, Source link

**D. MOST LIKELY CONGRESSIONAL RFI QUESTIONS TODAY**
- 5-10 likely RFI questions based on today's reporting

---

### PART II — ANALYST ANNEX

**1. EXECUTIVE SUMMARY** — 7-10 bullets with topic tags, one-sentence summary, why it matters, source, URL, confidence

**2. BATTLEFIELD AND MILITARY OPERATIONS** — Tables for each significant event (Event, Location, Date/Timeframe, Source, Link, Confidence, Significance)

**3. DEFENSE ARTICLES, WEAPONS, STOCKPILES, AND MUNITIONS**
- A. U.S.-Provided Defense Articles (Patriot, HIMARS, ATACMS, 155mm, etc.)
- B. Allied/Partner Defense Articles
- C. Stockpile and Readiness matrix
- D. Defense Article Analysis (for each: What article? Transfer/requested/depleted/replenished/produced? Source? Link? Confidence? Battlefield impact? U.S. readiness impact? Congressional interest? Appropriations implication?)

**4. DEFENSE INDUSTRIAL BASE AND PRODUCTION CAPACITY** — Table: Entity, System, Issue, Ukraine impact, Readiness impact, Source, Link, Confidence

**5. FUNDING, BUDGET, APPROPRIATIONS, AND CONGRESSIONAL RELEVANCE** — Table: Funding item, Account/mechanism, Amount, Source, Link, Confidence, Comptroller relevance, Potential RFI

**6. OPERATION EPIC FURY / IRAN AND UKRAINE-RUSSIA WAR LINKAGE**
- A. Weapons and Stockpile Competition — are both conflicts drawing from same inventory? Is one affecting other's supply priority? Congressional concern?
- B. Drone and Missile Warfare Linkage
- C. Russia-Iran Relationship post-Epic Fury
- D. Energy and Economic Effects
- E. Strategic Bandwidth (labeled: Confirmed/Analyst Judgment)

**7. RUSSIA, IRAN, CHINA, NORTH KOREA, BELARUS ASSISTANCE NETWORKS** — Table: Actor, Assistance type, Source, Link, Confidence, Ukraine war impact, U.S./Congressional relevance

**8. ESCALATION RISKS AND WARNING INDICATORS** — Table: Indicator, Low/Medium/High classification, Source, Link, Confidence, Why it matters, U.S. policy/budget implication

**9. CONGRESSIONAL RFI READINESS SECTION** — Table: Likely RFI Question, Short Answer, Source Links, Confidence

**10. DELTA FROM PRIOR REPORT** — What is new vs. prior day? New developments, changed assessments, escalated/de-escalated risks, new funding/defense article/stockpile issues

**11. ANALYST ASSESSMENT** — Evidence-based, no political commentary: What matters most? What to watch? What could become congressional? What could affect budget execution/defense articles/readiness? Most important cross-theater linkage? Confirmed Facts / Analyst Judgment / Cannot Confirm

**12. REQUIRED SOURCE LOG** — Table for EVERY source: #, Source, Title, Date, Link, Topic, Confidence, Notes

**13. CONFIDENCE MATRIX** — Table: Claim/Topic, Confidence (High/Medium/Low/Cannot Confirm), Reason

## STRICT RULES

- Every claim MUST have a source and a direct working web link.
- Do not present unverified claims as fact.
- Clearly label: Confirmed / Likely / Claimed but unverified / Disputed / Cannot confirm.
- If a claim cannot be confirmed, state "I cannot confirm this."
- Clearly label Russian and Ukrainian official claims as such.
- No political commentary. No sensational language. No vague statements without sources.
- Use ONLY credible sources: ISW, CSIS, RAND, RUSI, Atlantic Council, Reuters, AP, BBC, Financial Times, WSJ, NYT, Washington Post, Bloomberg, Politico, Defense News, Breaking Defense, USNI News, War on the Rocks, Kyiv Independent, Ukrinform, official U.S. government/DoD/White House/State Dept/Congress releases, NATO official releases.

Today's date: {date}
Report window: Last 24-48 hours from {date}
"""


def get_report_date() -> str:
    env_date = os.environ.get("REPORT_DATE", "").strip()
    if env_date:
        return env_date
    now = datetime.now(EASTERN)
    return now.strftime("%Y-%m-%d")


def generate_brief(report_date: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = REPORT_PROMPT.format(date=report_date)

    print(f"Generating brief for {report_date} using claude-opus-4-8 with web_search...")

    full_text = []
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 25}],
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if hasattr(event, "type"):
                if event.type == "content_block_start":
                    if hasattr(event, "content_block") and event.content_block.type == "tool_use":
                        print(f"  [Search] Querying: {getattr(event.content_block, 'input', {}).get('query', '...')}")
                elif event.type == "content_block_delta":
                    if hasattr(event, "delta") and hasattr(event.delta, "text"):
                        full_text.append(event.delta.text)

    return "".join(full_text)


def save_report(content: str, report_date: str) -> Path:
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    filename = f"{report_date}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md"
    filepath = reports_dir / filename
    filepath.write_text(content, encoding="utf-8")
    print(f"Report saved: {filepath}")
    return filepath


def main():
    report_date = get_report_date()
    print(f"Starting daily brief generation for {report_date}")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    content = generate_brief(report_date)
    report_path = save_report(content, report_date)

    # Write path to env file for next step
    with open(os.environ.get("GITHUB_ENV", "/dev/null"), "a") as f:
        f.write(f"REPORT_PATH={report_path}\n")
        f.write(f"REPORT_DATE={report_date}\n")

    print("Brief generation complete.")


if __name__ == "__main__":
    main()
