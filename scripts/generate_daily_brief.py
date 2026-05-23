"""
Daily Ukraine-Russia War Analyst Brief Generator
For OUSW Comptroller Program/Budget Analysts

Requires:
  - ANTHROPIC_API_KEY environment variable
  - GMAIL_RECIPIENT environment variable
  - GMAIL_SENDER_TOKEN environment variable (Google OAuth2 token for sending email)

Usage:
  python scripts/generate_daily_brief.py
"""

import os
import sys
import json
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic

TODAY = datetime.date.today().strftime("%Y-%m-%d")
REPORT_FILENAME = f"{TODAY}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB"
REPORT_PATH = f"reports/{REPORT_FILENAME}.md"
RECIPIENT = os.environ.get("GMAIL_RECIPIENT", "ericjsanchez23@gmail.com")

SYSTEM_PROMPT = """You are a senior defense intelligence analyst preparing a daily Ukraine-Russia War
Analyst Brief for the Department of War / OUSW Comptroller Program/Budget office.

Your job is to produce a thorough, sourced, analyst-grade daily brief that is:
- Useful for responding to congressional RFIs
- Focused on defense articles, stockpiles, budget execution, and readiness
- Attentive to Operation Epic Fury / Iran cross-theater impacts
- Accurate: every major claim must have a source with a working URL
- Clear about what is confirmed, likely, or cannot be confirmed

Write in a direct, executive analyst style. No political commentary. No unsupported claims."""

BRIEF_PROMPT = f"""Today is {TODAY}.

Generate the full Daily Ukraine-Russia War Analyst Brief for OUSW Comptroller Program/Budget analysts.

The report covers developments from the last 24-48 hours. Use your most current knowledge.

Required sections:

PART I — SENIOR LEADER SNAPSHOT
A. Bottom Line Up Front (3-5 bullets with source, link, confidence)
B. Top Issues for OUSW Comptroller P/B Analysts (5-7 tagged bullets: [Funding], [Appropriations], [Execution], [PDA], [USAI], [Defense Articles], [Stockpiles], [Replenishment], [Congressional RFI], [Readiness], [Epic Fury / Iran Linkage])
C. Watch Items for the Next 7 Days (5 items)
D. Most Likely Congressional RFI Questions Today (5-10 questions)

PART II — ANALYST ANNEX
1. Executive Summary (7-10 sourced bullets with tags)
2. Battlefield and Military Operations (tabular format for each major event)
3. Defense Articles, Weapons, Stockpiles, and Munitions
   A. U.S.-Provided Defense Articles
   B. Allied / Partner Defense Articles
   C. Stockpile and Readiness Issues
   D. Defense Article Analysis table
4. Defense Industrial Base and Production Capacity
5. Funding, Budget, Appropriations, and Congressional Relevance (tabular format)
6. Operation Epic Fury / Iran and Ukraine-Russia War Linkage (mandatory section)
   A. Weapons and Stockpile Competition
   B. Drone and Missile Warfare Linkage
   C. Russia-Iran Relationship
   D. Energy and Economic Effects
   E. Strategic Bandwidth and Force Allocation
7. Russia, Iran, China, North Korea, Belarus, and Sanctions-Evasion Networks
8. Escalation Risks and Warning Indicators (table with risk levels)
9. Congressional RFI Readiness Section (table format)
10. Delta From Prior Report
11. Analyst Assessment (Confirmed Facts / Analyst Judgment / Cannot Confirm)
12. Required News Article / Source Log (every source with date and working URL)
13. Confidence Matrix (table)

Rules:
- Every major claim must have a source with a direct web link
- Clearly label unverified claims
- Clearly label Russian/Ukrainian official claims
- If something cannot be confirmed, say "I cannot confirm this"
- Confidence levels: High / Medium / Low / Cannot Confirm
- Use tables where specified
- No political commentary
- No speculation without evidence
- The product should read like a daily senior analyst brief

Output the complete report in Markdown format, ready to save and send."""


def generate_brief() -> str:
    """Call the Anthropic API to generate the daily brief."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"Generating brief for {TODAY}...")
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": BRIEF_PROMPT}],
    )

    return message.content[0].text


def save_report(content: str) -> None:
    """Save the report to the reports directory."""
    os.makedirs("reports", exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        header = f"""# DAILY UKRAINE–RUSSIA WAR ANALYST BRIEF
## Defense Articles, Stockpiles, Budget, Congressional RFI, and Operation Epic Fury Cross-Theater Impacts

**Date:** {TODAY}
**Prepared for:** OUSW Comptroller Program/Budget Analysts
**File:** {REPORT_FILENAME}
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY (FOUO)

---

"""
        f.write(header + content)
    print(f"Report saved to {REPORT_PATH}")


def markdown_to_html(md_content: str) -> str:
    """Convert basic Markdown to HTML for email."""
    import re

    html = md_content
    # Headers
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    # Bold
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    # Links
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
    # Horizontal rules
    html = re.sub(r"^---$", r"<hr>", html, flags=re.MULTILINE)
    # Line breaks
    html = html.replace("\n", "<br>\n")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 13px; line-height: 1.5; max-width: 900px; margin: 0 auto; padding: 20px; color: #222; }}
  h1 {{ background: #1a3a6b; color: white; padding: 12px 16px; font-size: 18px; }}
  h2 {{ background: #2e5fa3; color: white; padding: 8px 12px; font-size: 14px; margin-top: 24px; }}
  h3 {{ color: #1a3a6b; border-bottom: 2px solid #1a3a6b; padding-bottom: 4px; font-size: 13px; }}
  h4 {{ color: #2e5fa3; font-size: 12px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 12px; }}
  th {{ background: #1a3a6b; color: white; padding: 6px 8px; text-align: left; }}
  td {{ border: 1px solid #ccc; padding: 5px 8px; vertical-align: top; }}
  tr:nth-child(even) {{ background: #f5f7fa; }}
  a {{ color: #2e5fa3; }}
  hr {{ border: 1px solid #2e5fa3; margin: 20px 0; }}
  .footer {{ font-size: 11px; color: #666; margin-top: 30px; border-top: 1px solid #ccc; padding-top: 10px; }}
</style>
</head>
<body>
{html}
<div class="footer">
  Daily Ukraine-Russia War Analyst Brief | OUSW Comptroller Program/Budget | {TODAY} | UNCLASSIFIED//FOUO
</div>
</body>
</html>"""


def send_email(subject: str, html_body: str, plain_body: str) -> None:
    """Send the report via Gmail SMTP using app password or OAuth token."""
    token = os.environ.get("GMAIL_SENDER_TOKEN", "")
    sender = "ericjsanchez23@gmail.com"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = RECIPIENT

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # Using Gmail SMTP with app password
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, token)
        server.sendmail(sender, RECIPIENT, msg.as_string())

    print(f"Email sent to {RECIPIENT}")


def main():
    # Generate the brief
    brief_content = generate_brief()

    # Save to file
    save_report(brief_content)

    # Prepare email
    subject = f"Daily Ukraine-Russia War Analyst Brief | OUSW P/B | {TODAY}"
    html_body = markdown_to_html(brief_content)

    # Send email
    try:
        send_email(subject, html_body, brief_content)
    except Exception as e:
        print(f"Warning: Email sending failed: {e}", file=sys.stderr)
        print("Report was still saved locally.", file=sys.stderr)


if __name__ == "__main__":
    main()
