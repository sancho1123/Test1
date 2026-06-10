#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief
OUSW Comptroller Program/Budget Analyst Support
Runs at 5:00 AM ET via GitHub Actions cron.
"""

import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

import anthropic

RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "ericjsanchez23@gmail.com")
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
SENDER_EMAIL = "ericjsanchez23@gmail.com"

REPORT_PROMPT = """You are a senior intelligence analyst supporting the Office of the Under Secretary of Defense (Comptroller) / OUSW Program and Budget staff. Today is {today}.

Generate a **Ukraine-Russia War Daily Analyst Brief** — a structured, analyst-grade report that a DoD program/budget analyst can read in approximately 10 minutes. Every factual claim MUST include an inline source citation with a direct URL in the format [Source: Publication Name](URL). Do not fabricate URLs; omit the hyperlink if you cannot confirm the exact URL, but still cite the publication and date.

Use this confidence vocabulary consistently:
- **[CONFIRMED]** — verified by multiple independent, credible sources
- **[LIKELY]** — single credible source or strong inferential basis
- **[CLAIMED/UNVERIFIED]** — reported by one party only, not independently corroborated
- **[DISPUTED]** — conflicting reports exist; explain the dispute briefly
- **[CANNOT CONFIRM]** — insufficient open-source evidence

Search extensively for today's most current information before writing. Prioritize: Institute for the Study of War (ISW), DoD press releases, Congressional Research Service, Reuters, AP, BBC, The Economist, Foreign Policy, Defense News, Breaking Defense, Kyiv Independent, Ukrainska Pravda, and official Ukrainian/NATO government statements.

---

# UKRAINE-RUSSIA WAR DAILY ANALYST BRIEF
## OUSW Comptroller / Program & Budget Analyst Support
### {today} | CLASSIFICATION: UNCLASSIFIED // FOR OFFICIAL USE (FOUO SIMULATION)

---

## PART I — SENIOR LEADER SNAPSHOT (2-minute read)

### 1.1 | Three Most Significant Developments (24 Hours)
List exactly three bullet points. Each must: name the development, state confidence level, and include one source citation.

### 1.2 | Budget/Appropriations Flash
Identify the single most important budget or appropriations event relevant to Ukraine security assistance in the last 24–72 hours. If none, state "No significant budget actions in the reporting period." Include confidence level and source.

### 1.3 | Escalation Risk Indicator
Rate overall escalation risk on a 5-point scale: **LOW / GUARDED / ELEVATED / HIGH / CRITICAL**. Provide a 2-sentence rationale with sources.

---

## PART II — ANALYST ANNEX (8-minute read)

### 2.1 | Battlefield Situation (Ground)
Provide a concise operational summary covering:
- Eastern Front (Donetsk, Luhansk oblasts): key line-of-contact changes, confirmed advances/withdrawals
- Southern Front (Zaporizhzhia, Kherson): status
- Northern/Kharkiv sector: any activity
- Overall operational tempo assessment

For each front, include confidence level and at least one source.

### 2.2 | Battlefield Situation (Air/Missile/Drone)
- Russian strike packages in the last 24 hours: targets, weapons used, Ukrainian air defense performance [CONFIRMED/CLAIMED/etc.]
- Ukrainian long-range strike activity (drones, ATACMS, Storm Shadow) if any [confidence level]
- Air defense inventory implications (include any public data on intercept rates, launcher status)

### 2.3 | Defense Articles & Stockpile Tracking
Report on:
- U.S. Presidential Drawdown Authority (PDA) packages: any new announcements, package numbers, dollar values
- Specific weapon systems: delivery status, reported battlefield employment, attrition
- Allied contributions (EU, UK, Germany, Poland, etc.) — new pledges or deliveries
- Ukrainian reported shortfalls or urgent requests
- Any public reporting on U.S. stockpile depletion concerns (e.g., 155mm, Patriot interceptors, HIMARS rockets)

Use confidence levels for each claim.

### 2.4 | Budget & Appropriations
- Supplemental appropriations: current status of any pending Ukraine security assistance legislation
- Ukraine Security Assistance Initiative (USAI): obligation rates, announced allocations
- Defense Production Act invocations relevant to Ukraine
- FMF (Foreign Military Financing) flows
- Any DoD reprogramming actions or continuing resolution impacts
- Congressional Budget Office or OMB estimates, if recently published

### 2.5 | Congressional Activity & RFI Preparation
- Relevant hearings (Armed Services, Appropriations, Foreign Relations/Affairs): scheduled or recent — summarize key testimony or questions
- Legislation introduced or advanced: bills, amendments, riders
- Key member statements (pro/anti Ukraine assistance) that may affect budget authorization or appropriations
- Anticipated RFI topics based on current Congressional focus areas (flag for analyst action)

### 2.6 | Operation Epic Fury & Iran Cross-Theater Impacts
- Status of U.S./allied operations in the Red Sea / Middle East theater
- Iranian weapons flows to Russia: drones (Shahed variants), ballistic missiles, technical support — latest confirmed/reported transfers
- Resource competition: any public reporting on U.S. munitions allocation tensions between CENTCOM and EUCOM requirements
- Iranian sanctions/designations actions (Treasury, State) relevant to Russia materiel supply chain

### 2.7 | Russia's External Partners
**Iran:** Shahed drone production, delivery cadence, new variants, crew/technical advisors in Russia
**North Korea:** Troop deployments (status, casualties if reported), ammunition transfers (artillery shells, ballistic missiles), Kim Jong-un statements, U.S./ROK/Ukrainian assessments
**China:** Dual-use goods transfers, satellite imagery support, diplomatic posture, sanctions exposure for Chinese firms
**Belarus:** Force posture, Lukashenko statements, Russian basing activity, any cross-border threat indicators toward Ukraine

### 2.8 | Russian Domestic Situation
- Mobilization: any new decrees, regional draft data, casualty figures (Ukrainian/Western estimates vs. Russian claims)
- Defense-industrial output: production rates for key systems (tanks, artillery, drones, missiles) if recently reported
- Economic pressure indicators: ruble, oil revenues, sanctions evasion developments
- Political developments relevant to war trajectory (Putin statements, Kremlin signaling)

### 2.9 | Ukrainian Government & Military
- Zelensky/Ukrainian MoD significant statements or actions
- Ukrainian mobilization legislation updates
- Corruption/governance issues relevant to U.S. assistance accountability
- Diplomatic activity: EU accession, bilateral security agreements, NATO status

### 2.10 | NATO & Allied Coordination
- NATO ministerial or working group outcomes relevant to Ukraine
- Bilateral security agreements: signed, negotiated, or publicly discussed
- Allied capability commitments: F-16 delivery status, training pipelines, Patriot/air defense
- Article 5 risk indicators; any Russian actions against NATO territory or assets

### 2.11 | Information Environment & Disinformation
- Active Russian information operations targeting U.S./allied domestic audiences
- Notable disinformation narratives gaining traction (flag those that may appear in Congressional hearings or press)
- Ukrainian information operations, if publicly reported

### 2.12 | Key Intelligence Gaps
List 3–5 specific questions that open-source analysis cannot answer and that are relevant to OUSW budget/program decisions. Format as: "**Gap [N]:** [Question] — *Why it matters for PB analysts:* [explanation]"

### 2.13 | Source Register
Provide a numbered list of all sources cited in this report. Format:
[N] Publication/Organization. "Article Title or Description." Date. URL (if confirmed).

---

*End of Report. Generated {today} by automated OUSW PB Analyst Support System.*
*All content is derived from open-source reporting. Confidence levels reflect OSINT assessment methodology.*
"""

HTML_WRAPPER = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Georgia, serif; max-width: 900px; margin: 0 auto; padding: 20px; color: #1a1a1a; background: #fafafa; }}
  h1 {{ color: #1a3a5c; border-bottom: 3px solid #b22222; padding-bottom: 8px; font-size: 1.4em; }}
  h2 {{ color: #1a3a5c; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 28px; font-size: 1.15em; }}
  h3 {{ color: #2c5282; margin-top: 20px; font-size: 1.0em; }}
  p {{ line-height: 1.7; margin: 8px 0; }}
  li {{ line-height: 1.7; margin: 4px 0; }}
  strong {{ color: #1a1a1a; }}
  a {{ color: #1a56a0; }}
  .header-block {{ background: #1a3a5c; color: white; padding: 14px 20px; border-radius: 4px; margin-bottom: 24px; }}
  .header-block h1 {{ color: white; border-bottom: 1px solid rgba(255,255,255,0.3); }}
  .header-block p {{ color: #cce0ff; margin: 4px 0; font-size: 0.9em; }}
  .classification {{ background: #b22222; color: white; text-align: center; padding: 6px; font-weight: bold; font-size: 0.85em; border-radius: 3px; margin-bottom: 16px; }}
  pre {{ white-space: pre-wrap; font-family: Georgia, serif; }}
  blockquote {{ border-left: 4px solid #1a3a5c; padding-left: 16px; color: #444; margin: 12px 0; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 20px 0; }}
  code {{ background: #f0f0f0; padding: 1px 4px; border-radius: 2px; font-size: 0.9em; }}
</style>
</head>
<body>
<div class="classification">UNCLASSIFIED // FOR OFFICIAL USE ONLY (SIMULATION) — OPEN SOURCE INTELLIGENCE</div>
<div class="header-block">
  <h1>Ukraine-Russia War Daily Analyst Brief</h1>
  <p>OUSW Comptroller / Program &amp; Budget Analyst Support</p>
  <p>Report Date: {today} | Generated: {generated_at} UTC</p>
</div>
{body}
<hr>
<p style="font-size:0.8em; color:#888;">This report was generated automatically using open-source intelligence and Anthropic Claude AI. All confidence assessments reflect OSINT methodology. This document does not contain classified information.</p>
</body>
</html>"""


def run_agentic_loop(client: anthropic.Anthropic, prompt: str) -> str:
    """Run the agentic web-search loop until end_turn, return final text."""
    messages = [{"role": "user", "content": prompt}]

    tools = [
        {
            "type": "web_search_20260209",
            "name": "web_search",
            "max_uses": 40,
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=16000,
            thinking={"type": "adaptive"},
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            # Collect all text content from the final response
            text_parts = [
                block.text
                for block in response.content
                if hasattr(block, "text") and block.type == "text"
            ]
            return "\n".join(text_parts)

        if response.stop_reason == "tool_use":
            # Append assistant turn and feed tool results back
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    # web_search is server-side; result is already in the response
                    # We pass an empty acknowledgment so the loop continues
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": "",
                        }
                    )
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
            continue

        # Unexpected stop reason — return whatever text we have
        text_parts = [
            block.text
            for block in response.content
            if hasattr(block, "text") and block.type == "text"
        ]
        return "\n".join(text_parts) or f"[Unexpected stop_reason: {response.stop_reason}]"


def markdown_to_html(md: str) -> str:
    """Convert minimal markdown to HTML for email display."""
    import re

    lines = md.split("\n")
    html_lines = []
    in_ul = False
    in_ol = False
    ol_counter = 0

    def close_lists():
        nonlocal in_ul, in_ol, ol_counter
        result = []
        if in_ul:
            result.append("</ul>")
            in_ul = False
        if in_ol:
            result.append("</ol>")
            in_ol = False
            ol_counter = 0
        return result

    def inline(text: str) -> str:
        # Bold
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        # Italic
        text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
        # Inline code
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
        # Links [text](url)
        text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', text)
        return text

    for line in lines:
        stripped = line.rstrip()

        # Headings
        h4 = re.match(r"^#### (.+)$", stripped)
        h3 = re.match(r"^### (.+)$", stripped)
        h2 = re.match(r"^## (.+)$", stripped)
        h1 = re.match(r"^# (.+)$", stripped)
        if h1:
            html_lines.extend(close_lists())
            html_lines.append(f"<h1>{inline(h1.group(1))}</h1>")
            continue
        if h2:
            html_lines.extend(close_lists())
            html_lines.append(f"<h2>{inline(h2.group(1))}</h2>")
            continue
        if h3:
            html_lines.extend(close_lists())
            html_lines.append(f"<h3>{inline(h3.group(1))}</h3>")
            continue
        if h4:
            html_lines.extend(close_lists())
            html_lines.append(f"<h4>{inline(h4.group(1))}</h4>")
            continue

        # Horizontal rule
        if re.match(r"^---+$", stripped):
            html_lines.extend(close_lists())
            html_lines.append("<hr>")
            continue

        # Unordered list
        ul_match = re.match(r"^[-*] (.+)$", stripped)
        if ul_match:
            if in_ol:
                html_lines.extend(close_lists())
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{inline(ul_match.group(1))}</li>")
            continue

        # Ordered list
        ol_match = re.match(r"^\d+\. (.+)$", stripped)
        if ol_match:
            if in_ul:
                html_lines.extend(close_lists())
            if not in_ol:
                html_lines.append("<ol>")
                in_ol = True
            html_lines.append(f"<li>{inline(ol_match.group(1))}</li>")
            continue

        # Empty line
        if stripped == "":
            html_lines.extend(close_lists())
            html_lines.append("")
            continue

        # Blockquote
        bq = re.match(r"^> (.+)$", stripped)
        if bq:
            html_lines.extend(close_lists())
            html_lines.append(f"<blockquote>{inline(bq.group(1))}</blockquote>")
            continue

        # Plain paragraph
        html_lines.extend(close_lists())
        html_lines.append(f"<p>{inline(stripped)}</p>")

    html_lines.extend(close_lists())
    return "\n".join(html_lines)


def send_email(subject: str, html_body: str, today: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    msg.attach(MIMEText(html_body, "html"))

    print(f"Sending email to {RECIPIENT_EMAIL} ...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("Email sent successfully.")


def save_report(content: str, today: str) -> str:
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/{today}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Report saved to {filename}")
    return filename


def main() -> None:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    et = ZoneInfo("America/New_York")
    now_et = datetime.now(et)
    today = now_et.strftime("%Y-%m-%d")
    today_long = now_et.strftime("%A, %B %d, %Y")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    print(f"Generating Ukraine-Russia War Analyst Brief for {today_long} ...")

    prompt = REPORT_PROMPT.format(today=today_long)

    try:
        report_markdown = run_agentic_loop(client, prompt)
    except Exception as exc:
        print(f"ERROR generating report: {exc}", file=sys.stderr)
        raise

    report_html_body = markdown_to_html(report_markdown)

    full_html = HTML_WRAPPER.format(
        today=today_long,
        generated_at=generated_at,
        body=report_html_body,
    )

    save_report(full_html, today)

    subject = f"Ukraine-Russia War Daily Analyst Brief — {today_long} | OUSW PB"
    send_email(subject, full_html, today)

    print("Done.")


if __name__ == "__main__":
    main()
