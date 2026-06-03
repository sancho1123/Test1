"""
Send the daily Ukraine-Russia analyst brief via Gmail API.
Reads the report path from brief_path.txt written by generate_brief.py.
Requires GMAIL_CREDENTIALS and GMAIL_TOKEN secrets in GitHub Actions.
"""

import os
import sys
import json
import base64
import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

RECIPIENT = "ericjsanchez23@gmail.com"
SENDER = os.environ.get("GMAIL_SENDER", RECIPIENT)


def load_credentials() -> Credentials:
    creds_json = os.environ.get("GMAIL_CREDENTIALS")
    token_json = os.environ.get("GMAIL_TOKEN")
    if not creds_json or not token_json:
        raise RuntimeError("GMAIL_CREDENTIALS and GMAIL_TOKEN environment variables are required.")
    token_data = json.loads(token_json)
    return Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", ["https://www.googleapis.com/auth/gmail.send"]),
    )


def read_report() -> tuple[str, str]:
    """Return (filepath, content) of today's report."""
    brief_path_file = Path("brief_path.txt")
    if brief_path_file.exists():
        filepath = brief_path_file.read_text().strip()
    else:
        date_str = datetime.date.today().isoformat()
        reports_dir = Path(__file__).parent.parent / "reports"
        filepath = str(reports_dir / f"{date_str}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md")

    content = Path(filepath).read_text(encoding="utf-8")
    return filepath, content


def build_email(filepath: str, content: str) -> dict:
    date_str = datetime.date.today().strftime("%B %d, %Y")
    subject = f"Daily Ukraine–Russia War Analyst Brief | OUSW P/B | {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = RECIPIENT

    # Plain text fallback
    plain = MIMEText(content, "plain", "utf-8")

    # HTML version — wrap markdown in pre block for readable formatting
    html_content = f"""<html><body>
<h2>Daily Ukraine–Russia War Analyst Brief</h2>
<h3>OUSW Comptroller Program/Budget Office | {date_str}</h3>
<hr>
<pre style="font-family: monospace; font-size: 13px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word;">
{content}
</pre>
</body></html>"""
    html = MIMEText(html_content, "html", "utf-8")

    msg.attach(plain)
    msg.attach(html)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def send_email(service, email_body: dict):
    result = service.users().messages().send(userId="me", body=email_body).execute()
    print(f"Email sent. Message ID: {result['id']}")
    return result


def main():
    try:
        creds = load_credentials()
        service = build("gmail", "v1", credentials=creds)
        filepath, content = read_report()
        email_body = build_email(filepath, content)
        send_email(service, email_body)
    except Exception as e:
        print(f"ERROR sending email: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
