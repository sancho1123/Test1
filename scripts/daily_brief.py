"""
Daily Ukraine–Russia War Analyst Brief
OUSW Comptroller Program/Budget Analysts
Runs via GitHub Actions at 0500 ET daily.

Required GitHub Secrets:
  ANTHROPIC_API_KEY     — Anthropic API key
  GMAIL_SENDER          — Gmail address to send FROM (e.g. yourname@gmail.com)
  GMAIL_APP_PASSWORD    — Gmail App Password (not your login password)
  RECIPIENT_EMAIL       — Set in workflow env; defaults to ericjsanchez23@gmail.com
"""

import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic
from duckduckgo_search import DDGS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RECIPIENT = os.environ.get("RECIPIENT_EMAIL", "ericjsanchez23@gmail.com")
SENDER = os.environ.get("GMAIL_SENDER", "")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
TODAY = datetime.date.today().strftime("%Y-%m-%d")
SUBJECT = (
    f"{TODAY} | Daily Ukraine–Russia War Analyst Brief | "
    "Defense Articles, Stockpiles, Budget, Congressional RFI & "
    "Operation Epic Fury Cross-Theater Impacts"
)

# ---------------------------------------------------------------------------
# Web search helper
# ---------------------------------------------------------------------------

def search(query: str, max_results: int = 6) -> list[dict]:
    """Return list of {title, href, body} dicts from DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as exc:
        print(f"Search warning for '{query}': {exc}")
        return []


def format_search_block(results: list[dict]) -> str:
    lines = []
    for r in results:
        lines.append(f"- [{r.get('title','')}]({r.get('href','')}) — {r.get('body','')[:300]}")
    return "\n".join(lines) if lines else "No results found."


# ---------------------------------------------------------------------------
# Gather research
# ---------------------------------------------------------------------------

SEARCH_QUERIES = [
    f"Ukraine Russia war battlefield update {TODAY[:7]}",
    f"Ukraine defense articles weapons stockpiles US {TODAY[:7]}",
    "Operation Epic Fury Iran ceasefire Hormuz 2026",
    "Patriot interceptor stockpile depletion Ukraine Iran war 2026",
    "Ukraine aid funding congressional appropriations 2026",
    "Pentagon halt Ukraine weapons shipment stockpile 2026",
    "Russia missile drone strikes Ukraine infrastructure 2026",
    "Russia nuclear escalation warning Ukraine 2026",
    "North Korea troops Russia Ukraine war 2026",
    "Russia Iran China North Korea weapons sanctions 2026",
    "defense industrial base 155mm ammunition production 2026",
    "Ukraine PURL USAI PDA funding mechanism 2026",
    "Ukraine Russia ceasefire peace negotiations 2026",
    "Strait of Hormuz oil prices energy 2026",
]

def gather_research() -> str:
    print("Gathering research...")
    sections = []
    for q in SEARCH_QUERIES:
        results = search(q)
        block = format_search_block(results)
        sections.append(f"### Search: {q}\n{block}\n")
        print(f"  ✓ {q}")
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Report generation prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a senior defense analyst supporting the OUSW Comptroller Program/Budget office.
You write professional, analyst-grade intelligence briefs for Department of War senior leaders and
congressional support analysts. You write in direct, clear language without political commentary.
Every claim you make must be attributed to a specific source with a direct URL.
You label unverified claims as such. You distinguish between Confirmed, Medium-confidence, and Cannot-confirm findings.
Output the entire report as clean, well-structured HTML (no markdown, no code fences) ready for email delivery."""


def build_user_prompt(research: str, today: str) -> str:
    return f"""Today is {today}. Using the research results below, produce the full
Daily Ukraine–Russia War Analyst Brief for OUSW Comptroller P/B analysts.

RESEARCH RESULTS (from web search — use these as your primary sourcing):
{research}

REPORT REQUIREMENTS — produce ALL of the following sections in clean HTML:

PART I — SENIOR LEADER SNAPSHOT (approx. 1 page)
  A. Bottom Line Up Front (3–5 bullets — each with source URL and confidence level)
  B. Top Issues for OUSW Comptroller P/B Analysts (5–7 tagged bullets: [Funding] [PDA] [USAI]
     [Stockpiles] [Replenishment] [Congressional RFI] [Epic Fury/Iran Linkage] etc.)
  C. Watch Items for the Next 7 Days (table: indicator | why it matters | implication | source)
  D. Most Likely Congressional RFI Questions Today (5–10 questions)

PART II — ANALYST ANNEX
  1. Executive Summary (7–10 tagged bullets with source URLs and confidence)
  2. Battlefield and Military Operations (table: event | location | date | source | confidence | significance)
  3. Defense Articles, Weapons, Stockpiles (A. Patriot/Air Defense B. Artillery C. Allied Support
     D. Analysis table: what article | status | impact on Ukraine | readiness impact | RFI risk)
  4. Defense Industrial Base and Production Capacity (table: entity | system | finding | Ukraine impact | readiness impact | source)
  5. Funding, Budget, Appropriations, Congressional Relevance (table: mechanism | amount | status | comptroller relevance | likely RFI)
     — Cover: PDA, USAI, PURL, supplementals, FY2026 appropriations, FY2027 request, coalition pledges
  6. Operation Epic Fury / Iran and Ukraine–Russia War Linkage (mandatory — confirm or deny linkage with sources)
     — A. Stockpile competition B. Drone/missile warfare linkage C. Russia–Iran relationship post-Epic Fury
     — D. Energy and economic effects E. Strategic bandwidth
  7. Russia, Iran, China, North Korea, Belarus, Sanctions-Evasion Networks (table)
  8. Escalation Risks and Warning Indicators (table: indicator | risk level | source | confidence | implication)
  9. Congressional RFI Readiness (table: question | short answer | source links | confidence)
  10. Delta From Prior Report (note if no prior report available)
  11. Analyst Assessment (Confirmed Facts | Analyst Judgment | Cannot Confirm)
  12. Source Log (table: # | source | title | date | link | topic | confidence | notes)
  13. Confidence Matrix (table: claim | confidence | reason)

FORMATTING RULES:
- Output clean HTML only (no markdown, no triple backticks)
- Every major claim must have a source URL as an HTML hyperlink
- Use inline CSS for styling (professional dark blue headers, alternating table rows,
  warning boxes for high-priority items)
- Label every confidence level: HIGH (multiple credible sources), MEDIUM (single credible source),
  LOW (single source, unverified), CANNOT CONFIRM
- Label Russian/Ukrainian official claims explicitly
- Do not speculate without evidence
- Include UNCLASSIFIED // FOUO header and footer
- Report date: {today}
- Recipient: OUSW Comptroller Program/Budget Analysts"""


# ---------------------------------------------------------------------------
# Call Anthropic API
# ---------------------------------------------------------------------------

def generate_report(research: str, today: str) -> str:
    print("Generating report via Anthropic API...")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": build_user_prompt(research, today)}
        ],
    )
    print("  ✓ Report generated")
    return message.content[0].text


# ---------------------------------------------------------------------------
# Email delivery
# ---------------------------------------------------------------------------

def send_email(html_body: str, today: str) -> None:
    if not SENDER or not APP_PASSWORD:
        print("WARNING: GMAIL_SENDER or GMAIL_APP_PASSWORD not set. Skipping email send.")
        print("Report HTML written to /tmp/daily_brief_output.html instead.")
        with open("/tmp/daily_brief_output.html", "w") as f:
            f.write(html_body)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"] = SENDER
    msg["To"] = RECIPIENT

    # Plain-text fallback
    plain = f"Daily Ukraine–Russia War Analyst Brief — {today}\nSee HTML version for full report."
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    print(f"Sending email to {RECIPIENT}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
    print("  ✓ Email sent successfully")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"=== Daily Ukraine–Russia War Analyst Brief — {today} ===")

    research = gather_research()
    report_html = generate_report(research, today)
    send_email(report_html, today)

    print("=== Complete ===")


if __name__ == "__main__":
    main()
