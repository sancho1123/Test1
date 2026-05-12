#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief Generator
OUSW Comptroller Program/Budget Office

Runs via cron or GitHub Actions at 05:00 ET daily.
Generates an analyst-grade report and emails it to configured recipients.

Requirements:
  pip install anthropic requests python-dotenv

Environment variables (set in .env or GitHub Actions secrets):
  ANTHROPIC_API_KEY   - Anthropic API key
  SMTP_HOST           - SMTP server host (default: smtp.gmail.com)
  SMTP_PORT           - SMTP port (default: 587)
  SMTP_USER           - Gmail / SMTP username
  SMTP_PASSWORD       - Gmail App Password (not your Google password)
  REPORT_RECIPIENTS   - Comma-separated list of recipient email addresses
"""

import os
import sys
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env loading is optional; fall back to environment


REPORT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
REPORT_DATE_LONG = datetime.datetime.now().strftime("%B %d, %Y")

ANALYST_BRIEF_PROMPT = f"""
Today's date is {REPORT_DATE_LONG}.

You are a senior defense analyst supporting the Department of War / OUSW Comptroller
Program/Budget office. Generate a comprehensive, analyst-grade Daily Ukraine-Russia War
Brief. This is for analysts who support Congressional RFIs, senior leader questions,
budget execution inquiries, defense article and stockpile questions, Ukraine aid
questions, and cross-theater impact questions involving Operation Epic Fury / Iran.

REPORT TITLE: Daily Ukraine-Russia War Analyst Brief
FILE NAME: {REPORT_DATE}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB

REQUIRED SECTIONS (in order):

PART I — SENIOR LEADER SNAPSHOT
A. Bottom Line Up Front (3-5 bullets, each with source name, direct URL, confidence level)
B. Top Issues for OUSW Comptroller P/B Analysts (5-7 bullets, each tagged with:
   [Funding] [Appropriations] [Execution] [PDA] [USAI] [Defense Articles] [Stockpiles]
   [Replenishment] [Congressional RFI] [Readiness] [Epic Fury/Iran Linkage])
C. Watch Items for the Next 7 Days (5 items with indicator, why it matters, implication)
D. Most Likely Congressional RFI Questions Today (5-10 questions)

PART II — ANALYST ANNEX
1. Executive Summary (7-10 bullets with topic tags, source, URL, confidence)
2. Battlefield and Military Operations (frontline, strikes, drones, ceasefire status)
3. Defense Articles, Weapons, Stockpiles, and Munitions (Patriot, NASAMS, HIMARS,
   155mm, ATACMS, Javelin, Stinger, F-16, drones, counter-UAS — all with sources)
4. Defense Industrial Base and Production Capacity
5. Funding, Budget, Appropriations, Congressional Relevance (PDA, USAI, FMF,
   supplementals, reprogramming, European contributions)
6. Operation Epic Fury / Iran and Ukraine-Russia War Linkage (mandatory; if no
   confirmed linkage found, state "I cannot confirm a direct linkage")
7. Russia, Iran, China, North Korea, Belarus, and Sanctions-Evasion Networks
8. Escalation Risks and Warning Indicators (classified Low/Medium/High)
9. Congressional RFI Readiness Section (table format: Question | Answer | Sources | Confidence)
10. Delta From Prior Report (or state "No prior report available")
11. Analyst Assessment (confirmed facts, analyst judgment, cannot confirm — labeled)
12. Required News Article / Source Log (every source with: #, Source, Title, Date, URL,
    Topic, Confidence, Notes)
13. Confidence Matrix

STRICT RULES:
- Every major claim must include a direct web link to the source
- Clearly label: Confirmed / Likely / Claimed but unverified / Disputed / Cannot confirm
- Do not present unverified claims as fact
- Label Russian and Ukrainian official claims as such
- No political commentary; sober, evidence-based language only
- Prioritize: ISW, CSIS, RAND, Atlantic Council, Reuters, AP, BBC, DoD/DoW official releases,
  White House, State Dept, Congress.gov, CRS, GAO, CENTCOM, EUCOM

OUTPUT FORMAT: HTML formatted for email (use inline CSS, tables, colored headers).
The report should be approximately a 10-minute read. Use clear executive-level language.
"""


def generate_brief(client: "anthropic.Anthropic") -> str:
    """Generate the analyst brief using the Anthropic API with web search tool."""
    print(f"[{REPORT_DATE}] Generating analyst brief via Anthropic API...")

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 25,
            }
        ],
        messages=[
            {
                "role": "user",
                "content": ANALYST_BRIEF_PROMPT,
            }
        ],
    )

    # Extract text content from the response
    report_html = ""
    for block in response.content:
        if block.type == "text":
            report_html += block.text

    if not report_html.strip():
        raise RuntimeError("Empty report generated — check API response")

    print(f"[{REPORT_DATE}] Brief generated successfully ({len(report_html)} chars).")
    return report_html


def send_email(report_html: str, recipients: list[str]) -> None:
    """Send the analyst brief via SMTP."""
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")

    if not smtp_user or not smtp_password:
        raise RuntimeError(
            "SMTP_USER and SMTP_PASSWORD environment variables are required"
        )

    subject = (
        f"{REPORT_DATE} | Daily Ukraine–Russia War Analyst Brief | "
        f"Defense Articles, Stockpiles, Budget, Congressional RFI & Operation Epic Fury"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = ", ".join(recipients)

    # Plain-text fallback
    plain_text = (
        f"Daily Ukraine–Russia War Analyst Brief — {REPORT_DATE_LONG}\n\n"
        f"Please view this message in an HTML-capable email client.\n\n"
        f"Prepared for: OUSW Comptroller Program/Budget Analysts\n"
        f"Classification: UNCLASSIFIED // OPEN SOURCE COMPILATION"
    )
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(report_html, "html"))

    print(f"[{REPORT_DATE}] Sending to: {', '.join(recipients)}")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipients, msg.as_string())

    print(f"[{REPORT_DATE}] Email sent successfully.")


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is required.")
        sys.exit(1)

    recipients_raw = os.environ.get("REPORT_RECIPIENTS", "ericjsanchez23@gmail.com")
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

    client = anthropic.Anthropic(api_key=api_key)

    try:
        report_html = generate_brief(client)
        send_email(report_html, recipients)
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
