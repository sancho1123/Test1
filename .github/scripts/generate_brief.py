"""
Daily Ukraine–Russia War Analyst Brief Generator
OUSW Comptroller Program/Budget Office
Runs via GitHub Actions at 05:00 AM ET daily.
"""

import os
import json
import base64
import datetime
import pathlib
import textwrap
import anthropic
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RECIPIENT = os.environ["RECIPIENT_EMAIL"]
REPORT_DATE = os.environ.get("REPORT_DATE", datetime.date.today().isoformat())
OUTPUT_DIR = pathlib.Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = textwrap.dedent("""
You are a senior intelligence analyst supporting the Department of War /
OUSW Comptroller Program/Budget office. You produce daily analyst-grade
briefings on the Ukraine–Russia War for audiences who must respond quickly
to congressional RFIs and senior leader questions.

Your briefings are factual, sourced, and clearly labeled with confidence
levels (High / Medium / Low / Cannot confirm). You never present unverified
claims as fact. You distinguish between confirmed reporting, official claims,
and analytical judgment. You do not editorialize or use sensational language.

Every major claim must include a direct web link. If you cannot confirm
something, say "I cannot confirm this."
""").strip()

RESEARCH_PROMPT = textwrap.dedent(f"""
Today is {REPORT_DATE}. Produce the full Daily Ukraine–Russia War Analyst
Brief for OUSW Comptroller Program/Budget analysts. The reporting window
is the last 24–48 hours.

Search for the most current reporting on:
1. Ukraine–Russia battlefield developments (frontlines, strikes, drones, missiles)
2. Defense articles, weapons transfers, stockpile levels (Patriot, 155mm,
   HIMARS, NASAMS, counter-UAS, etc.)
3. U.S. funding, USAI, PDA, appropriations, congressional oversight
4. Operation Epic Fury / Iran — cross-theater stockpile and strategic impacts
5. Russia's supply chains (Iran, North Korea, China, Belarus)
6. Escalation risks and nuclear signaling
7. Peace talks / ceasefire status

Structure the report in two parts:
PART I — Senior Leader Snapshot (BLUF, Top Issues, 7-Day Watch Items,
          Likely Congressional RFI Questions)
PART II — Analyst Annex (Executive Summary, Battlefield, Defense Articles,
           DIB, Funding, Epic Fury Linkage, CRINK, Escalation Risks,
           Congressional RFI Readiness, Delta from Prior Report,
           Analyst Assessment, Source Log, Confidence Matrix)

Output the full report as clean HTML suitable for an email body.
Include every source with a direct hyperlink.
""").strip()

# ---------------------------------------------------------------------------
# Generate report via Claude with web search (tool use)
# ---------------------------------------------------------------------------

def generate_report() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    tools = [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 20,
        }
    ]

    response = client.messages.create(
        model="claude-opus-4-7-20251101",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=[{"role": "user", "content": RESEARCH_PROMPT}],
    )

    # Extract text content from the response
    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text

    return html_content


# ---------------------------------------------------------------------------
# Send via Gmail API
# ---------------------------------------------------------------------------

def get_gmail_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GMAIL_CLIENT_ID"],
        client_secret=os.environ["GMAIL_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/gmail.send"],
    )
    return build("gmail", "v1", credentials=creds)


def send_email(subject: str, html_body: str) -> dict:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["To"] = RECIPIENT
    msg.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service = get_gmail_service()
    result = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"[{REPORT_DATE}] Generating analyst brief...")
    html_report = generate_report()

    # Save to file
    report_path = OUTPUT_DIR / f"{REPORT_DATE}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.html"
    report_path.write_text(html_report, encoding="utf-8")
    print(f"Report saved to {report_path}")

    # Send email
    subject = (
        f"{REPORT_DATE} | Daily Ukraine–Russia War Analyst Brief | "
        "Defense Articles, Stockpiles, Budget, Congressional RFI & "
        "Operation Epic Fury Cross-Theater Impacts"
    )

    try:
        result = send_email(subject, html_report)
        print(f"Email sent. Message ID: {result.get('id')}")
    except Exception as exc:
        print(f"Email send failed: {exc}")
        print("Report is saved as an artifact — retrieve from GitHub Actions.")
        raise


if __name__ == "__main__":
    main()
