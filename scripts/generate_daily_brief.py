#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief Generator
Generates and emails a daily analyst-grade report for OUSW Comptroller P/B analysts.
Schedule: 5:00 AM Eastern Time daily via GitHub Actions.
"""

import os
import sys
import datetime
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic


# ── Configuration ──────────────────────────────────────────────────────────────

RECIPIENT_EMAIL = "ericjsanchez23@gmail.com"
SENDER_EMAIL    = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_APP_PASSWORD", "")  # Gmail App Password
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BRAVE_API_KEY     = os.environ.get("BRAVE_API_KEY", "")      # Optional: for web search tool

TODAY = datetime.date.today().strftime("%Y-%m-%d")
REPORT_TITLE = f"Daily Ukraine–Russia War Analyst Brief — {TODAY}"
FILE_NAME    = f"{TODAY}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB"


# ── System Prompt ───────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior Department-level defense analyst producing a daily classified-style \
unclassified analyst brief for the Department of War / OUSW Comptroller Program/Budget office. \
Your audience is analysts who support congressional RFIs, senior leader briefings, and budget \
execution decisions related to Ukraine aid, defense articles, stockpile replenishment, and \
cross-theater impacts involving Operation Epic Fury / Iran.

WRITING RULES:
- Use direct, executive language. Short paragraphs. Bullets and tables where helpful.
- No political commentary. No unsupported claims. No sensational language.
- Every major claim must cite a source with a direct web link.
- Clearly label: Confirmed | Likely | Claimed but unverified | Disputed | Cannot confirm
- Label Russian and Ukrainian government claims as such unless independently corroborated.
- If a claim cannot be confirmed, explicitly state "I cannot confirm this."
- Prioritize DoD, White House, State Dept, NATO, CSIS, ISW, RAND, RUSI, Atlantic Council,
  Reuters, AP, BBC, FT, WSJ, NYT, WaPo, Defense News, Breaking Defense, USNI News.

REPORT STRUCTURE:
1. PART I: SENIOR LEADER SNAPSHOT (target: 10-minute read)
   A. Bottom Line Up Front (3–5 sourced bullets)
   B. Top Issues for OUSW Comptroller P/B Analysts (5–7 tagged bullets)
   C. Watch Items for Next 7 Days (5 items)
   D. Most Likely Congressional RFI Questions Today (5–10 questions)

2. PART II: ANALYST ANNEX
   1. Executive Summary (7–10 sourced bullets with topic tags)
   2. Battlefield and Military Operations
   3. Defense Articles, Weapons, Stockpiles, and Munitions (MANDATORY)
   4. Defense Industrial Base and Production Capacity
   5. Funding, Budget, Appropriations, and Congressional Relevance
   6. Operation Epic Fury / Iran and Ukraine–Russia War Linkage (MANDATORY)
   7. Russia, Iran, China, North Korea, Belarus, and Sanctions-Evasion Networks
   8. Escalation Risks and Warning Indicators
   9. Congressional RFI Readiness Section (table format)
   10. Delta From Prior Report
   11. Analyst Assessment (Confirmed Facts | Analyst Judgment | Cannot Confirm)
   12. Source Log (table: #, Source, Title, Date, Link, Topic, Confidence, Notes)
   13. Confidence Matrix (table: Claim/Topic, Confidence, Reason)

TOPIC TAGS TO USE: [Military] [Funding] [Appropriations] [Defense Articles] [Stockpiles]
[DIB] [Replenishment] [Readiness] [Congressional Interest] [Epic Fury / Iran Linkage]
[Escalation Risk] [Sanctions] [Energy] [PDA] [USAI] [Congressional RFI]

OUTPUT FORMAT: Full Markdown with tables and headers. Every source must have a direct URL link."""


# ── Report Generation Prompt ────────────────────────────────────────────────────

def build_user_prompt(today_str: str) -> str:
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%B %d, %Y")
    today_fmt = datetime.date.today().strftime("%B %d, %Y")
    return f"""Generate the Daily Ukraine–Russia War Analyst Brief for {today_fmt}.

RESEARCH WINDOW: Focus on developments from the last 24–48 hours (approximately {yesterday} through {today_fmt}).

SEARCH FOR THE FOLLOWING TOPICS:
1. Ukraine–Russia war battlefield developments (last 24–48 hours) — frontline, missile attacks, drone attacks, Oreshnik, air defense
2. U.S. defense articles and weapons transfers or requests related to Ukraine
3. Patriot / PAC-3 MSE / NASAMS / THAAD interceptor stockpile status and Epic Fury depletion
4. Operation Epic Fury / Iran status — ceasefire, CENTCOM operations, Strait of Hormuz
5. FY2026 Ukraine funding — USAI, PDA, appropriations, any new supplemental activity
6. Russia CRINK support — Iran drones, North Korea troops/artillery, China dual-use tech
7. Peace talks / ceasefire negotiations status
8. Defense industrial base — munitions production, replenishment rates, production lead times
9. Congressional activity related to Ukraine aid, defense articles, or oversight
10. Escalation indicators — nuclear signaling, Oreshnik use, attacks on civilian infrastructure

MANDATORY REQUIREMENTS:
- Every major claim must include a direct web link (format: [Source Name](URL))
- Label confidence: High | Medium | Low | Cannot confirm
- Label Russian/Ukrainian government claims as such
- Address Operation Epic Fury / Ukraine linkage in dedicated section
- Include source log table at end
- Include confidence matrix at end

DATE: {today_str}
REPORT TITLE: Daily Ukraine–Russia War Analyst Brief — Defense Articles, Stockpiles, Budget, Congressional RFI, and Operation Epic Fury Cross-Theater Impacts
FILE NAME: {today_str}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB"""


# ── Claude API Call ─────────────────────────────────────────────────────────────

def generate_report() -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    tools = []
    if BRAVE_API_KEY:
        tools = [
            {
                "name": "web_search",
                "description": "Search the web for current news and reporting.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                    },
                    "required": ["query"],
                },
            }
        ]

    messages = [
        {"role": "user", "content": build_user_prompt(TODAY)}
    ]

    print(f"[{TODAY}] Generating report via Claude API...")

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=tools if tools else anthropic.NOT_GIVEN,
    )

    # Extract text content
    report_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            report_text += block.text

    if not report_text.strip():
        raise ValueError("Empty report generated — aborting email send.")

    return report_text


# ── Markdown → HTML Conversion ──────────────────────────────────────────────────

def markdown_to_html(md_text: str) -> str:
    """Convert basic Markdown to HTML for email. Uses mistune if available, else basic conversion."""
    try:
        import mistune
        return mistune.html(md_text)
    except ImportError:
        pass

    # Minimal fallback converter
    import re
    html = md_text
    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    # Links
    html = re.sub(r'\[(.+?)\]\((https?://[^\)]+)\)', r'<a href="\2">\1</a>', html)
    # Horizontal rules
    html = re.sub(r'^---$', r'<hr/>', html, flags=re.MULTILINE)
    # Bullets
    html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)
    # Paragraphs (double newline)
    html = re.sub(r'\n\n', r'</p><p>', html)
    html = f"<p>{html}</p>"
    # Table rows (minimal)
    html = re.sub(r'^\|(.+)\|$', lambda m: '<tr>' + ''.join(
        f'<td>{cell.strip()}</td>' for cell in m.group(1).split('|')
    ) + '</tr>', html, flags=re.MULTILINE)

    return html


def build_html_email(report_md: str) -> str:
    report_html = markdown_to_html(report_md)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 13px; color: #1a1a1a; max-width: 900px; margin: auto; padding: 20px; }}
  h1 {{ color: #003366; border-bottom: 3px solid #003366; padding-bottom: 8px; }}
  h2 {{ color: #004080; border-bottom: 1px solid #cccccc; margin-top: 28px; }}
  h3 {{ color: #0055a5; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 12px; }}
  th {{ background-color: #003366; color: white; padding: 6px 8px; text-align: left; }}
  td {{ border: 1px solid #cccccc; padding: 5px 8px; vertical-align: top; }}
  tr:nth-child(even) {{ background-color: #f5f7fa; }}
  li {{ margin-bottom: 4px; }}
  a {{ color: #0055a5; }}
  hr {{ border: none; border-top: 2px solid #e0e0e0; margin: 20px 0; }}
  .bluf {{ background-color: #fff8dc; border-left: 4px solid #cc8800; padding: 10px 14px; margin: 10px 0; }}
  .header-bar {{ background-color: #003366; color: white; padding: 16px 20px; margin-bottom: 20px; }}
  .header-bar h1 {{ color: white; border-bottom: none; margin: 0; font-size: 18px; }}
  .header-bar p {{ margin: 4px 0 0 0; font-size: 12px; color: #ccddee; }}
  .footer {{ font-size: 11px; color: #666; border-top: 1px solid #ccc; margin-top: 30px; padding-top: 10px; }}
</style>
</head>
<body>
<div class="header-bar">
  <h1>DAILY UKRAINE–RUSSIA WAR ANALYST BRIEF</h1>
  <p>Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury Cross-Theater Impacts</p>
  <p>Date: {TODAY} | Prepared For: OUSW Comptroller Program/Budget Analysts | UNCLASSIFIED // FOUO</p>
</div>
{report_html}
<div class="footer">
  <p>Generated automatically by the OUSW P/B Daily Ukraine Brief system. Report date: {TODAY}.<br>
  All claims sourced. Unverified items labeled. Russian/Ukrainian government claims labeled as such.<br>
  Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY</p>
</div>
</body>
</html>"""


# ── Save Report to File ─────────────────────────────────────────────────────────

def save_report(report_md: str) -> str:
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    path = os.path.join(reports_dir, f"{FILE_NAME}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[{TODAY}] Report saved: {path}")
    return path


# ── Send Email via SMTP ─────────────────────────────────────────────────────────

def send_email(subject: str, body_html: str, body_text: str) -> None:
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print(f"[{TODAY}] WARNING: SENDER_EMAIL or SENDER_APP_PASSWORD not set. Skipping email.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL

    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(body_html,  "html",  "utf-8"))

    print(f"[{TODAY}] Sending email to {RECIPIENT_EMAIL}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print(f"[{TODAY}] Email sent successfully.")


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    report_md   = generate_report()
    save_report(report_md)
    html_body   = build_html_email(report_md)
    subject     = f"[OUSW P/B] {REPORT_TITLE}"

    send_email(subject, html_body, report_md)
    print(f"[{TODAY}] Daily brief complete.")


if __name__ == "__main__":
    main()
