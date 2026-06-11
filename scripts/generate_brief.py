#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief Generator
For: OUSW Comptroller Program/Budget Analysts
Runs daily at 5:00 AM ET via GitHub Actions
Sends to: ericjsanchez23@gmail.com
"""

import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic

REPORT_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "ericjsanchez23@gmail.com")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

BRIEF_PROMPT = f"""
Today's date is {REPORT_DATE}. You are generating a Daily Ukraine-Russia War Analyst Brief for
OUSW Comptroller Program/Budget analysts at the Department of War.

Search for the latest news (last 24-48 hours) on all of the following topics:
1. Ukraine-Russia war frontline and battlefield updates
2. Russian missile and drone attacks on Ukraine
3. Ukrainian counterstrikes on Russia
4. U.S. defense articles and weapons provided to Ukraine (Patriot, NASAMS, HIMARS, 155mm, etc.)
5. U.S. Patriot PAC-3 and air defense interceptor stockpile status
6. Operation Epic Fury / U.S.-Iran conflict aftermath and current status
7. Cross-theater defense article competition (Ukraine + Epic Fury demand on same systems)
8. U.S. Congressional action on Ukraine funding (PDA, USAI, supplementals, PURL)
9. FY26 appropriations for Ukraine (House vs. Senate vs. enacted)
10. North Korea and Iran supplying Russia with weapons, troops, ammunition
11. Russia-Iran-North Korea-China military cooperation networks
12. U.S. 155mm and munitions production rates vs. replenishment targets
13. Ukraine peace negotiations status
14. Escalation risks (nuclear signaling, hypersonic use, NATO border incidents)

After researching, produce a complete Daily Ukraine-Russia War Analyst Brief following this exact structure.
The report should be a 10-minute read. Every major claim MUST have a source with a clickable URL.
Clearly label all confidence levels: HIGH / MEDIUM / LOW / Cannot confirm.
Label Russian/Ukrainian official claims as such.

REQUIRED REPORT STRUCTURE:

---
# DAILY UKRAINE-RUSSIA WAR ANALYST BRIEF
# Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury
# Report Date: {REPORT_DATE} | OUSW Comptroller Program/Budget
---

## PART I — SENIOR LEADER SNAPSHOT

### A. Bottom Line Up Front (3-5 bullets with source, link, confidence each)

### B. Top 7 Issues for OUSW Comptroller P/B Analysts
(Tag each: [Funding] [PDA] [USAI] [Stockpiles] [Defense Articles] [Replenishment] [Epic Fury / Iran Linkage] [Congressional RFI] [Readiness] [DIB] [Appropriations] [Execution] [Sanctions])

### C. Watch Items for the Next 7 Days (5 items with indicator, why it matters, budget implication, source)

### D. Most Likely Congressional RFI Questions Today (10 questions)

---

## PART II — ANALYST ANNEX

### 1. Executive Summary (8 bullets: tag, development, why it matters, source, confidence)

### 2. Battlefield and Military Operations
(Tables for: major strikes, frontline changes, DPRK forces, Ukrainian counterattacks)

### 3. Defense Articles, Weapons, Stockpiles
A. U.S.-Provided Defense Articles (status table: Patriot PAC-3, NASAMS, HIMARS, 155mm, etc.)
B. Allied Defense Articles (UK, Germany, Norway, South Korea, NATO)
C. Critical Stockpile Finding — PATRIOT PAC-3 DUAL-THEATER DEPLETION

### 4. Defense Industrial Base (155mm production, PAC-3 production, Russian drone production)

### 5. Funding, Budget, Appropriations, Congressional Relevance
(Table: House package, NDAA USAI, FY26 appropriations, PDA status, PURL, replenishment)

### 6. Operation Epic Fury / Iran Linkage (MANDATORY)
A. Weapons/Stockpile Competition — confirm or deny linkage with sources
B. Russia-Iran relationship post-Epic Fury
C. Energy/Economic effects
D. Strategic Bandwidth (label as Analyst Judgment if not sourced)

### 7. Adversary Networks (Russia, Iran, China, North Korea, Belarus)

### 8. Escalation Risks (table: indicator, risk level HIGH/MEDIUM/LOW, source, implication)

### 9. Congressional RFI Readiness (table: question, short answer, source links, confidence)

### 10. Delta From Prior Report (what changed since yesterday, or state "First report of series")

### 11. Analyst Assessment
- Confirmed Facts (bulleted)
- Analyst Judgment (labeled)
- Cannot Confirm (labeled)

### 12. Source Log (table: #, source, title, date, URL, confidence, notes — ALL sources used)

### 13. Confidence Matrix (table: claim/topic, confidence, reason)

---

STRICT RULES:
- Every major claim MUST have a working URL
- If you cannot find a source, say "I cannot confirm this" — do not present as fact
- Label Russian/Ukrainian official claims as claims
- No speculation without evidence
- No political commentary
- Use direct, clear language suitable for Department-level senior analysts
- This report serves congressional RFI readiness, not media consumption

File name: {REPORT_DATE}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB
"""


def generate_report() -> str:
    """Call Claude with web search enabled to generate the analyst brief."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"[{REPORT_DATE}] Generating Daily Ukraine-Russia War Analyst Brief...")

    # Use claude with web search tool
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 20}],
        messages=[{"role": "user", "content": BRIEF_PROMPT}],
    )

    # Extract the text content from the response
    report_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            report_text += block.text

    if not report_text:
        raise ValueError("No report text generated from Claude API response")

    print(f"[{REPORT_DATE}] Report generated successfully ({len(report_text)} chars)")
    return report_text


def markdown_to_html(text: str) -> str:
    """Convert basic markdown to HTML for email rendering."""
    lines = text.split("\n")
    html_lines = []
    in_table = False
    in_ul = False

    for line in lines:
        stripped = line.strip()

        # Headers
        if stripped.startswith("#### "):
            html_lines.append(f"<h4>{stripped[5:]}</h4>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
        # Table rows
        elif stripped.startswith("|"):
            if not in_table:
                html_lines.append('<table border="1" style="border-collapse:collapse;width:100%;font-size:12px;">')
                in_table = True
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
                continue  # skip separator rows
            row_html = "<tr>" + "".join(f"<td style='padding:4px 8px;'>{c}</td>" for c in cells) + "</tr>"
            html_lines.append(row_html)
        elif in_table and not stripped.startswith("|"):
            html_lines.append("</table>")
            in_table = False
            html_lines.append(f"<p>{stripped}</p>" if stripped else "")
        # Bullet lists
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{stripped[2:]}</li>")
        elif in_ul and not (stripped.startswith("- ") or stripped.startswith("* ")):
            html_lines.append("</ul>")
            in_ul = False
            html_lines.append(f"<p>{stripped}</p>" if stripped else "")
        # Bold/italic inline
        elif stripped:
            # Convert **bold** and *italic*
            import re
            processed = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            processed = re.sub(r"\*(.+?)\*", r"<em>\1</em>", processed)
            # Convert [text](url) links
            processed = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', processed)
            html_lines.append(f"<p>{processed}</p>")
        else:
            html_lines.append("")

    if in_table:
        html_lines.append("</table>")
    if in_ul:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def send_email(report_text: str) -> None:
    """Send the report via Gmail SMTP."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("[WARNING] Gmail credentials not set — saving report to file only")
        save_report_to_file(report_text)
        return

    subject = f"Daily Ukraine-Russia War Analyst Brief | OUSW P/B | {REPORT_DATE}"

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;font-size:13px;color:#1a1a1a;max-width:900px;margin:0 auto;padding:20px;line-height:1.5;">
    <h1 style="font-size:18px;color:#002868;border-bottom:3px solid #BF0A30;padding-bottom:8px;">
      DAILY UKRAINE–RUSSIA WAR ANALYST BRIEF
    </h1>
    <p style="font-size:11px;color:#555;">
      <strong>Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury</strong><br>
      Report Date: <strong>{REPORT_DATE}</strong> &nbsp;|&nbsp; Distribution: OUSW Comptroller Program/Budget<br>
      Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY
    </p>
    <hr>
    {markdown_to_html(report_text)}
    <hr>
    <p style="font-size:10px;color:#777;">
      Auto-generated by OUSW P/B Daily Brief Routine | File: {REPORT_DATE}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB
    </p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(report_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    print(f"[{REPORT_DATE}] Sending email to {RECIPIENT_EMAIL}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

    print(f"[{REPORT_DATE}] Email sent successfully to {RECIPIENT_EMAIL}")
    save_report_to_file(report_text)


def save_report_to_file(report_text: str) -> None:
    """Save report to reports/ directory for archiving."""
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/{REPORT_DATE}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"[{REPORT_DATE}] Report saved to {filename}")


if __name__ == "__main__":
    try:
        report = generate_report()
        send_email(report)
        print(f"[{REPORT_DATE}] Daily brief complete.")
    except Exception as e:
        print(f"[ERROR] Brief generation failed: {e}", file=sys.stderr)
        sys.exit(1)
