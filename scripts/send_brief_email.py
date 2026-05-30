#!/usr/bin/env python3
"""
Send the daily Ukraine-Russia War brief via Gmail SMTP.
Requires GMAIL_SENDER and GMAIL_APP_PASSWORD environment variables.
"""

import argparse
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_brief(input_path: str) -> None:
    sender = os.environ["GMAIL_SENDER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ.get("GMAIL_RECIPIENT", sender)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with open(input_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = (
        f"{today} | Daily Ukraine-Russia War Analyst Brief | OUSW Comptroller P/B"
    )
    msg["From"] = sender
    msg["To"] = recipient
    msg["X-Priority"] = "2"

    # Plain-text fallback
    plain = (
        f"Daily Ukraine-Russia War Analyst Brief\n"
        f"Date: {today}\n"
        f"Department of War | OUSW Comptroller Program-Budget Office\n\n"
        f"Please view this email in an HTML-capable email client.\n"
    )
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    print(f"Sending brief to {recipient}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())
    print("Email sent successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="/tmp/brief.html")
    args = parser.parse_args()
    send_brief(args.input)
