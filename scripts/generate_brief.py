#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief Generator
Calls Claude API with web search to produce analyst-grade daily report.
"""

import os
import sys
import json
import datetime
import anthropic

REPORT_DATE = datetime.date.today().strftime("%Y-%m-%d")
OUTPUT_FILE = "reports/latest_brief.md"
ARCHIVE_FILE = f"reports/{REPORT_DATE}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md"

SYSTEM_PROMPT = """You are a senior intelligence analyst supporting the Department of War / OUSW Comptroller Program/Budget office.
Your task is to produce a daily analyst-grade brief on the Ukraine-Russia War for analysts who need to respond to Congressional RFIs, senior leader questions, defense article/stockpile inquiries, and budget/execution questions.

Rules:
- Every major claim must have a source, title, date, and direct URL.
- Clearly distinguish: Confirmed / Likely / Claimed but unverified / Cannot confirm.
- Do not present unverified claims as fact.
- Use direct language, short paragraphs, clear bullets, and tables.
- No political commentary. No speculation without evidence.
- Prioritize official sources, then think tanks, then major news outlets.
- Label Russian and Ukrainian official claims as claims unless independently confirmed.
- Write for a 10-minute analyst read."""

USER_PROMPT = f"""Today is {REPORT_DATE}.

Generate the full Daily Ukraine-Russia War Analyst Brief for OUSW Comptroller Program/Budget analysts.

Search the web for developments from the last 24-48 hours covering:
1. Battlefield and military operations (frontlines, strikes, drone activity, Russian/Ukrainian force posture)
2. Defense articles, weapons, stockpiles, and munitions (Patriot, HIMARS, GMLRS, ATACMS, 155mm, air defense)
3. U.S. and allied weapons support to Ukraine (PDA, USAI, NATO contributions)
4. Funding, appropriations, and Congressional activity (USAI, FMF, supplementals, reprogramming)
5. Operation Epic Fury / Iran cross-theater linkage (stockpile competition, Iran-Russia relationship)
6. Russia's external support networks (Iran, North Korea, China, Belarus)
7. Escalation risks and warning indicators (nuclear signaling, NATO border incidents)
8. Defense industrial base developments (production capacity, replenishment timelines)

Use the following report structure exactly:

---
# DAILY UKRAINE–RUSSIA WAR ANALYST BRIEF
**Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury Cross-Theater Impacts**
**Date: {REPORT_DATE} | UNCLASSIFIED // FOR OFFICIAL USE ONLY**
**Prepared for: OUSW Comptroller Program/Budget Analysts**

---
## PART I — SENIOR LEADER SNAPSHOT

### A. BOTTOM LINE UP FRONT (BLUF)
[5 bullets: What changed in last 24-48 hrs, what matters most, funding/defense article impacts, Epic Fury overlap]
[Each bullet: Source name, URL, Confidence]

### B. TOP ISSUES FOR OUSW COMPTROLLER P/B ANALYSTS
[7 bullets tagged [Funding] [Appropriations] [Execution] [PDA] [USAI] [Defense Articles] [Stockpiles] [Replenishment] [Congressional RFI] [Readiness] [Epic Fury / Iran Linkage]]

### C. WATCH ITEMS — NEXT 7 DAYS
[5 items: Indicator | Why it matters | Budget/defense article implication | Source link]

### D. MOST LIKELY CONGRESSIONAL RFI QUESTIONS TODAY
[8-10 numbered questions]

---
## PART II — ANALYST ANNEX

### 1. EXECUTIVE SUMMARY
[8-10 bullets: Topic tag | One-sentence summary | Why it matters | Source | URL | Confidence]

### 2. BATTLEFIELD AND MILITARY OPERATIONS
[Table: Event | Location | Date | Source | Link | Confidence | Significance]

### 3. DEFENSE ARTICLES, WEAPONS, STOCKPILES, AND MUNITIONS
#### A. U.S.-Provided Defense Articles
#### B. Allied / Partner Defense Articles
#### C. Stockpile and Readiness Issues
#### D. Defense Article Analysis Table

### 4. DEFENSE INDUSTRIAL BASE AND PRODUCTION CAPACITY

### 5. FUNDING, BUDGET, APPROPRIATIONS, AND CONGRESSIONAL RELEVANCE
[Table: Funding Item | Account/Mechanism | Amount | Source | Link | Confidence | Comptroller Relevance | Potential RFI]

### 6. OPERATION EPIC FURY / IRAN AND UKRAINE–RUSSIA WAR LINKAGE
#### A. Weapons and Stockpile Competition
#### B. Drone and Missile Warfare Linkage
#### C. Russia–Iran Relationship
#### D. Energy and Economic Effects
#### E. Strategic Bandwidth and Force Allocation

### 7. RUSSIA, IRAN, CHINA, NORTH KOREA, BELARUS, AND SANCTIONS-EVASION NETWORKS

### 8. ESCALATION RISKS AND WARNING INDICATORS
[Table: Indicator | Source | Link | Confidence | Why It Matters | Policy/Budget Implication]

### 9. CONGRESSIONAL RFI READINESS SECTION
[Table: Likely RFI Question | Short Answer | Source Links | Confidence]

### 10. DELTA FROM PRIOR REPORT

### 11. ANALYST ASSESSMENT
[Label: Confirmed Facts / Analyst Judgment / Cannot Confirm]

### 12. REQUIRED NEWS ARTICLE / SOURCE LOG
[Table: # | Source | Title | Date | Link | Topic | Confidence | Notes]

### 13. CONFIDENCE MATRIX
[Table: Claim/Topic | Confidence | Reason]
---

Before finalizing, verify every major claim is sourced and labeled. If a claim cannot be confirmed, state 'I cannot confirm this.'
"""


def generate_brief() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"Generating daily brief for {REPORT_DATE}...")

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT}
        ],
    )

    return message.content[0].text


def save_report(content: str) -> None:
    os.makedirs("reports", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Report saved: {OUTPUT_FILE}")
    print(f"Archive saved: {ARCHIVE_FILE}")


if __name__ == "__main__":
    brief = generate_brief()
    save_report(brief)
    print("Done.")
