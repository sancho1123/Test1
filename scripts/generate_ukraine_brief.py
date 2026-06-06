#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief Generator
For: OUSW Comptroller Program/Budget Analysts
Runs daily at 05:00 ET via GitHub Actions.
"""

import os
import sys
import smtplib
import argparse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import anthropic

RECIPIENT_EMAIL = "ericjsanchez23@gmail.com"
SENDER_EMAIL = os.environ.get("GMAIL_USER", "ericjsanchez23@gmail.com")
TODAY = datetime.now().strftime("%Y-%m-%d")
REPORT_FILENAME = f"{TODAY}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB"

SYSTEM_PROMPT = """You are a senior defense analyst at the Department of War generating a daily Ukraine-Russia War Analyst Brief.

Your audience: OUSW Comptroller Program/Budget analysts supporting congressional RFIs, senior leader questions, budget and execution inquiries, defense article questions, Ukraine aid questions, and cross-theater impact questions involving Operation Epic Fury / Iran.

CRITICAL RULES:
1. Every major claim MUST have a source with a direct web link.
2. Distinguish clearly: Confirmed / Likely / Claimed but unverified / Disputed / Cannot confirm.
3. Use only credible sources: DoD, State Dept, White House, ISW, CSIS, RAND, RUSI, Reuters, AP, BBC, FT, WSJ, NYT, WaPo, Bloomberg, Politico, Kyiv Independent, etc.
4. If a claim cannot be confirmed, state "I cannot confirm this" — never present unverified claims as fact.
5. No political commentary. No speculation without evidence. No sensational language.
6. Write for analysts who need to answer Congress on short notice: clarity, precision, sourcing.
7. The report should be a 10-minute read, broken into 5 clear chunks."""


def build_report_prompt() -> str:
    return f"""Search for and compile the Daily Ukraine-Russia War Analyst Brief for {TODAY}.

Search for developments from the last 24-48 hours across these topics:
- Ukraine-Russia battlefield activity (frontlines, strikes, air defense, Black Sea)
- Ukraine defense articles, stockpile levels, replenishment needs
- US defense budget, Ukraine aid, PDA/USAI accounts, congressional action
- Defense industrial base: ammunition, missile, interceptor production
- Russia support from Iran, North Korea, China, Belarus
- Operation Epic Fury / Iran — any linkage to Ukraine or shared stockpiles
- Escalation indicators, nuclear signaling, NATO posture

Generate the complete report in Markdown using this EXACT structure:

---

# Daily Ukraine–Russia War Analyst Brief
**Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury Cross-Theater**
**Date: {TODAY} | UNCLASSIFIED // FOR OFFICIAL USE ONLY**
**Prepared for: OUSW Comptroller Program/Budget Analysts**

---

## PART I — SENIOR LEADER SNAPSHOT *(Chunk 1 of 5)*

### A. BOTTOM LINE UP FRONT (BLUF)
*3-5 critical bullets. Format: [Tag] Summary. Source: Name, "Title," Date, URL. Confidence: Level.*

### B. TOP ISSUES — OUSW COMPTROLLER P/B ANALYSTS
*5-7 tagged bullets. Tags: [Funding] [Appropriations] [Execution] [PDA] [USAI] [Defense Articles] [Stockpiles] [Replenishment] [Congressional RFI] [Readiness] [Epic Fury/Iran Linkage]. Each explains: what happened, why it matters, likely congressional question.*

### C. WATCH ITEMS — NEXT 7 DAYS
*5 items: Indicator | Why it matters | Budget/defense article implication | Source link*

### D. LIKELY CONGRESSIONAL RFI QUESTIONS TODAY
*5-10 questions based on today's reporting*

---

## PART II — ANALYST ANNEX

### 1. EXECUTIVE SUMMARY *(Chunk 2 of 5)*
*7-10 bullets. Format: [Tag] | Summary | Why it matters | Source | Link | Confidence*
*Tags: [Military] [Funding] [Appropriations] [Defense Articles] [Stockpiles] [DIB] [Replenishment] [Readiness] [Congressional Interest] [Epic Fury/Iran Linkage] [Escalation Risk] [Sanctions] [Energy]*

### 2. BATTLEFIELD AND MILITARY OPERATIONS *(Chunk 3 of 5)*
*Cover: frontline changes, offensives, missile/drone attacks, air defense activity, Black Sea, Crimea, force posture, territorial changes, casualties (credible sources only).*

| Event | Location | Date | Source | Link | Confidence | Significance |
|-------|----------|------|--------|------|------------|--------------|

### 3. DEFENSE ARTICLES, WEAPONS, STOCKPILES, AND MUNITIONS *(Chunk 4 of 5)*

**A. US-Provided Defense Articles**
Track: Patriot, NASAMS, HIMARS, GMLRS, ATACMS, Javelins, Stingers, 155mm, 105mm, Bradleys, Abrams, Strykers, MRAPs, air defense radars, counter-UAS, drones, EW, F-16 support, sustainment packages.

**B. Allied/Partner Defense Articles**
Track: NATO, UK, Germany, France, Poland, Baltic, Nordic, Canada, Australia, Japan, South Korea.

**C. Stockpile and Readiness Issues**
US/allied depletion, interceptor shortages, artillery shortages, replenishment delays, production constraints, multi-theater demand.

**D. Defense Article Analysis**

| Article | Status | Source | Link | Confidence | Ukraine Battlefield Impact | US Readiness Impact | Congressional Interest | Appropriations Implication |
|---------|--------|--------|------|------------|---------------------------|--------------------|-----------------------|---------------------------|

### 4. DEFENSE INDUSTRIAL BASE AND PRODUCTION

| Entity | System/Munition | Issue or Improvement | Ukraine Impact | US Readiness Impact | Source | Link | Confidence |
|--------|----------------|---------------------|----------------|--------------------|---------|----|------------|

### 5. FUNDING, BUDGET, APPROPRIATIONS, CONGRESSIONAL RELEVANCE

| Funding Item | Account/Mechanism | Amount (if sourced) | Source | Link | Confidence | Comptroller Relevance | Potential RFI |
|-------------|------------------|---------------------|--------|------|------------|----------------------|---------------|

*If no new item found: "No new confirmed funding, appropriations, or execution development was identified in the reporting window."*

### 6. OPERATION EPIC FURY / IRAN — UKRAINE LINKAGE *(Chunk 5 of 5)*
*If no credible connection: "I cannot confirm a direct linkage between Operation Epic Fury and the Ukraine-Russia War in today's reporting."*

**A. Weapons/Stockpile Competition** — Are both conflicts drawing from same inventory? (Patriot, THAAD, SM variants, NASAMS, counter-drone, PGMs)

**B. Drone/Missile Warfare Linkage** — Iranian-origin drones in Ukraine, shared technology, Shahed-type systems, ballistic/cruise missile threats

**C. Russia-Iran Relationship** — Does Epic Fury affect Russia-Iran cooperation? Iranian weapons to Russia, Russian diplomatic/military support for Iran.

**D. Energy/Economic Effects** — Oil prices, LNG, Strait of Hormuz, Black Sea energy, Russian revenue, sanctions enforcement

**E. Strategic Bandwidth and Force Allocation** — CENTCOM vs EUCOM prioritization, congressional appetite for Ukraine funding, allied burden-sharing

*Label each: Confirmed evidence / Credible reporting / Analyst judgment*

### 7. RUSSIA, IRAN, CHINA, NORTH KOREA, BELARUS, SANCTIONS NETWORKS

| Actor | Assistance Type | Source | Link | Confidence | War Impact | US Policy/Congressional Relevance |
|-------|----------------|--------|------|------------|------------|----------------------------------|

### 8. ESCALATION RISKS

| Risk Indicator | Risk Level | Source | Link | Confidence | Why It Matters | US Policy/Budget Implication |
|---------------|------------|--------|------|------------|----------------|------------------------------|

### 9. CONGRESSIONAL RFI READINESS

| Likely RFI Question | Short Answer | Source Links | Confidence |
|--------------------|-------------|--------------|------------|

### 10. DELTA FROM PRIOR REPORT
*(No prior report available for comparison. Items to track in subsequent deltas listed below.)*

### 11. ANALYST ASSESSMENT

**Confirmed Facts:**
- [list with sources]

**Analyst Judgment:**
- [clearly labeled as judgment]

**Cannot Confirm:**
- [list items that cannot be confirmed]

*What matters most today | What to watch next 7 days | Congressional risk | Budget execution risk | Readiness concern | Cross-theater linkage*

### 12. SOURCE LOG

| # | Source | Title | Date | Link | Topic | Confidence | Notes |
|---|--------|-------|------|------|-------|------------|-------|

*Notes: official source / analysis / paywalled / Russian claim / Ukrainian claim*

### 13. CONFIDENCE MATRIX

| Claim/Topic | Confidence | Reason |
|-------------|------------|--------|

---
*Report generated: {TODAY} | UNCLASSIFIED // FOR OFFICIAL USE ONLY | OUSW Comptroller P/B*"""


def generate_report() -> str:
    """Generate the daily analyst brief using Claude with web search."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    print(f"Searching for latest Ukraine-Russia War developments ({TODAY})...")

    response = client.beta.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 25
        }],
        messages=[{"role": "user", "content": build_report_prompt()}],
        betas=["web-search-2025-03-05"]
    )

    report_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            report_text += block.text

    if not report_text.strip():
        raise RuntimeError("Claude returned an empty report. Check API key and model availability.")

    return report_text


def build_html_email(report_content: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 960px; margin: 0 auto; padding: 0; color: #1a1a1a; background: #f4f4f4; }}
  .header {{ background: #1a1a2e; color: white; padding: 20px 30px; }}
  .header h1 {{ margin: 0 0 6px; font-size: 20px; }}
  .header p {{ margin: 3px 0; font-size: 12px; color: #ccd; }}
  .content {{ background: white; padding: 25px 30px; }}
  h2 {{ color: #1a1a2e; border-bottom: 2px solid #1a1a2e; padding-bottom: 4px; margin-top: 28px; }}
  h3 {{ color: #16213e; margin-top: 20px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }}
  th {{ background: #1a1a2e; color: white; padding: 8px 10px; text-align: left; font-size: 12px; }}
  td {{ padding: 7px 10px; border: 1px solid #ddd; vertical-align: top; font-size: 13px; }}
  tr:nth-child(even) {{ background: #f8f8f8; }}
  pre {{ white-space: pre-wrap; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.65; margin: 0; }}
  .footer {{ background: #1a1a2e; color: #99a; padding: 12px 30px; font-size: 11px; }}
</style>
</head>
<body>
<div class="header">
  <h1>Daily Ukraine–Russia War Analyst Brief</h1>
  <p>Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury Cross-Theater</p>
  <p>Date: {TODAY} &nbsp;|&nbsp; UNCLASSIFIED // FOR OFFICIAL USE ONLY &nbsp;|&nbsp; OUSW Comptroller Program/Budget</p>
</div>
<div class="content">
<pre>{report_content}</pre>
</div>
<div class="footer">
  UNCLASSIFIED // FOR OFFICIAL USE ONLY &nbsp;|&nbsp; Prepared for OUSW Comptroller Program/Budget Analysts &nbsp;|&nbsp; {TODAY}
</div>
</body>
</html>"""


def send_email(report_content: str, dry_run: bool = False):
    """Send the report via Gmail SMTP SSL."""
    if dry_run:
        print(f"[DRY RUN] Would email report to {RECIPIENT_EMAIL}")
        return

    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_password:
        print("WARNING: GMAIL_APP_PASSWORD not set — skipping email. Report saved locally.")
        return

    subject = f"Daily Ukraine-Russia War Analyst Brief — {TODAY}"

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    body = MIMEMultipart("alternative")
    body.attach(MIMEText(report_content, "plain", "utf-8"))
    body.attach(MIMEText(build_html_email(report_content), "html", "utf-8"))
    msg.attach(body)

    attachment = MIMEApplication(report_content.encode("utf-8"), Name=f"{REPORT_FILENAME}.md")
    attachment["Content-Disposition"] = f'attachment; filename="{REPORT_FILENAME}.md"'
    msg.attach(attachment)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, gmail_password)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print(f"Report emailed to {RECIPIENT_EMAIL}")


def main():
    parser = argparse.ArgumentParser(description="Generate Daily Ukraine-Russia War Analyst Brief")
    parser.add_argument("--dry-run", action="store_true", help="Generate report without sending email")
    parser.add_argument("--output-dir", default="reports", help="Directory to save report")
    args = parser.parse_args()

    print(f"=== Daily Ukraine-Russia War Analyst Brief Generator ===")
    print(f"Date:      {TODAY}")
    print(f"Recipient: {RECIPIENT_EMAIL}")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    report = generate_report()
    print(f"Report generated: {len(report):,} characters")

    os.makedirs(args.output_dir, exist_ok=True)
    report_path = os.path.join(args.output_dir, f"{REPORT_FILENAME}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved: {report_path}")

    send_email(report, dry_run=args.dry_run)
    print("Done.")


if __name__ == "__main__":
    main()
