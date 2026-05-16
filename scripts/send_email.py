#!/usr/bin/env python3
"""
Send the daily Ukraine-Russia War Analyst Brief via Gmail SMTP.
Requires GMAIL_USER and GMAIL_APP_PASSWORD environment variables.
"""

import os
import sys
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

REPORT_DATE = datetime.date.today().strftime("%Y-%m-%d")
REPORT_FILE = "reports/latest_brief.md"
RECIPIENT = os.environ.get("RECIPIENT_EMAIL", "ericjsanchez23@gmail.com")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
SUBJECT = f"Daily Ukraine–Russia War Analyst Brief | {REPORT_DATE} | OUSW P/B"


def load_report() -> str:
    if not os.path.exists(REPORT_FILE):
        print(f"ERROR: Report file not found: {REPORT_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def markdown_to_html(md: str) -> str:
    lines = md.split("\n")
    html_lines = []
    in_table = False
    in_code = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            if in_code:
                html_lines.append("<pre><code>")
            else:
                html_lines.append("</code></pre>")
            continue

        if in_code:
            html_lines.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        if stripped.startswith("# "):
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("## "):
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append(f"<h2 style='color:#1a3a5c;border-bottom:2px solid #1a3a5c;'>{stripped[3:]}</h2>")
        elif stripped.startswith("### "):
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append(f"<h3 style='color:#2e5984;'>{stripped[4:]}</h3>")
        elif stripped.startswith("#### "):
            html_lines.append(f"<h4 style='color:#4a7aad;'>{stripped[5:]}</h4>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html_lines.append(f"<li>{stripped[2:]}</li>")
        elif stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not in_table:
                html_lines.append("<table style='border-collapse:collapse;width:100%;font-size:13px;'>")
                in_table = True
            if all(set(c) <= set("-: ") for c in cells):
                continue
            row = "".join(f"<td style='border:1px solid #ccc;padding:6px;'>{c}</td>" for c in cells)
            html_lines.append(f"<tr>{row}</tr>")
        elif stripped == "---":
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append("<hr style='border:1px solid #ccc;'>")
        elif stripped.startswith("**") and stripped.endswith("**"):
            html_lines.append(f"<p><strong>{stripped[2:-2]}</strong></p>")
        elif stripped == "":
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append("<br>")
        else:
            text = stripped.replace("**", "<strong>", 1)
            while "**" in text:
                text = text.replace("**", "</strong>", 1)
            html_lines.append(f"<p style='margin:4px 0;'>{text}</p>")

    if in_table:
        html_lines.append("</table>")

    header = f"""
    <div style='background:#1a3a5c;color:white;padding:16px;font-family:Arial,sans-serif;'>
      <h1 style='margin:0;font-size:18px;'>DAILY UKRAINE–RUSSIA WAR ANALYST BRIEF</h1>
      <p style='margin:4px 0;font-size:13px;'>Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury</p>
      <p style='margin:4px 0;font-size:13px;'>{REPORT_DATE} | UNCLASSIFIED // FOR OFFICIAL USE ONLY | OUSW Comptroller P/B</p>
    </div>
    <div style='font-family:Arial,sans-serif;font-size:14px;line-height:1.6;padding:16px;'>
    """
    footer = "</div>"
    return header + "\n".join(html_lines) + footer


def send_email(report_md: str) -> None:
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("ERROR: GMAIL_USER or GMAIL_APP_PASSWORD not set.", file=sys.stderr)
        sys.exit(1)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT

    plain = MIMEText(report_md, "plain", "utf-8")
    html_content = markdown_to_html(report_md)
    html = MIMEText(html_content, "html", "utf-8")

    msg.attach(plain)
    msg.attach(html)

    print(f"Sending email to {RECIPIENT}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, RECIPIENT, msg.as_string())

    print("Email sent successfully.")


if __name__ == "__main__":
    report = load_report()
    send_email(report)
