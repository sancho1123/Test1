"""
Daily Ukraine-Russia War Analyst Brief Generator
Runs via GitHub Actions at 05:00 AM ET daily.
Requires: ANTHROPIC_API_KEY, GMAIL_CREDENTIALS_JSON, GMAIL_TOKEN_JSON secrets.
"""

import anthropic
import json
import os
import base64
import datetime
import pathlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "ericjsanchez23@gmail.com")
TODAY = datetime.date.today().isoformat()
FILE_PREFIX = f"{TODAY}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB"

SYSTEM_PROMPT = """You are a senior defense analyst producing a daily intelligence brief for OUSW Comptroller Program-Budget analysts.
Your output must be a complete, analyst-grade HTML report following the exact structure specified in the user prompt.
Every major claim must be sourced with a direct web link. Label unverified claims as 'Cannot confirm.'
Russian and Ukrainian official statements are labeled as claims unless independently confirmed by credible outlets.
Write in direct, executive language — no political commentary, no speculation without evidence."""

BRIEF_PROMPT = f"""Today is {TODAY}. Generate the complete Daily Ukraine–Russia War Analyst Brief per the full specification below.

REPORT REQUIREMENTS:
- Reporting window: last 24-48 hours (use web search to find current news)
- Use ONLY credible, sourced reporting (ISW, CSIS, Reuters, AP, BBC, FT, WSJ, NYT, WaPo, DoW/DoD, White House, State Dept, Congress.gov, Atlantic Council, RUSI, War on the Rocks, Defense News, Breaking Defense, USNI, Kyiv Independent, Ukrinform, NATO)
- Every claim must include: source name, article title, publication date, and direct web link
- Label confidence: High / Medium / Low / Cannot confirm
- Clearly distinguish: Confirmed / Likely / Claimed but unverified / Disputed / Cannot confirm

REPORT STRUCTURE — produce all sections:

PART I — SENIOR LEADER SNAPSHOT (fits ~1 page):
A. Bottom Line Up Front (BLUF) — 3-5 bullets with source + confidence each
B. Top Issues for OUSW Comptroller P/B Analysts — 5-7 tagged bullets ([Funding], [Appropriations], [Execution], [PDA], [USAI], [Defense Articles], [Stockpiles], [Replenishment], [Congressional RFI], [Readiness], [Epic Fury/Iran Linkage])
C. Watch Items for Next 7 Days — 5 items with indicators and implications
D. Most Likely Congressional RFI Questions Today — 5-10 questions

PART II — ANALYST ANNEX:
1. Executive Summary — 7-10 sourced bullets with topic tags
2. Battlefield and Military Operations — table format (Event/Location/Date/Source/Link/Confidence/Significance)
3. Defense Articles, Weapons, Stockpiles, and Munitions — sections A (US-provided), B (Allied), C (Stockpile/Readiness), D (Analysis per system)
4. Defense Industrial Base and Production Capacity — table format
5. Funding, Budget, Appropriations, and Congressional Relevance — table format (Funding item/Account/Amount/Source/Link/Confidence/Comptroller relevance/Potential RFI). If nothing new: state "No new confirmed funding development identified."
6. Operation Epic Fury / Iran and Ukraine-Russia War Linkage — sections A (weapons competition), B (drone/missile), C (Russia-Iran relationship), D (energy/economic), E (strategic bandwidth). If no confirmed linkage: state "I cannot confirm a direct linkage."
7. Russia/Iran/China/North Korea/Belarus/Sanctions-Evasion Networks — table format
8. Escalation Risks and Warning Indicators — classify each Low/Medium/High
9. Congressional RFI Readiness — table (Question/Short Answer/Source Links/Confidence)
10. Delta From Prior Report — compare to yesterday; if no prior: state baseline
11. Analyst Assessment — labeled Confirmed Facts / Analyst Judgment / Cannot Confirm
12. Source Log — full table (# / Source / Title / Date / Link / Topic / Confidence / Notes) — EVERY source must have a direct web link
13. Confidence Matrix — table (Claim / Confidence / Reason)

OUTPUT FORMAT: Complete HTML document with inline CSS styling suitable for email. Professional, readable, color-coded by confidence/urgency. Include the report title, date, and "Estimated Read: ~10 minutes" in the header.

FINAL CHECK before outputting:
- Every major claim has a source with a direct web link?
- Unverified claims clearly labeled?
- Russian/Ukrainian official claims labeled as such?
- All 13 Analyst Annex sections present?
- Defense articles/stockpile section present?
- Epic Fury section present?
- Congressional RFI section present?
- Source log present with links?
"""


def generate_brief_html() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": BRIEF_PROMPT}],
    )
    return message.content[0].text


def send_via_gmail(html_body: str, subject: str, recipient: str) -> None:
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        import subprocess
        subprocess.run(["pip", "install", "google-auth", "google-api-python-client"], check=True)
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

    creds_json = os.environ.get("GMAIL_CREDENTIALS_JSON")
    token_json = os.environ.get("GMAIL_TOKEN_JSON")

    if not token_json:
        print("WARNING: GMAIL_TOKEN_JSON secret not set. Cannot send email.")
        print("Save the brief HTML to artifact instead.")
        return

    token_data = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(token_data)

    service = build("gmail", "v1", credentials=creds)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["To"] = recipient
    msg["From"] = "me"
    msg.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Email sent to {recipient}")


def main():
    print(f"[{TODAY}] Generating Daily Ukraine-Russia War Analyst Brief...")

    html = generate_brief_html()

    output_dir = pathlib.Path("brief_output")
    output_dir.mkdir(exist_ok=True)

    html_path = output_dir / f"{FILE_PREFIX}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"Brief saved to {html_path}")

    subject = (
        f"{TODAY} | Daily Ukraine–Russia War Analyst Brief | "
        "Defense Articles, Stockpiles, Budget, Congressional RFI & Operation Epic Fury Cross-Theater Impacts"
    )

    try:
        send_via_gmail(html, subject, RECIPIENT_EMAIL)
    except Exception as e:
        print(f"Email send failed: {e}")
        print("Brief saved as artifact — check GitHub Actions artifacts.")


if __name__ == "__main__":
    main()
