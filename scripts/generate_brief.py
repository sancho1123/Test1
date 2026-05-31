"""
Daily Ukraine-Russia War Analyst Brief Generator
OUSW Comptroller Program/Budget Office

Runs via GitHub Actions at 0500 ET daily.
Requires environment variables:
  ANTHROPIC_API_KEY   - Anthropic API key
  BRAVE_API_KEY       - Brave Search API key (get free tier at https://api.search.brave.com)
  GMAIL_FROM          - Sender Gmail address (e.g. ericjsanchez23@gmail.com)
  GMAIL_APP_PASSWORD  - Gmail App Password (not regular password; enable 2FA first)
  REPORT_RECIPIENT    - Recipient email address
  REPORT_DATE         - Optional override date (YYYY-MM-DD); defaults to today
"""

import os
import json
import smtplib
import requests
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import anthropic

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
GMAIL_FROM = os.environ.get("GMAIL_FROM", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
REPORT_RECIPIENT = os.environ.get("REPORT_RECIPIENT", "ericjsanchez23@gmail.com")

_date_override = os.environ.get("REPORT_DATE", "").strip()
REPORT_DATE: date = (
    datetime.strptime(_date_override, "%Y-%m-%d").date()
    if _date_override
    else date.today()
)

REPORT_FILENAME = (
    f"{REPORT_DATE.strftime('%Y-%m-%d')}"
    "_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md"
)
REPORT_PATH = Path(__file__).parent.parent / "reports" / REPORT_FILENAME

SEARCH_WINDOW_DAYS = 2  # search for the last N days of news


# ──────────────────────────────────────────────────────────────────────────────
# Search helper (Brave Search API)
# ──────────────────────────────────────────────────────────────────────────────

def brave_search(query: str, count: int = 8) -> list[dict]:
    """Return a list of {title, url, description, published} dicts."""
    if not BRAVE_API_KEY:
        return []
    url = "https://api.search.brave.com/res/v1/news/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY,
    }
    params = {
        "q": query,
        "count": count,
        "freshness": f"p{SEARCH_WINDOW_DAYS}d",
        "text_decorations": False,
        "safesearch": "moderate",
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "published": item.get("age", ""),
                "source": item.get("meta_url", {}).get("hostname", ""),
            })
        return results
    except Exception as exc:
        print(f"[WARN] Brave search failed for '{query}': {exc}")
        return []


def gather_intelligence() -> dict[str, list[dict]]:
    """Run all required searches and return categorized results."""
    year = REPORT_DATE.year
    month = REPORT_DATE.strftime("%B")

    queries = {
        "battlefield": (
            f"Ukraine Russia war frontline battlefield update {month} {year}"
        ),
        "missile_drone_attacks": (
            f"Russia drone missile strike Ukraine {month} {year}"
        ),
        "defense_articles": (
            f"Ukraine US defense weapons aid Patriot NASAMS {month} {year}"
        ),
        "stockpiles": (
            f"Ukraine air defense interceptor stockpile shortage Patriot {year}"
        ),
        "dib_production": (
            f"US defense industrial base Patriot missile production replenishment {year}"
        ),
        "funding_appropriations": (
            f"Ukraine war funding appropriations Congress USAI {month} {year}"
        ),
        "epic_fury": (
            f"Operation Epic Fury Iran US military {month} {year}"
        ),
        "epic_fury_ukraine_linkage": (
            f"Operation Epic Fury Ukraine weapons stockpile competition {year}"
        ),
        "crink_supply": (
            f"Russia North Korea China Iran weapons supply Ukraine war {year}"
        ),
        "escalation": (
            f"Russia escalation nuclear Oreshnik hypersonic Ukraine {month} {year}"
        ),
        "sanctions": (
            f"Russia sanctions evasion China dual-use components Ukraine {year}"
        ),
        "congressional": (
            f"Congress Ukraine aid oversight RFI defense appropriations {month} {year}"
        ),
    }

    results: dict[str, list[dict]] = {}
    for category, query in queries.items():
        print(f"[INFO] Searching: {query}")
        results[category] = brave_search(query)
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Report generation via Claude API
# ──────────────────────────────────────────────────────────────────────────────

REPORT_SYSTEM_PROMPT = """You are a senior intelligence analyst supporting the Department of War / OUSW Comptroller Program/Budget Office. Your task is to produce a daily analyst-grade Ukraine-Russia War brief that is authoritative, sourced, and directly useful for responding to Congressional RFIs, senior leader questions, and budget/execution inquiries.

CRITICAL RULES:
1. Every major claim MUST have a source with a direct working URL.
2. If a claim cannot be confirmed, state: "I cannot confirm this."
3. Clearly label: Confirmed | Likely | Claimed but unverified | Disputed | Cannot confirm.
4. Russian and Ukrainian government claims must be labeled as claims unless independently confirmed.
5. No political commentary. No sensational language. No unsupported claims.
6. Write at a Department-level analyst standard: direct, precise, sourced.
7. Use all provided search results as your primary source material.
8. Where search results are thin, acknowledge the gap — do not invent sources or URLs.
"""

REPORT_TEMPLATE = """
Using the intelligence gathered below, produce a complete Daily Ukraine-Russia War Analyst Brief for {report_date}.

The report must follow this EXACT structure. Do not skip any section.

---
# Daily Ukraine–Russia War Analyst Brief
## Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury Cross-Theater Impacts
### Date: {report_date} | OUSW Comptroller Program/Budget Office | UNCLASSIFIED // FOR OFFICIAL USE ONLY

# PART I — SENIOR LEADER SNAPSHOT
## A. Bottom Line Up Front (BLUF)
[5 bullets. Each must have source name, direct URL, confidence level: HIGH/MEDIUM/LOW]

## B. Top Issues for OUSW Comptroller P/B Analysts
[7 bullets. Each tagged: [Funding] [Appropriations] [Execution] [PDA] [USAI] [Defense Articles] [Stockpiles] [Replenishment] [Congressional RFI] [Readiness] [Epic Fury / Iran Linkage]]
[Each bullet: what happened, why it matters, what question Congress or senior leaders may ask]

## C. Watch Items for the Next 7 Days
[5 items: indicator, why it matters, budget/defense article/congressional implication, source link]

## D. Most Likely Congressional RFI Questions Today
[10 questions based on today's reporting]

---
# PART II — ANALYST ANNEX

## 1. Executive Summary
[10 bullets, each tagged with topic, one-sentence summary, why it matters, source name, URL, confidence]

## 2. Battlefield and Military Operations
[Cover: frontline changes, Russian offensives, Ukrainian counteroffensives, missile/drone attacks, air defense, Black Sea, territorial changes, casualties if credible]
[For each event use a table: Event | Location | Date/Timeframe | Source | Link | Confidence | Significance]

## 3. Defense Articles, Weapons, Stockpiles, and Munitions
[Sections A (U.S.-provided) B (Allied) C (Stockpile/Readiness table) D (Required analysis)]

## 4. Defense Industrial Base and Production Capacity
[Patriot and other key systems; production rates, contracts, constraints, timelines]

## 5. Funding, Budget, Appropriations, and Congressional Relevance
[Table: Funding item | Account/Mechanism | Amount | Source | Link | Confidence | Comptroller Relevance | Potential RFI]

## 6. Operation Epic Fury / Iran and Ukraine-Russia War Linkage
[Sections A (stockpile competition) B (drone/missile linkage) C (Russia-Iran relationship) D (energy/economic) E (strategic bandwidth)]
[If no credible connection: state "I cannot confirm a direct linkage between Operation Epic Fury and the Ukraine-Russia War in today's reporting."]

## 7. Russia, Iran, China, North Korea, Belarus — Sanctions-Evasion Networks
[Table: Actor | Assistance Type | Confidence | Impact on Ukraine War | Congressional/Sanctions Relevance]

## 8. Escalation Risks and Warning Indicators
[Table: Indicator | Risk Level | Confidence | Why It Matters | U.S. Policy/Budget Implication]

## 9. Congressional RFI Readiness Section
[Table: Likely RFI Question | Short Answer | Source Links | Confidence]

## 10. Delta From Prior Report
[Compare to prior day. If no prior: state "No prior report was available for comparison."]

## 11. Analyst Assessment
[Confirmed Facts | Analyst Judgment | Cannot Confirm — clearly labeled]
[What matters most today, watch items, congressional risk, budget execution risk, readiness risk, cross-theater linkage]

## 12. Required News Article / Source Log
[Table: # | Source | Title | Date Published | Link | Topic | Confidence | Notes]
[Every source used in the report must appear here with a direct working URL]

## 13. Confidence Matrix
[Table: Claim/Topic | Confidence | Reason]

---
*Report generated: {report_date} | Prepared for: OUSW Comptroller P/B Office*
*Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY*
*Next report: {next_date}*

---

INTELLIGENCE GATHERED (use this as your primary source material):

{intelligence_json}
"""


def format_intelligence(intelligence: dict[str, list[dict]]) -> str:
    """Format gathered search results into readable text for the prompt."""
    sections = []
    for category, results in intelligence.items():
        if not results:
            sections.append(f"\n### {category.upper()}\nNo results returned for this category.\n")
            continue
        items = []
        for r in results:
            items.append(
                f"- [{r['title']}]({r['url']})\n"
                f"  Source: {r['source']} | Published: {r['published']}\n"
                f"  Summary: {r['description']}"
            )
        sections.append(f"\n### {category.upper()}\n" + "\n".join(items))
    return "\n".join(sections)


def generate_report(intelligence: dict[str, list[dict]]) -> str:
    """Call Claude API to generate the full analyst brief."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    next_date = (REPORT_DATE + timedelta(days=1)).strftime("%Y-%m-%d")
    intel_formatted = format_intelligence(intelligence)

    user_prompt = REPORT_TEMPLATE.format(
        report_date=REPORT_DATE.strftime("%Y-%m-%d"),
        next_date=next_date,
        intelligence_json=intel_formatted,
    )

    print("[INFO] Calling Claude API to generate report...")
    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        system=REPORT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    report_text = message.content[0].text
    print(f"[INFO] Report generated: {len(report_text)} characters")
    return report_text


# ──────────────────────────────────────────────────────────────────────────────
# Email delivery via Gmail SMTP
# ──────────────────────────────────────────────────────────────────────────────

def send_email(report_markdown: str) -> None:
    """Send the report via Gmail SMTP using an App Password."""
    if not GMAIL_FROM or not GMAIL_APP_PASSWORD:
        print("[WARN] Gmail credentials not configured. Skipping email.")
        return

    subject = (
        f"Daily Ukraine-Russia War Analyst Brief — {REPORT_DATE.strftime('%Y-%m-%d')} "
        f"| OUSW Comptroller P/B | UNCLASSIFIED"
    )

    html_body = markdown_to_html(report_markdown)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_FROM
    msg["To"] = REPORT_RECIPIENT

    msg.attach(MIMEText(report_markdown, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    print(f"[INFO] Sending email to {REPORT_RECIPIENT}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_FROM, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_FROM, [REPORT_RECIPIENT], msg.as_string())
    print("[INFO] Email sent successfully.")


def markdown_to_html(md: str) -> str:
    """Convert markdown to basic HTML for email display."""
    try:
        import markdown
        body = markdown.markdown(
            md,
            extensions=["tables", "fenced_code", "nl2br"],
        )
    except ImportError:
        # Fallback: wrap in <pre> if markdown package unavailable
        body = f"<pre style='font-family:monospace;font-size:12px;'>{md}</pre>"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 13px; color: #1a1a1a; max-width: 900px; margin: 0 auto; padding: 20px; }}
  h1 {{ font-size: 18px; color: #1a237e; border-bottom: 2px solid #1a237e; padding-bottom: 6px; }}
  h2 {{ font-size: 15px; color: #283593; margin-top: 24px; }}
  h3 {{ font-size: 13px; color: #37474f; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 12px; }}
  th {{ background: #1a237e; color: white; padding: 6px 8px; text-align: left; }}
  td {{ border: 1px solid #ccc; padding: 5px 8px; vertical-align: top; }}
  tr:nth-child(even) {{ background: #f5f5f5; }}
  blockquote {{ border-left: 3px solid #1a237e; margin: 8px 0; padding: 4px 12px; background: #f0f4ff; color: #333; }}
  code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-size: 11px; }}
  a {{ color: #1565c0; }}
  hr {{ border: none; border-top: 1px solid #ccc; margin: 20px 0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Save report to disk
# ──────────────────────────────────────────────────────────────────────────────

def save_report(report: str) -> None:
    """Save the generated report as a markdown file in the reports/ directory."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"[INFO] Report saved: {REPORT_PATH}")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"[INFO] Generating Daily Analyst Brief for {REPORT_DATE} ...")

    # Step 1: Gather intelligence
    intelligence = gather_intelligence()

    # Step 2: Generate report via Claude
    report = generate_report(intelligence)

    # Step 3: Save to disk (GitHub Actions will commit this)
    save_report(report)

    # Step 4: Email the report
    send_email(report)

    print("[INFO] Done.")


if __name__ == "__main__":
    main()
