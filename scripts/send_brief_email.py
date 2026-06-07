#!/usr/bin/env python3
"""
Send the daily Ukraine–Russia War Analyst Brief via Gmail SMTP.
Uses Gmail App Password stored as GMAIL_APP_PASSWORD env var / GitHub secret.
"""

import argparse
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


def build_failure_email(report_date: str) -> tuple[str, str, str]:
    subject = f"[FAILED] Ukraine–Russia War Daily Brief — {report_date}"
    plain = (
        f"The daily Ukraine–Russia War Analyst Brief for {report_date} "
        f"FAILED to generate. Please check the GitHub Actions run log at:\n"
        f"https://github.com/sancho1123/Test1/actions\n\n"
        f"This message was sent automatically by the OUSW P/B daily brief workflow."
    )
    html = f"""<html><body>
    <p style="color:#c0392b;font-weight:bold;">BRIEF GENERATION FAILED</p>
    <p>The daily Ukraine–Russia War Analyst Brief for <strong>{report_date}</strong> failed to generate.</p>
    <p>Check the workflow run log:<br>
    <a href="https://github.com/sancho1123/Test1/actions">
    https://github.com/sancho1123/Test1/actions</a></p>
    </body></html>"""
    return subject, plain, html


def build_brief_email(report_date: str, md_path: str, html_path: str) -> tuple[str, str, str]:
    subject = f"Ukraine–Russia War Daily Analyst Brief — {report_date} | OUSW P/B"

    plain = Path(md_path).read_text(encoding="utf-8") if md_path and Path(md_path).exists() else (
        "Brief generated. HTML version attached."
    )

    html_body = Path(html_path).read_text(encoding="utf-8") if html_path and Path(html_path).exists() else (
        f"<p>Brief for {report_date} generated. See attached markdown.</p>"
    )

    return subject, plain, html_body


def send_email(
    sender: str,
    password: str,
    recipient: str,
    subject: str,
    plain_body: str,
    html_body: str,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg["X-Mailer"] = "OUSW-PB-Daily-Brief-Workflow/1.0"

    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    print(f"  Connecting to {GMAIL_SMTP_HOST}:{GMAIL_SMTP_PORT}...")
    with smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())

    print(f"  Email sent to {recipient}.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--date", default=datetime.utcnow().strftime("%Y-%m-%d"))
    parser.add_argument("--md-file", default="")
    parser.add_argument("--html-file", default="")
    parser.add_argument("--failure-notice", action="store_true")
    args = parser.parse_args()

    sender = os.environ.get("GMAIL_SENDER", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not sender or not password:
        print("ERROR: GMAIL_SENDER and GMAIL_APP_PASSWORD must be set.", file=sys.stderr)
        sys.exit(1)

    if not args.to:
        print("ERROR: --to recipient is required.", file=sys.stderr)
        sys.exit(1)

    if args.failure_notice:
        subject, plain, html = build_failure_email(args.date)
    else:
        subject, plain, html = build_brief_email(args.date, args.md_file, args.html_file)

    print(f"[{datetime.utcnow().isoformat()}] Sending brief email...")
    send_email(sender, password, args.to, subject, plain, html)
    print(f"[{datetime.utcnow().isoformat()}] Email delivery complete.")


if __name__ == "__main__":
    main()
