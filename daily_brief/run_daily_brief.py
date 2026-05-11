#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief
OUSW Comptroller Program/Budget Support
Runs daily at 05:00 ET via cron.

Requirements (set in .env file or environment):
  ANTHROPIC_API_KEY    - Anthropic API key
  GMAIL_SENDER         - Gmail address to send FROM (must have App Password enabled)
  GMAIL_APP_PASSWORD   - Gmail App Password (not your regular password)
  GMAIL_RECIPIENT      - Recipient email (default: ericjsanchez23@gmail.com)
  SERPAPI_KEY          - (Optional) SerpAPI key for richer web search results
"""

import os
import sys
import json
import datetime
import smtplib
import logging
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

# Load .env file if present
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# Config
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GMAIL_SENDER = os.environ.get("GMAIL_SENDER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
GMAIL_RECIPIENT = os.environ.get("GMAIL_RECIPIENT", "ericjsanchez23@gmail.com")
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"brief_{datetime.date.today()}.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def build_report_prompt(today: str) -> str:
    return f"""You are a senior defense analyst supporting the Department of War / OUSW Comptroller Program/Budget office. Today's date is {today}.

Generate a comprehensive daily analyst brief on the Ukraine-Russia War. Search for developments from the LAST 24-48 HOURS. Use your web search capability to find the most current reporting from credible sources.

REQUIRED SEARCHES to conduct before writing (conduct ALL of these):
1. "Ukraine Russia war {today} frontline battlefield latest"
2. "US defense articles weapons Ukraine aid {today}"
3. "Operation Epic Fury Iran ceasefire {today}"
4. "Ukraine aid funding Congress USAI PDA {today}"
5. "Russia Iran North Korea China weapons Ukraine {today}"
6. "Patriot interceptor stockpile Ukraine shortage {today}"
7. "US defense industrial base munitions production {today}"
8. "Strait of Hormuz blockade shipping {today}"

After searching, write the complete report below. Every claim must cite a source with a working web URL. If a claim cannot be confirmed with a source, state "I cannot confirm this."

---

# DAILY UKRAINE-RUSSIA WAR ANALYST BRIEF
## Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury
### {today} | UNCLASSIFIED | OUSW Comptroller P/B

---

## PART I — SENIOR LEADER SNAPSHOT

### A. BOTTOM LINE UP FRONT (BLUF)
[5 bullets. Each: What changed, why it matters, source name + URL, confidence: HIGH/MEDIUM/LOW]
Tag each bullet: [Defense Articles] [Funding] [Stockpiles] [Epic Fury/Iran] [Military] etc.

### B. TOP ISSUES FOR OUSW COMPTROLLER P/B ANALYSTS
[7 bullets tagged: [Funding] [Appropriations] [Execution] [PDA] [USAI] [Defense Articles] [Stockpiles] [Replenishment] [Congressional RFI] [Readiness] [Epic Fury/Iran Linkage]]
Each bullet: What happened | Why it matters | Likely congressional question | Source URL

### C. WATCH ITEMS — NEXT 7 DAYS
[5 watch items: Indicator | Why it matters | Budget/defense article implication | Source URL]

### D. MOST LIKELY CONGRESSIONAL RFI QUESTIONS TODAY
[10 questions based on today's reporting]

---

## PART II — ANALYST ANNEX

### 1. EXECUTIVE SUMMARY
[8 bullets with tags: [Military] [Funding] [Defense Articles] [Stockpiles] [DIB] [Replenishment] [Epic Fury/Iran Linkage] [Escalation Risk] [Congressional Interest]]
Each: Topic | Summary | Why it matters | Source + URL | Confidence

### 2. BATTLEFIELD AND MILITARY OPERATIONS
[Cover: frontline changes, Russian offensives, Ukrainian counteroffensives, missile/drone attacks, air defense, Black Sea, casualties. Use table format: Event | Location | Date | Source+URL | Confidence | Significance]

### 3. DEFENSE ARTICLES, WEAPONS, STOCKPILES, AND MUNITIONS
[MANDATORY. Track: Patriot, NASAMS, HIMARS, GMLRS, ATACMS, Javelins, 155mm, Bradley, F-16, drones, counter-UAS, allied contributions. For each: What article | Status (transferred/requested/depleted/delayed/produced) | Source+URL | Confidence | Ukraine battlefield impact | U.S. readiness impact | Congressional interest | Appropriations implication]

### 4. DEFENSE INDUSTRIAL BASE AND PRODUCTION
[Analyze: Lockheed, Raytheon, BAE, General Dynamics, European producers. Patriot PAC-3, GMLRS, ATACMS, 155mm, drones. Include: Company | System | Production status | Ukraine impact | Readiness impact | Source+URL | Confidence]

### 5. FUNDING, BUDGET, APPROPRIATIONS, AND CONGRESSIONAL RELEVANCE
[Cover: USAI, PDA, FMF, supplementals, reprogramming, coalition contributions, PURL. Table: Funding item | Account/mechanism | Amount (if sourced) | Source+URL | Confidence | Comptroller relevance | Potential RFI]
If no new funding development: state "No new confirmed funding development identified in the reporting window."

### 6. OPERATION EPIC FURY / IRAN AND UKRAINE-RUSSIA LINKAGE
[MANDATORY. Research confirmed connections. If no connection confirmed, state it.
A. Weapons/Stockpile Competition (especially Patriot, THAAD, SM-series, counter-drone)
B. Drone/Missile Warfare Linkage (Shahed, Iranian drones, lessons learned)
C. Russia-Iran Relationship Post-Epic Fury
D. Energy/Economic Effects (Hormuz, oil prices, LNG, European energy)
E. Strategic Bandwidth (CENTCOM vs EUCOM, congressional appetite, allied burden sharing)
Label each: Confirmed Evidence | Credible Reporting | Analyst Judgment]

### 7. RUSSIA, IRAN, CHINA, NORTH KOREA, BELARUS, SANCTIONS NETWORKS
[Table: Actor | Assistance type | Details | Source+URL | Confidence | Ukraine impact | Congressional/budget relevance]

### 8. ESCALATION RISKS AND WARNING INDICATORS
[Table: Indicator | Risk level (HIGH/MEDIUM/LOW) | Source+URL | Confidence | Why it matters | Possible policy/budget implication]

### 9. CONGRESSIONAL RFI READINESS
[Table: Likely RFI Question | Short Answer | Source Links | Confidence]
Cover: battlefield changes, defense articles needed, stockpile status, Epic Fury/Ukraine overlap, funding streams, supplementals, Russia's supply chain, sanctions, DIB constraints.

### 10. DELTA FROM PRIOR REPORT
[Compare to prior day. Identify: new developments, changed assessments, escalated/de-escalated risks, new funding/defense article/stockpile/congressional issues.]

### 11. ANALYST ASSESSMENT
[Label clearly: Confirmed Facts | Analyst Judgment | Cannot Confirm]
Answer: What matters most today? What to watch next 7 days? Possible congressional issues? Budget execution risks? Defense article/stockpile implications? Readiness risk? Cross-theater linkage?

### 12. SOURCE LOG
[MANDATORY table: # | Source | Title | Date | URL | Topic | Confidence | Notes]
Every source must have a direct web URL. Label: official source / analysis / paywalled / Ukrainian claim / Russian claim as applicable.

### 13. CONFIDENCE MATRIX
[Table: Claim/Topic | Confidence | Reason]
HIGH = official source or multiple credible independent sources
MEDIUM = credible source, not independently confirmed
LOW = single-source, unclear, or disputed
Cannot confirm = insufficient reliable sourcing

---

QUALITY CHECK before finalizing:
- Every major claim has a source with a working URL
- Unverified claims are clearly labeled
- Russian and Ukrainian government claims labeled as such
- All required sections present
- Budget, appropriations, execution, stockpile, readiness implications identified
- Epic Fury / Iran linkage section complete
- Report is useful for OUSW Comptroller P/B analysts responding to congressional RFIs

Write in direct, professional analyst style. No political commentary. No unsupported claims. No vague statements without listed sources. This should read like a daily senior analyst brief, not a media summary. Target: 10-minute read."""


def generate_report(today: str) -> str:
    """Call Claude API with web search to generate the report."""
    try:
        import anthropic
    except ImportError:
        log.error("anthropic package not installed. Run: pip3 install anthropic")
        sys.exit(1)

    if not ANTHROPIC_API_KEY:
        log.error("ANTHROPIC_API_KEY not set. Add it to daily_brief/.env")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = build_report_prompt(today)

    log.info("Calling Claude API to generate report (this may take 2-4 minutes)...")

    # Use claude-sonnet-4-6 with web search tool
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 20}],
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract text from response
    report_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            report_text += block.text
        elif block.type == "tool_use":
            log.info(f"  Web search: {block.input.get('query', '')[:80]}")

    log.info(f"Report generated. Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}")
    return report_text


def markdown_to_html(text: str, today: str) -> str:
    """Convert markdown report to styled HTML email."""
    lines = text.split("\n")
    html_lines = []
    in_table = False
    in_code = False

    style = """
    <style>
      body{font-family:Arial,sans-serif;font-size:13px;color:#1a1a1a;max-width:950px;margin:0 auto;padding:16px}
      h1{background:#1a3a5c;color:#fff;padding:10px 14px;font-size:16px;margin:0 0 4px 0}
      h2{background:#2c5f8a;color:#fff;padding:7px 12px;font-size:14px;margin:16px 0 4px 0}
      h3{background:#d9e8f4;color:#1a3a5c;padding:5px 10px;font-size:13px;margin:12px 0 4px 0}
      table{border-collapse:collapse;width:100%;font-size:12px;margin:6px 0}
      th{background:#1a3a5c;color:#fff;padding:5px 7px;text-align:left}
      td{border:1px solid #ccc;padding:4px 7px;vertical-align:top}
      tr:nth-child(even){background:#f4f8fc}
      ul,ol{margin:4px 0;padding-left:20px}
      li{margin-bottom:3px}
      a{color:#1a3a5c}
      hr{border:1px solid #2c5f8a;margin:14px 0}
      .footer{background:#f4f4f4;border-top:2px solid #1a3a5c;padding:8px;font-size:11px;color:#555;margin-top:16px}
      blockquote{background:#fff3cd;border-left:4px solid #f0a500;margin:6px 0;padding:6px 10px}
      code{background:#f4f4f4;padding:1px 4px;border-radius:3px;font-size:11px}
    </style>
    """

    html_lines.append(f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{style}</head><body>""")
    html_lines.append(f"""<h1>&#x1F6E1; DAILY UKRAINE-RUSSIA WAR ANALYST BRIEF &mdash; {today}<br>
    Defense Articles &bull; Stockpiles &bull; Budget &bull; Congressional RFI &bull; Operation Epic Fury<br>
    UNCLASSIFIED &bull; OUSW Comptroller P/B</h1>""")

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            html_lines.append(f"<code>{stripped}</code><br>")
            continue

        # Table detection
        if stripped.startswith("|") and "|" in stripped[1:]:
            if not in_table:
                in_table = True
                html_lines.append("<table>")
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            is_separator = all(set(c.replace("-", "").replace(":", "")) <= {""} for c in cells)
            if is_separator:
                continue
            if html_lines and "<table>" in html_lines[-2] or (len(html_lines) > 1 and "<table>" == html_lines[-1]):
                tag = "th"
            else:
                tag = "td"
            row = "".join(f"<{tag}>{_linkify(c)}</{tag}>" for c in cells)
            html_lines.append(f"<tr>{row}</tr>")
            continue
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False

        # Headings
        if stripped.startswith("#### "):
            html_lines.append(f"<h4>{_linkify(stripped[5:])}</h4>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{_linkify(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{_linkify(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            html_lines.append(f"<h1>{_linkify(stripped[2:])}</h1>")
        elif stripped.startswith("---") or stripped.startswith("==="):
            html_lines.append("<hr>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html_lines.append(f"<ul><li>{_linkify(stripped[2:])}</li></ul>")
        elif stripped.startswith("> "):
            html_lines.append(f"<blockquote>{_linkify(stripped[2:])}</blockquote>")
        elif stripped == "":
            html_lines.append("<br>")
        else:
            # Inline bold/italic
            html_lines.append(f"<p style='margin:3px 0'>{_linkify(stripped)}</p>")

    if in_table:
        html_lines.append("</table>")

    today_str = today
    html_lines.append(f"""<div class="footer">
      Classification: UNCLASSIFIED // FOR OFFICIAL USE &bull;
      Generated: {today_str} 05:00 ET &bull;
      File: {today_str}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB &bull;
      Distribution: OUSW Comptroller P/B Analysts
    </div></body></html>""")

    return "\n".join(html_lines)


def _linkify(text: str) -> str:
    """Convert markdown links and bold/italic to HTML."""
    import re
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Inline code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links [text](url)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def send_email(subject: str, html_body: str, plain_body: str) -> bool:
    """Send email via Gmail SMTP with App Password."""
    if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
        log.warning("Gmail credentials not configured. Email not sent.")
        log.warning("Set GMAIL_SENDER and GMAIL_APP_PASSWORD in daily_brief/.env")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_SENDER
    msg["To"] = GMAIL_RECIPIENT
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        log.info(f"Sending email to {GMAIL_RECIPIENT} via Gmail SMTP...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, GMAIL_RECIPIENT, msg.as_string())
        log.info("Email sent successfully.")
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("Gmail SMTP authentication failed. Check GMAIL_SENDER and GMAIL_APP_PASSWORD.")
        log.error("App Password setup: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        log.error(f"Failed to send email: {e}")
        return False


def save_report(report_text: str, today: str) -> Path:
    """Save report to disk as a backup."""
    out_dir = LOG_DIR / "reports"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"{today}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.txt"
    out_file.write_text(report_text, encoding="utf-8")
    log.info(f"Report saved to: {out_file}")
    return out_file


def main():
    today = datetime.date.today().isoformat()
    log.info(f"=== Daily Ukraine-Russia War Analyst Brief | {today} ===")

    # 1. Generate the report via Claude API with web search
    report_text = generate_report(today)

    # 2. Save report to disk
    save_report(report_text, today)

    # 3. Convert to HTML for email
    html_body = markdown_to_html(report_text, today)
    plain_body = textwrap.dedent(f"""
        Daily Ukraine-Russia War Analyst Brief | {today}
        OUSW Comptroller P/B | UNCLASSIFIED

        [This email is best viewed in HTML. If you see this text, your email client
        does not render HTML. The full report is in the HTML version of this email.]

        Report saved to: daily_brief/logs/reports/{today}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.txt
    """).strip()

    # 4. Send email
    subject = (
        f"{today} | Daily Ukraine-Russia War Analyst Brief | "
        "Defense Articles, Stockpiles, Budget, Congressional RFI & "
        "Operation Epic Fury | OUSW P/B"
    )
    sent = send_email(subject, html_body, plain_body)

    if not sent:
        log.warning("Email delivery failed or skipped. Report saved locally. Check logs.")
        sys.exit(1)

    log.info("=== Daily brief complete. ===")


if __name__ == "__main__":
    main()
