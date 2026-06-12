"""
Send the daily Ukraine-Russia War Analyst Brief via Gmail.
Uses Gmail SMTP with an App Password (2FA must be enabled on the Gmail account).

Required environment variables:
  GMAIL_USER         — sender Gmail address (e.g., ericjsanchez23@gmail.com)
  GMAIL_APP_PASSWORD — Gmail App Password (not the account password)
  RECIPIENT_EMAIL    — recipient address (defaults to GMAIL_USER if not set)
  REPORT_PATH        — path to the markdown report (set by generate_brief.py)
  REPORT_DATE        — date string YYYY-MM-DD (set by generate_brief.py)
"""

import os
import sys
import smtplib
import mimetypes
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


def convert_md_to_html(md_content: str) -> str:
    """Convert markdown to HTML for the email body."""
    try:
        import markdown2
        html = markdown2.markdown(
            md_content,
            extras=["tables", "fenced-code-blocks", "header-ids", "break-on-newline"]
        )
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 13px; color: #1a1a1a; max-width: 900px; margin: 0 auto; padding: 20px; }}
  h1 {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 8px; }}
  h2 {{ color: #283593; border-bottom: 1px solid #283593; }}
  h3 {{ color: #3949ab; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 12px; }}
  th {{ background-color: #1a237e; color: white; padding: 8px; text-align: left; }}
  td {{ border: 1px solid #ccc; padding: 6px 8px; vertical-align: top; }}
  tr:nth-child(even) {{ background-color: #f5f5f5; }}
  blockquote {{ border-left: 4px solid #1a237e; margin: 10px 0; padding: 8px 16px; background: #e8eaf6; }}
  code {{ background: #f0f0f0; padding: 2px 4px; border-radius: 3px; }}
  strong {{ color: #b71c1c; }}
  a {{ color: #1565c0; }}
  .bluf {{ background: #e8f5e9; border: 1px solid #2e7d32; padding: 12px; border-radius: 4px; margin-bottom: 16px; }}
</style>
</head>
<body>
{html}
</body>
</html>"""
    except ImportError:
        # Fallback: plain text with minimal HTML wrapping
        escaped = md_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<html><body><pre style='font-family:monospace;font-size:12px;'>{escaped}</pre></body></html>"


def build_email(
    sender: str,
    recipient: str,
    report_date: str,
    md_content: str,
    report_path: Path,
) -> MIMEMultipart:
    msg = MIMEMultipart("mixed")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = (
        f"[UNCLASSIFIED] Daily Ukraine-Russia War Analyst Brief | "
        f"OUSW Comptroller P/B | {report_date}"
    )

    # Plain-text fallback
    text_part = MIMEText(md_content[:8000] + "\n\n[Full report attached as .md file]", "plain", "utf-8")

    # HTML body
    html_content = convert_md_to_html(md_content)
    html_part = MIMEText(html_content, "html", "utf-8")

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(text_part)
    alt_part.attach(html_part)
    msg.attach(alt_part)

    # Attach the markdown file
    if report_path.exists():
        attachment_name = report_path.name
        with open(report_path, "rb") as f:
            attachment_data = f.read()
        mime_base = MIMEBase("text", "markdown")
        mime_base.set_payload(attachment_data)
        encoders.encode_base64(mime_base)
        mime_base.add_header(
            "Content-Disposition",
            f'attachment; filename="{attachment_name}"',
        )
        msg.attach(mime_base)

    return msg


def send_email(msg: MIMEMultipart, sender: str, recipient: str, app_password: str):
    print(f"Connecting to Gmail SMTP...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipient, msg.as_string())
    print(f"Email sent to {recipient}")


def main():
    gmail_user = os.environ.get("GMAIL_USER", "").strip()
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    recipient = os.environ.get("RECIPIENT_EMAIL", gmail_user).strip()
    report_path_str = os.environ.get("REPORT_PATH", "").strip()
    report_date = os.environ.get("REPORT_DATE", datetime.now().strftime("%Y-%m-%d"))

    if not gmail_user or not app_password:
        print("ERROR: GMAIL_USER and GMAIL_APP_PASSWORD must be set.", file=sys.stderr)
        sys.exit(1)

    # Resolve report path
    if report_path_str:
        report_path = Path(report_path_str)
    else:
        # Find today's report
        reports_dir = Path(__file__).parent.parent / "reports"
        matches = list(reports_dir.glob(f"{report_date}_Ukraine-Russia*.md"))
        if not matches:
            print(f"ERROR: No report found for {report_date} in {reports_dir}", file=sys.stderr)
            sys.exit(1)
        report_path = matches[0]

    print(f"Sending report: {report_path}")
    md_content = report_path.read_text(encoding="utf-8")

    msg = build_email(gmail_user, recipient, report_date, md_content, report_path)
    send_email(msg, gmail_user, recipient, app_password)
    print("Done.")


if __name__ == "__main__":
    main()
