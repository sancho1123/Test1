"""
Daily Ukraine-Russia War Analyst Brief Generator
Generates and emails an analyst-grade report for OUSW Comptroller P/B analysts.
Runs daily at 5:00 AM ET via GitHub Actions.
"""

import anthropic
import datetime
import json
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

RECIPIENT_EMAIL = "ericjsanchez23@gmail.com"
SENDER_EMAIL = os.environ.get("GMAIL_ADDRESS", "")
SENDER_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

TODAY = datetime.date.today().strftime("%Y-%m-%d")
REPORT_DATE_LONG = datetime.date.today().strftime("%B %d, %Y")

SYSTEM_PROMPT = """You are a senior defense analyst supporting the Department of War / OUSW Comptroller Program/Budget office. Your job is to produce daily analyst-grade reports on the Ukraine-Russia War.

Your audience is Department-level comptroller and program/budget analysts who must respond to Congressional RFIs, senior leader questions, budget and execution inquiries, defense article and stockpile questions, Ukraine aid questions, and cross-theater impact questions involving Operation Epic Fury / Iran.

Rules you MUST follow:
1. Every major claim must include the source name, article title, publication date, and direct web link.
2. Clearly label claims as: Confirmed | Likely | Claimed but unverified | Disputed | Cannot confirm.
3. Do not present unverified claims as fact.
4. Distinguish Russian/Ukrainian official claims from independently confirmed reporting.
5. Use direct, concise, executive-level language. No political commentary.
6. Tag every bullet with the appropriate category: [Military] [Funding] [Appropriations] [Defense Articles] [Stockpiles] [DIB] [Replenishment] [Readiness] [Congressional Interest] [Epic Fury / Iran Linkage] [Escalation Risk] [Sanctions] [Energy]
7. Every source must have a working web link. Do not include a source without a link.
8. The report must be structured per the required format below.
"""

REPORT_PROMPT = f"""Today is {REPORT_DATE_LONG}.

Generate the complete Daily Ukraine-Russia War Analyst Brief for OUSW Comptroller Program/Budget analysts.

Use your web search tool to research the following topics with searches dated within the last 24-48 hours where possible. Search for at least 8-10 different topics and synthesize your findings into the full report structure below.

Required research topics:
1. Ukraine-Russia battlefield update — last 24-48 hours (frontline, drone attacks, missile strikes)
2. U.S. defense articles and weapons transfers to Ukraine
3. U.S. funding, appropriations, and congressional activity on Ukraine aid
4. Operation Epic Fury / Iran — current status, ceasefire stability, munitions aftermath
5. U.S. air defense interceptor and munitions stockpile status (Patriot, THAAD, NASAMS, Tomahawk)
6. Russia, Iran, North Korea, China weapons and support networks
7. Defense industrial base and production capacity issues
8. Russia-Ukraine peace talks and diplomatic developments
9. Escalation risks — Russian nuclear signaling, NATO tensions
10. Energy, sanctions, and economic impacts (oil prices, Black Sea, EU sanctions)

Required Report Structure:

---
# DAILY UKRAINE-RUSSIA WAR ANALYST BRIEF
## {REPORT_DATE_LONG} | OUSW Comptroller Program/Budget

---

# PART I — SENIOR LEADER SNAPSHOT

## A. BOTTOM LINE UP FRONT
[5 bullets, each with source name, link, and confidence level]

## B. TOP ISSUES FOR OUSW COMPTROLLER P/B ANALYSTS
[7 bullets tagged with: Funding / Appropriations / Execution / PDA / USAI / Defense Articles / Stockpiles / Replenishment / Congressional RFI / Readiness / Epic Fury/Iran Linkage]

## C. WATCH ITEMS FOR THE NEXT 7 DAYS
[5 watch items with indicators, implications, and links]

## D. MOST LIKELY CONGRESSIONAL RFI QUESTIONS TODAY
[10 likely questions]

---

# PART II — ANALYST ANNEX

## 1. EXECUTIVE SUMMARY
[7-10 sourced bullets]

## 2. BATTLEFIELD AND MILITARY OPERATIONS
[Event/Location/Date/Source/Link/Confidence/Significance table]

## 3. DEFENSE ARTICLES, WEAPONS, STOCKPILES, AND MUNITIONS
[3A U.S. Defense Articles | 3B Allied Defense Articles | 3C Stockpile Issues | 3D Analysis]

## 4. DEFENSE INDUSTRIAL BASE AND PRODUCTION CAPACITY

## 5. FUNDING, BUDGET, APPROPRIATIONS, AND CONGRESSIONAL RELEVANCE
[Table: Funding item / Account / Amount / Source / Link / Confidence / Comptroller relevance / Potential RFI]

## 6. OPERATION EPIC FURY / IRAN AND UKRAINE-RUSSIA WAR LINKAGE
[6A Status | 6B Weapons Competition | 6C Drone/Missile Linkage | 6D Russia-Iran Relationship | 6E Energy Effects | 6F Strategic Bandwidth]

## 7. RUSSIA, IRAN, CHINA, NORTH KOREA, AND SANCTIONS-EVASION NETWORKS

## 8. ESCALATION RISKS AND WARNING INDICATORS
[Classified Low/Medium/High with sources]

## 9. CONGRESSIONAL RFI READINESS SECTION
[Table: Likely RFI Question / Short Answer / Source Links / Confidence]

## 10. DELTA FROM PRIOR REPORT
[What changed since yesterday]

## 11. ANALYST ASSESSMENT
[Confirmed Facts | Analyst Judgment | Cannot Confirm]

## 12. SOURCE LOG
[Full table: # / Source / Title / Date / Link / Topic / Confidence / Notes]

## 13. CONFIDENCE MATRIX
[Table: Claim / Confidence / Reason]

---
END REPORT
---

Search broadly and synthesize comprehensively. Every claim must have a source link. Label unverified claims clearly. Write for Department-level analysts, not the general public.
"""


def search_and_generate_report():
    """Use Claude with web search to generate the daily brief."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print(f"[{datetime.datetime.now()}] Starting report generation for {TODAY}...")

    tools = [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 15,
        }
    ]

    messages = [{"role": "user", "content": REPORT_PROMPT}]

    report_text = ""
    iteration = 0
    max_iterations = 20

    while iteration < max_iterations:
        iteration += 1
        print(f"[{datetime.datetime.now()}] API call iteration {iteration}...")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        print(f"[{datetime.datetime.now()}] Stop reason: {response.stop_reason}")

        # Collect any text content from this response
        for block in response.content:
            if hasattr(block, "text"):
                report_text += block.text

        # If model is done, break
        if response.stop_reason == "end_turn":
            break

        # If model wants to use tools, continue the agentic loop
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"[{datetime.datetime.now()}] Tool call: {block.name} — {json.dumps(block.input)[:120]}")
                    # Tool results are automatically handled by the API in web_search mode
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": "Search completed.",
                        }
                    )

            messages.append({"role": "user", "content": tool_results})
        else:
            break

    print(f"[{datetime.datetime.now()}] Report generation complete. Length: {len(report_text)} chars")
    return report_text


def save_report(report_text):
    """Save the report to the reports directory."""
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    filename = f"{TODAY}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md"
    filepath = os.path.join(reports_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"[{datetime.datetime.now()}] Report saved to: {filepath}")
    return filepath, filename


def send_email(report_text, filename):
    """Send the report via Gmail SMTP."""
    if not SENDER_EMAIL or not SENDER_APP_PASSWORD:
        print("WARNING: Gmail credentials not configured. Skipping email send.")
        print("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables / GitHub Secrets.")
        return False

    print(f"[{datetime.datetime.now()}] Sending email to {RECIPIENT_EMAIL}...")

    subject = f"Daily Ukraine-Russia War Analyst Brief — {REPORT_DATE_LONG} | OUSW P/B"

    # Build HTML version with basic formatting
    html_body = f"""
<html>
<head>
<style>
  body {{ font-family: Courier New, monospace; font-size: 13px; color: #1a1a1a; max-width: 900px; margin: 0 auto; padding: 20px; }}
  h1 {{ color: #002060; border-bottom: 3px solid #002060; padding-bottom: 10px; }}
  h2 {{ color: #1F3864; border-bottom: 1px solid #1F3864; }}
  h3 {{ color: #2F5496; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 12px; }}
  th {{ background-color: #002060; color: white; padding: 6px 8px; text-align: left; }}
  td {{ border: 1px solid #ccc; padding: 5px 8px; vertical-align: top; }}
  tr:nth-child(even) {{ background-color: #f2f2f2; }}
  blockquote {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
  code {{ background: #f0f0f0; padding: 2px 4px; border-radius: 2px; }}
  .header-box {{ background: #002060; color: white; padding: 15px; margin-bottom: 20px; }}
  .footer {{ font-size: 11px; color: #666; border-top: 1px solid #ccc; padding-top: 10px; margin-top: 20px; }}
</style>
</head>
<body>
<div class="header-box">
  <strong>DAILY UKRAINE-RUSSIA WAR ANALYST BRIEF</strong><br/>
  Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury<br/>
  {REPORT_DATE_LONG} | OUSW Comptroller Program/Budget | UNCLASSIFIED
</div>
<pre style="white-space: pre-wrap; font-family: Courier New, monospace; font-size: 12px; line-height: 1.5;">
{report_text}
</pre>
<div class="footer">
  Generated automatically at 0500 ET | Prepared for OUSW Comptroller P/B Analysts<br/>
  File: {filename}<br/>
  This report is for analytical purposes only and does not represent official U.S. government assessments.
</div>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    plain_part = MIMEText(report_text, "plain", "utf-8")
    html_part = MIMEText(html_body, "html", "utf-8")
    msg.attach(plain_part)
    msg.attach(html_part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print(f"[{datetime.datetime.now()}] Email sent successfully to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        print(f"ERROR sending email: {e}")
        return False


def main():
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    report_text = search_and_generate_report()

    if not report_text.strip():
        print("ERROR: Report generation produced empty output.")
        sys.exit(1)

    filepath, filename = save_report(report_text)
    email_sent = send_email(report_text, filename)

    print(f"\n{'='*60}")
    print(f"DAILY BRIEF COMPLETE — {TODAY}")
    print(f"Report saved: {filepath}")
    print(f"Email sent:   {'YES' if email_sent else 'NO (credentials not configured)'}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
