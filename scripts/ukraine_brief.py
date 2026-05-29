#!/usr/bin/env python3
"""
Daily Ukraine-Russia War Analyst Brief Generator
Department of War / OUSW Comptroller Program/Budget Office
Scheduled via GitHub Actions at ~5:00 AM ET daily.
"""

import os
import sys
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import pytz
import feedparser
import requests
from anthropic import Anthropic

# ─── Configuration ────────────────────────────────────────────────────────────

RECIPIENT_EMAIL   = os.environ.get("RECIPIENT_EMAIL", "ericjsanchez23@gmail.com")
SENDER_EMAIL      = os.environ.get("SENDER_EMAIL", "")
SMTP_PASSWORD     = os.environ.get("SMTP_PASSWORD", "")
SMTP_SERVER       = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT         = int(os.environ.get("SMTP_PORT", "587"))
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OUTPUT_DIR        = os.environ.get("OUTPUT_DIR", "reports")
OVERRIDE_DATE     = os.environ.get("OVERRIDE_DATE", "")
MODEL             = "claude-opus-4-8"

# ─── RSS Feeds ────────────────────────────────────────────────────────────────

RSS_FEEDS = {
    "Reuters":            "https://feeds.reuters.com/Reuters/worldNews",
    "BBC World News":     "https://feeds.bbci.co.uk/news/world/rss.xml",
    "AP Top News":        "https://apnews.com/rss/apf-topnews",
    "Defense News":       "https://www.defensenews.com/rss/",
    "Breaking Defense":   "https://breakingdefense.com/feed/",
    "USNI News":          "https://news.usni.org/feed",
    "War on the Rocks":   "https://warontherocks.com/feed/",
    "Kyiv Independent":   "https://kyivindependent.com/feed/",
    "Atlantic Council":   "https://www.atlanticcouncil.org/feed/",
    "CSIS":               "https://www.csis.org/rss.xml",
    "FPRI":               "https://www.fpri.org/feed/",
    "ISW":                "https://www.understandingwar.org/feeds/reports",
    "Foreign Policy":     "https://foreignpolicy.com/feed/",
    "Politico":           "https://www.politico.com/rss/politics08.xml",
    "NPR World":          "https://feeds.npr.org/1004/rss.xml",
    "Al Jazeera":         "https://www.aljazeera.com/xml/rss/all.xml",
    "VOA News":           "https://www.voanews.com/api/zkkq_y$qpe",
}

FILTER_KEYWORDS = [
    "ukraine", "russia", "ukrainian", "russian", "zelensky", "putin",
    "kyiv", "kremlin", "donbas", "zaporizhzhia", "kherson", "kharkiv",
    "crimea", "donetsk", "luhansk", "nato", "war", "invasion",
    "patriot", "himars", "atacms", "f-16", "air defense", "nasams",
    "drone", "shahed", "missile", "artillery", "javelin", "stinger",
    "defense article", "military aid", "weapon", "stockpile", "ammunition",
    "appropriation", "congressional", "funding", "aid package", "pda", "usai",
    "epic fury", "iran", "middle east", "centcom", "hezbollah", "hamas",
    "north korea", "china", "crink", "sanctions", "defense industrial",
    "replenishment", "interceptor", "thaad", "gmlrs", "bradley", "abrams",
    "ceasefire", "peace talks", "negotiations", "oreshnik",
]

# ─── Claude Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior defense analyst supporting the Department of War / OUSW Comptroller Program/Budget Office. Generate a daily analyst-grade brief on the Ukraine-Russia War.

TARGET AUDIENCE: OUSW Comptroller P/B analysts who respond to Congressional RFIs, track defense articles/stockpiles, monitor appropriations and budget execution, and assess cross-theater effects involving Operation Epic Fury / Iran.

WRITING STANDARDS:
- Direct, concise government analyst prose — no sensational language, no political commentary
- Every major claim must cite a source name and URL
- Clearly label: Confirmed | Likely | Claimed but unverified | Cannot confirm
- Russian and Ukrainian official claims labeled as such
- If a claim cannot be confirmed, state: "I cannot confirm this"
- Target: ~2500–3000 words (~10-minute read). Break into 5 logical chunks if needed.
- No vague statements like "many reports say" — list the specific sources

REQUIRED STRUCTURE — produce exactly this:

# Daily Ukraine–Russia War Analyst Brief
## Defense Articles | Stockpiles | Budget | Congressional RFI | Operation Epic Fury Cross-Theater Impacts
### [DATE] | OUSW Comptroller Program/Budget Office | UNCLASSIFIED // OPEN SOURCE

---

## PART I — SENIOR LEADER SNAPSHOT

### A. BOTTOM LINE UP FRONT
[3–5 bullets. Each: What changed + Why it matters + Source name + URL + Confidence]

### B. TOP ISSUES FOR OUSW COMPTROLLER P/B
[5–7 tagged bullets. Each: [Tag] What happened | Why it matters | Likely congressional question]
Tags to use: [Funding] [Appropriations] [Execution] [PDA] [USAI] [Defense Articles] [Stockpiles] [Replenishment] [Congressional RFI] [Readiness] [Epic Fury/Iran Linkage] [DIB]

### C. WATCH ITEMS — NEXT 7 DAYS
[5 items. Each: Indicator | Why it matters | Budget/congressional implication | Source URL if available]

### D. MOST LIKELY CONGRESSIONAL RFI QUESTIONS TODAY
[5–8 questions]

---

## PART II — ANALYST ANNEX

### 1. EXECUTIVE SUMMARY
[7–10 tagged bullets. Each: [Tag] One-sentence summary | Why it matters | Source | URL | Confidence]

### 2. BATTLEFIELD AND MILITARY OPERATIONS
[Frontline changes, major attacks, Russian/Ukrainian posture, air defense activity, ceasefire status]
[For each event: Event | Location | Date | Source | URL | Confidence | Significance]

### 3. DEFENSE ARTICLES, WEAPONS, AND STOCKPILES [MANDATORY]
[A. U.S.-Provided Defense Articles | B. Allied/Partner Support | C. Stockpile and Readiness Issues]
[For each item: Article | Status | Source | URL | Confidence | Ukraine impact | U.S. readiness impact | Congressional interest?]

### 4. FUNDING, BUDGET, APPROPRIATIONS, AND CONGRESSIONAL RELEVANCE
[New aid, PDA, USAI, supplementals, reprogramming, congressional oversight]
[Table format: Funding item | Account | Amount | Source | URL | Confidence | Comptroller relevance | Potential RFI]

### 5. OPERATION EPIC FURY / IRAN — UKRAINE LINKAGE [MANDATORY]
[A. Weapons/Stockpile Competition | B. Drone/Missile Linkage | C. Russia-Iran Relationship | D. Energy/Economic | E. Strategic Bandwidth]
[If no confirmed linkage exists in a sub-area, state: "I cannot confirm this linkage in today's reporting."]

### 6. RUSSIA'S EXTERNAL MILITARY SUPPORT
[Iran, North Korea, China, Belarus — weapons, materials, financial networks]

### 7. ESCALATION RISKS AND WARNING INDICATORS
[Risk | Low/Medium/High | Source | URL | Confidence | Implication]

### 8. CONGRESSIONAL RFI READINESS TABLE
| Likely RFI Question | Short Answer | Source Link(s) | Confidence |
|---|---|---|---|

### 9. DELTA FROM PRIOR REPORT
[New developments | Changed assessments | Escalated/de-escalated risks | New funding/stockpile issues]

### 10. ANALYST ASSESSMENT
Sections: What Matters Most Today | Watch Next 7 Days | Confirmed Facts | Analyst Judgment | Cannot Confirm

### 11. SOURCE LOG [MANDATORY — every source must appear here]
| # | Source | Title | Date | URL | Topic | Confidence | Notes |
|---|---|---|---|---|---|---|---|

### 12. CONFIDENCE MATRIX
| Claim/Topic | Confidence | Reason |
|---|---|---|

---
UNCLASSIFIED // OPEN SOURCE ONLY"""


# ─── RSS Fetcher ──────────────────────────────────────────────────────────────

def fetch_rss_articles(max_age_hours: int = 48, max_per_feed: int = 8) -> list:
    articles = []
    utc = pytz.UTC
    cutoff = datetime.datetime.now(utc) - datetime.timedelta(hours=max_age_hours)

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(
                feed_url,
                request_headers={"User-Agent": "OUSW-PB-AnalystBot/1.0"}
            )
            count = 0
            for entry in feed.entries:
                if count >= max_per_feed:
                    break

                pub_date = None
                for field in ("published_parsed", "updated_parsed"):
                    raw = getattr(entry, field, None)
                    if raw:
                        try:
                            pub_date = datetime.datetime(*raw[:6], tzinfo=utc)
                        except Exception:
                            pass
                        break

                if pub_date and pub_date < cutoff:
                    continue

                title   = entry.get("title", "")
                summary = entry.get("summary", "")
                text    = (title + " " + summary).lower()

                if any(kw in text for kw in FILTER_KEYWORDS):
                    articles.append({
                        "source":  source_name,
                        "title":   title,
                        "url":     entry.get("link", ""),
                        "date":    str(pub_date)[:10] if pub_date else "Unknown",
                        "summary": summary[:600],
                    })
                    count += 1

        except Exception as exc:
            print(f"[RSS] {source_name}: {exc}", file=sys.stderr)

    return articles


# ─── Report Generator ─────────────────────────────────────────────────────────

def generate_report(articles: list, report_date: str) -> str:
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    header = (
        f"# SOURCE ARTICLES — Last 24–48 Hours (retrieved {report_date})\n\n"
        f"Total relevant articles: {len(articles)}\n\n"
    )
    body = ""
    for i, art in enumerate(articles[:100], 1):
        body += (
            f"**[{i}] {art['source']}**\n"
            f"Title: {art['title']}\n"
            f"Date:  {art['date']}\n"
            f"URL:   {art['url']}\n"
            f"Summary: {art['summary']}\n\n"
        )
    if not articles:
        body = (
            "No articles retrieved from RSS feeds. "
            "Generate the report from general knowledge; label all claims 'Cannot confirm from today's sources'.\n"
        )

    user_message = (
        header + body +
        "---\n\n"
        f"Generate the Daily Ukraine–Russia War Analyst Brief for **{report_date}**.\n\n"
        "Use the articles above as primary sources. For information not in the articles, "
        "draw on recent general knowledge but explicitly label as 'Cannot confirm from today's sources'.\n\n"
        "Remember: target ~2500–3000 words, structured for a 10-minute read by senior government analysts. "
        f"File name: `{report_date}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB`"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


# ─── File Saver ───────────────────────────────────────────────────────────────

def save_report(text: str, report_date: str) -> tuple:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base = f"{report_date}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB"

    md_path   = os.path.join(OUTPUT_DIR, base + ".md")
    html_path = os.path.join(OUTPUT_DIR, base + ".html")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text)

    try:
        import markdown as md_lib
        html_body = md_lib.markdown(text, extensions=["tables", "fenced_code"])
    except ImportError:
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_body = f"<pre>{escaped}</pre>"

    html_full = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<title>Ukraine–Russia War Analyst Brief {report_date}</title>
<style>
  body {{ font-family: Arial, sans-serif; font-size: 13px; max-width: 960px; margin: auto; padding: 20px; color: #222; }}
  h1 {{ color: #1a3c6e; font-size: 18px; margin-bottom: 4px; }}
  h2 {{ color: #1a3c6e; font-size: 15px; border-bottom: 2px solid #1a3c6e; padding-bottom: 4px; margin-top: 24px; }}
  h3 {{ color: #2c5f9e; font-size: 13px; margin-top: 18px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 12px; }}
  th, td {{ border: 1px solid #aaa; padding: 5px 8px; text-align: left; }}
  th {{ background-color: #1a3c6e; color: #fff; }}
  tr:nth-child(even) {{ background-color: #f0f4f8; }}
  .banner {{ background: #1a3c6e; color: #fff; padding: 8px 16px; font-size: 12px; font-weight: bold; margin-bottom: 20px; }}
  .footer {{ font-size: 10px; color: #888; border-top: 1px solid #ccc; padding-top: 8px; margin-top: 30px; }}
  a {{ color: #1a3c6e; }}
  blockquote {{ border-left: 3px solid #ccc; margin-left: 0; padding-left: 12px; color: #555; }}
</style>
</head><body>
<div class="banner">
  UNCLASSIFIED // OPEN SOURCE ONLY &nbsp;|&nbsp;
  Daily Ukraine–Russia War Analyst Brief &nbsp;|&nbsp;
  OUSW Comptroller Program/Budget Office &nbsp;|&nbsp;
  {report_date}
</div>
{html_body}
<div class="footer">
  UNCLASSIFIED // OPEN SOURCE ONLY &nbsp;|&nbsp;
  Generated by OUSW P/B Daily Brief Automation &nbsp;|&nbsp;
  All sources are publicly available open-source information only.
</div>
</body></html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_full)

    return md_path, html_path


# ─── Email Sender ─────────────────────────────────────────────────────────────

def send_email(report_text: str, md_path: str, html_path: str, report_date: str) -> None:
    if not SMTP_PASSWORD or not SENDER_EMAIL:
        print("[Email] Skipping — SENDER_EMAIL or SMTP_PASSWORD not set.", file=sys.stderr)
        return

    subject = (
        f"[OUSW P/B] Daily Ukraine–Russia War Analyst Brief — {report_date}"
        " | Defense Articles | Stockpiles | Budget | Epic Fury"
    )

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(report_text, "plain", "utf-8"))
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            alt.attach(MIMEText(f.read(), "html", "utf-8"))
    msg.attach(alt)

    if os.path.exists(md_path):
        with open(md_path, "rb") as f:
            att = MIMEApplication(f.read(), _subtype="octet-stream")
            att.add_header(
                "Content-Disposition", "attachment",
                filename=os.path.basename(md_path)
            )
            msg.attach(att)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)

    print(f"[Email] Sent to {RECIPIENT_EMAIL}", file=sys.stderr)


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main() -> None:
    et = pytz.timezone("America/New_York")
    report_date = OVERRIDE_DATE.strip() if OVERRIDE_DATE.strip() else datetime.datetime.now(et).strftime("%Y-%m-%d")

    print(f"[Brief] Generating Ukraine–Russia War Analyst Brief for {report_date} …")

    print("[Brief] Fetching RSS feeds …")
    articles = fetch_rss_articles(max_age_hours=48)
    print(f"[Brief] {len(articles)} relevant articles found")

    print("[Brief] Calling Claude API …")
    report_text = generate_report(articles, report_date)

    print("[Brief] Saving report files …")
    md_path, html_path = save_report(report_text, report_date)
    print(f"[Brief] Saved: {md_path}")

    print("[Brief] Emailing report …")
    send_email(report_text, md_path, html_path, report_date)

    print("[Brief] Done.")
    sys.exit(0)


if __name__ == "__main__":
    main()
