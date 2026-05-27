#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief Generator
OUSW Comptroller Program/Budget
Runs daily at 5:00 AM ET via GitHub Actions
"""

import os
import json
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic
from tavily import TavilyClient

# ── Configuration ────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TAVILY_API_KEY    = os.environ["TAVILY_API_KEY"]
GMAIL_ADDRESS     = os.environ["GMAIL_ADDRESS"]      # sender (must match app password)
GMAIL_APP_PASS    = os.environ["GMAIL_APP_PASSWORD"]
RECIPIENT_EMAIL   = os.environ.get("RECIPIENT_EMAIL", "ericjsanchez23@gmail.com")
MODEL             = "claude-sonnet-4-6"

TODAY = datetime.date.today().strftime("%Y-%m-%d")
TODAY_DISPLAY = datetime.date.today().strftime("%d %B %Y").upper()

# ── Search queries ────────────────────────────────────────────────────────────
SEARCH_QUERIES = [
    f"Ukraine Russia war latest news {TODAY}",
    f"Ukraine defense articles weapons stockpiles US aid {datetime.date.today().strftime('%B %Y')}",
    f"Operation Epic Fury Iran US military {datetime.date.today().strftime('%B %Y')}",
    f"US munitions stockpiles depletion Ukraine multi-theater 2026",
    f"Patriot air defense interceptors Ukraine shortage replenishment 2026",
    f"Ukraine USAI PDA supplemental appropriations Congress 2026 budget",
    f"Russia Iran North Korea China weapons supply Ukraine war 2026",
    f"Ukraine battlefield frontline Donetsk Kharkiv {datetime.date.today().strftime('%B %Y')}",
    f"US defense industrial base ammunition production expansion 2026",
    f"Ukraine Russia ceasefire negotiations {datetime.date.today().strftime('%B %Y')}",
]

# ── Tool definitions for Claude ──────────────────────────────────────────────
TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current news and information. "
            "Use for gathering latest Ukraine-Russia war reporting, defense articles, "
            "stockpile data, budget/appropriations info, and Operation Epic Fury updates."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5, max 10)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
]

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are a senior intelligence analyst producing daily classified-style briefings for the Department of War / OUSW Comptroller Program/Budget office. Today's date is {TODAY_DISPLAY}.

Your task: Generate a comprehensive Daily Ukraine-Russia War Analyst Brief in HTML format, suitable for a 10-minute read by senior analysts.

CRITICAL RULES:
1. Every major claim MUST have a cited source with a working URL.
2. Unverified claims must be labeled: Claimed / Low Confidence / Cannot Confirm.
3. Russian and Ukrainian official claims must be labeled as such.
4. Do not speculate without evidence.
5. Prioritize developments from the last 24-48 hours.
6. Use the web_search tool extensively — search at minimum 8-10 different query angles before writing.
7. The report must cover ALL required sections (see below).

REQUIRED REPORT SECTIONS:
PART I — SENIOR LEADER SNAPSHOT:
  A. Bottom Line Up Front (3-5 bullets; source + confidence per bullet)
  B. Top Issues for OUSW Comptroller P/B Analysts (5-7 tagged bullets)
  C. Watch Items for Next 7 Days (5 items)
  D. Most Likely Congressional RFI Questions Today (5-10 questions)

PART II — ANALYST ANNEX:
  1. Executive Summary (7-10 tagged bullets)
  2. Battlefield and Military Operations (table format)
  3. Defense Articles, Weapons, Stockpiles, and Munitions (tables; mandatory)
  4. Defense Industrial Base and Production Capacity
  5. Funding, Budget, Appropriations, and Congressional Relevance (table; mandatory)
  6. Operation Epic Fury / Iran and Ukraine-Russia War Linkage (mandatory)
  7. Russia, Iran, China, North Korea, Belarus — CRINK Support Networks
  8. Escalation Risks and Warning Indicators
  9. Congressional RFI Readiness Section (table format)
  10. Delta From Prior Report
  11. Analyst Assessment (Confirmed Facts / Analyst Judgment / Cannot Confirm)
  12. Source Log (numbered table with all sources + links)
  13. Confidence Matrix

OUTPUT FORMAT:
Return complete, valid HTML. Include inline CSS for professional formatting:
- Dark blue header (#1a3a5c)
- Section headers in varying shades of blue
- Color-coded confidence: green=HIGH, amber=MEDIUM, red=LOW/CANNOT CONFIRM
- Tables for all structured data
- Bullet-point style BLUF section with highlighted background
- Footer with classification marker and date

The final HTML must be self-contained and render correctly in Gmail."""

# ── Agentic report generation ─────────────────────────────────────────────────
def run_search(client: TavilyClient, query: str, max_results: int = 5) -> str:
    """Execute a Tavily search and return formatted results."""
    try:
        resp = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_raw_content=False
        )
        results = []
        for r in resp.get("results", []):
            results.append(
                f"Title: {r.get('title','')}\n"
                f"URL: {r.get('url','')}\n"
                f"Published: {r.get('published_date','Unknown')}\n"
                f"Snippet: {r.get('content','')[:600]}\n"
            )
        return "\n---\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {e}"


def generate_report() -> str:
    """Run the agentic loop: Claude searches the web then produces the HTML report."""
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    messages = [
        {
            "role": "user",
            "content": (
                f"Generate the Daily Ukraine-Russia War Analyst Brief for {TODAY_DISPLAY}. "
                "Use the web_search tool to research all required topic areas before writing. "
                "Search at least 8-10 different queries covering: battlefield updates, "
                "defense articles/stockpiles, Patriot interceptor status, USAI/PDA/appropriations, "
                "Operation Epic Fury linkage, Russia-DPRK-China-Iran cooperation, "
                "ceasefire/diplomacy, DIB production, congressional RFI topics, and escalation risks. "
                "After completing research, produce the complete HTML report."
            )
        }
    ]

    html_report = ""
    max_iterations = 20

    for _ in range(max_iterations):
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        # Collect text and tool use blocks
        tool_calls = []
        text_blocks = []
        for block in response.content:
            if block.type == "tool_use":
                tool_calls.append(block)
            elif block.type == "text":
                text_blocks.append(block.text)

        if text_blocks:
            html_report = "\n".join(text_blocks)

        # If done, break
        if response.stop_reason == "end_turn":
            break

        if not tool_calls:
            break

        # Execute tool calls
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for tc in tool_calls:
            query = tc.input.get("query", "")
            max_results = tc.input.get("max_results", 5)
            result_text = run_search(tavily, query, max_results)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": result_text
            })

        messages.append({"role": "user", "content": tool_results})

    return html_report


# ── Email delivery ────────────────────────────────────────────────────────────
def send_email(html_body: str):
    """Send the report via Gmail SMTP."""
    subject = f"DAILY UKRAINE-RUSSIA WAR ANALYST BRIEF | {TODAY_DISPLAY} | OUSW P/B"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = RECIPIENT_EMAIL

    # Plain-text fallback
    plain = (
        f"Daily Ukraine-Russia War Analyst Brief — {TODAY_DISPLAY}\n"
        "OUSW Comptroller Program/Budget\n\n"
        "Please view this email in an HTML-capable client.\n\n"
        "Report generated from open sources. All claims sourced and linked in the HTML version."
    )
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
        server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

    print(f"[OK] Report emailed to {RECIPIENT_EMAIL}")


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    print(f"[*] Generating analyst brief for {TODAY_DISPLAY}...")
    html = generate_report()

    if not html.strip():
        raise RuntimeError("Report generation returned empty content.")

    print(f"[*] Report generated ({len(html):,} chars). Sending email...")
    send_email(html)
    print("[*] Done.")


if __name__ == "__main__":
    main()
