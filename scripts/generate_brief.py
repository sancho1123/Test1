"""
Daily Ukraine–Russia War Analyst Brief Generator
For: OUSW Comptroller Program/Budget Analysts
Runs via GitHub Actions at 5:00 AM ET daily.

Required environment variables (set as GitHub Secrets):
  ANTHROPIC_API_KEY   — Anthropic API key
  TAVILY_API_KEY      — Tavily web search API key (https://tavily.com)
  GMAIL_SENDER        — Gmail address used to send (e.g. yourname@gmail.com)
  GMAIL_APP_PASSWORD  — Gmail App Password (not your login password)
  RECIPIENT_EMAIL     — Recipient address (e.g. ericjsanchez23@gmail.com)
"""

import os
import json
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic
from tavily import TavilyClient

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TODAY = datetime.date.today().strftime("%Y-%m-%d")
SUBJECT = f"{TODAY} | Daily Ukraine–Russia War Analyst Brief | OUSW Comptroller P/B | UNCLASSIFIED OPEN SOURCE"

SEARCH_QUERIES = [
    f"Ukraine Russia war battlefield update {datetime.date.today().strftime('%B %Y')}",
    f"Ukraine Russia missile drone attack {datetime.date.today().strftime('%B %Y')}",
    f"Ukraine defense articles weapons stockpiles US aid {datetime.date.today().strftime('%B %Y')}",
    "Operation Epic Fury US military Iran ceasefire status 2026",
    "Ukraine war funding appropriations Congress supplemental 2026",
    "Patriot THAAD interceptor stockpile depletion Ukraine Iran war 2026",
    "Russia North Korea China weapons supply Ukraine battlefield 2026",
    "US defense industrial base missile production Patriot THAAD ramp 2026",
    "Ukraine ceasefire negotiations peace talks Russia 2026",
    "Russia nuclear signaling escalation Ukraine 2026",
]

REPORT_PROMPT = f"""You are a senior analyst supporting the Department of War / OUSW Comptroller Program/Budget office.
Today's date is {TODAY}.

Below are web search results from the last 24–48 hours gathered from credible open sources.
Using ONLY information from these search results (do not hallucinate sources), generate the full
Daily Ukraine–Russia War Analyst Brief in the exact format specified below.

SEARCH RESULTS:
{{search_results}}

---

REQUIRED REPORT FORMAT:

Write a professional analyst-grade daily brief in clean HTML for email delivery.
The report must be a ~10-minute read divided into 5 clearly labeled chunks.
Use tables wherever the format calls for them.
Every major claim must include the source name, article title, date, and URL hyperlink.
Clearly distinguish: Confirmed / Medium confidence / Low confidence / Cannot confirm.
Label Russian and Ukrainian official claims as such.
Do not present unverified claims as fact.

REQUIRED STRUCTURE:

== CHUNK 1: SENIOR LEADER SNAPSHOT ==
A. Bottom Line Up Front (3–5 bullets) — each with source, link, confidence
B. Top 5–7 Issues for OUSW Comptroller P/B Analysts — tagged [Funding][Appropriations][Execution][PDA][USAI][Defense Articles][Stockpiles][Replenishment][Congressional RFI][Readiness][Epic Fury / Iran Linkage]
C. Watch Items for Next 7 Days — table with indicator, why it matters, budget/defense article implication, source link
D. Most Likely Congressional RFI Questions Today — 5–10 questions

== CHUNK 2: BATTLEFIELD & MILITARY OPERATIONS ==
- Frontline changes, Russian offensives, Ukrainian advances
- Missile/drone attacks
- Air defense activity
- Ceasefire dynamics
- Nuclear signaling / escalation indicators
For each: Event | Location | Date | Source + Link | Confidence | Significance

== CHUNK 3: DEFENSE ARTICLES, STOCKPILES & DEFENSE INDUSTRIAL BASE ==
- U.S.-provided defense articles status (Patriot, THAAD, NASAMS, HIMARS, GMLRS, ATACMS, 155mm, F-16, etc.)
- Allied/partner contributions
- Stockpile and readiness issues table
- DIB production capacity (Lockheed, Raytheon, BAE, etc.)
For each: System | Status | Ukraine Impact | Readiness Impact | Production/Rebuild timeline | Source + Link | Confidence

== CHUNK 4: FUNDING, BUDGET, APPROPRIATIONS & EPIC FURY LINKAGE ==
- FY2026 NDAA Ukraine provisions
- USAI / PDA / FMF status
- Allied pledges and execution
- New supplemental legislation (if any)
- Epic Fury / Iran–Ukraine-Russia linkage (stockpile competition, drone/missile warfare overlap, Russia-Iran relationship post-Epic Fury, energy effects, strategic bandwidth)
For each funding item: Account | Amount | Status | Comptroller Relevance | Potential RFI | Source + Link | Confidence

== CHUNK 5: DPRK/CHINA/IRAN SUPPLY | CONGRESSIONAL RFI PREP | ANALYST ASSESSMENT ==
- Russia's external weapons networks (North Korea, China, Iran, Belarus)
- Sanctions effectiveness
- Congressional RFI readiness table: Likely Question | Short Answer | Source Links | Confidence
- Delta from Prior Report (note: list key changes if a prior report exists; otherwise note inaugural report)
- Analyst Assessment: Confirmed Facts | Analyst Judgment | Cannot Confirm | What Matters Most | Watch Items | Budget Implications

End with a Confidence Matrix table:
Claim/Topic | Confidence (HIGH/MEDIUM/LOW/Cannot confirm) | Reason

---

WRITING STYLE REQUIREMENTS:
- Direct, executive-level language
- No political commentary
- No speculation without evidence
- No vague "many reports say" — cite specific sources
- Short paragraphs; bullet points; tables
- Every major claim hyperlinked to source
- HTML format suitable for email (use inline styles; no external CSS)
- Color scheme: #003366 for headers; #c00000 for section titles
"""

BRIEF_SYSTEM_PROMPT = (
    "You are a senior defense analyst generating daily classified-equivalent open-source "
    "intelligence briefs for Department of War / OUSW Comptroller Program/Budget analysts. "
    "Write with precision, brevity, and analytical rigor. Every claim must be sourced. "
    "Label unverified claims. Never present speculation as fact."
)


# ---------------------------------------------------------------------------
# Step 1: Gather search results via Tavily
# ---------------------------------------------------------------------------

def gather_search_results(api_key: str) -> str:
    client = TavilyClient(api_key=api_key)
    all_results = []

    for query in SEARCH_QUERIES:
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_answer=True,
                include_raw_content=False,
            )
            results_for_query = {
                "query": query,
                "answer": response.get("answer", ""),
                "results": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "published_date": r.get("published_date", ""),
                        "content": r.get("content", "")[:800],  # cap per result
                    }
                    for r in response.get("results", [])
                ],
            }
            all_results.append(results_for_query)
        except Exception as exc:
            all_results.append({"query": query, "error": str(exc)})

    return json.dumps(all_results, indent=2)


# ---------------------------------------------------------------------------
# Step 2: Generate report via Claude API
# ---------------------------------------------------------------------------

def generate_report(search_results: str, anthropic_api_key: str) -> str:
    client = anthropic.Anthropic(api_key=anthropic_api_key)

    user_message = REPORT_PROMPT.replace("{search_results}", search_results)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        system=BRIEF_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text


# ---------------------------------------------------------------------------
# Step 3: Send report via Gmail SMTP
# ---------------------------------------------------------------------------

def send_email(html_body: str, sender: str, app_password: str, recipient: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"] = sender
    msg["To"] = recipient

    # Plain-text fallback
    plain_text = (
        f"Daily Ukraine–Russia War Analyst Brief — {TODAY}\n\n"
        "Please view this email in an HTML-capable client.\n\n"
        "UNCLASSIFIED // FOR OFFICIAL USE ONLY — OPEN SOURCE ONLY"
    )

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Brief sent to {recipient}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]
    tavily_api_key = os.environ["TAVILY_API_KEY"]
    gmail_sender = os.environ["GMAIL_SENDER"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient_email = os.environ["RECIPIENT_EMAIL"]

    print(f"[{TODAY}] Gathering search results...")
    search_results = gather_search_results(tavily_api_key)
    print(f"Collected results for {len(SEARCH_QUERIES)} queries.")

    print("Generating analyst brief via Claude API...")
    report_html = generate_report(search_results, anthropic_api_key)
    print(f"Report generated ({len(report_html):,} characters).")

    print("Sending email...")
    send_email(report_html, gmail_sender, gmail_app_password, recipient_email)
    print("Done.")


if __name__ == "__main__":
    main()
