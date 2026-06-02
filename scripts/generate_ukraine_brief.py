#!/usr/bin/env python3
"""
Daily Ukraine–Russia War Analyst Brief Generator
OUSW Comptroller Program/Budget | Automated via GitHub Actions
Schedule: 5:00 AM ET daily (cron: 0 10 * * *)

Required GitHub Secrets (Settings → Secrets and variables → Actions):
  ANTHROPIC_API_KEY   – https://console.anthropic.com/
  GMAIL_SENDER        – Gmail address used to send the report
  GMAIL_APP_PASSWORD  – Google App Password (NOT your Google account password)
                        Create at: https://myaccount.google.com/apppasswords

Optional env var:
  TARGET_DATE – Override date in YYYY-MM-DD (useful for backfill / manual runs)
"""

import os
import sys
import smtplib
import pytz
import anthropic
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ─── Configuration ──────────────────────────────────────────────────

RECIPIENT_EMAIL = "ericjsanchez23@gmail.com"
REPORTS_DIR     = Path("reports")
MODEL           = "claude-opus-4-8"
MAX_TOKENS      = 16000
MAX_TOOL_ROUNDS = 25

# ─── System prompt ────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a senior defense analyst at the Department of War / OUSW Comptroller Program-Budget office.
Generate daily analyst-grade Ukraine–Russia War briefings for staff who answer congressional RFIs,
support senior leader questions, and track defense articles, appropriations, budget execution,
stockpile replenishment, and cross-theater impacts involving Operation Epic Fury / Iran.

MANDATORY STANDARDS
• Every major claim: source name | article title | date | direct URL
• Confidence: High (official or multiple independent sources) |
               Medium (credible, single source) |
               Low (disputed, partial, or single unverified source) |
               Cannot confirm (insufficient sourcing)
• Russian/Ukrainian official claims MUST be labeled as such.
• Write "I cannot confirm this" for claims lacking reliable sourcing.
• No political commentary. No speculation. Direct, clear, analytical language.
• Source priority:
    U.S. gov official > DoD/NATO official > CRS/GAO > CSIS/RAND/RUSI/ISW/Atlantic Council >
    Reuters/AP/BBC/WSJ/FT/NYT/WaPo/Bloomberg > Defense News/TWZ/USNI/Breaking Defense >
    Kyiv Independent/Ukrinform (label as Ukrainian outlets)
"""

# ─── Date handling ────────────────────────────────────────────────

def get_report_date() -> tuple[str, str]:
    """Return (formatted_date, file_date) in Eastern Time."""
    et = pytz.timezone("America/New_York")
    override = os.environ.get("TARGET_DATE", "").strip()
    if override:
        try:
            dt = datetime.strptime(override, "%Y-%m-%d").replace(tzinfo=et)
        except ValueError:
            dt = datetime.now(et)
    else:
        dt = datetime.now(et)
    return dt.strftime("%B %d, %Y"), dt.strftime("%Y-%m-%d")

# ─── Report prompt ───────────────────────────────────────────────

def build_prompt(formatted_date: str) -> str:
    return f"""Generate the complete Daily Ukraine–Russia War Analyst Brief for {formatted_date}.
Reporting window: last 24–48 hours (background only to explain current developments).

PERFORM WEB SEARCHES on all angles before writing:
1. Ukraine Russia war frontline strikes operations {formatted_date}
2. US Ukraine Patriot HIMARS 155mm NASAMS weapons stockpile 2026
3. US Ukraine aid PDA USAI appropriations congressional 2026
4. Operation Epic Fury Iran cross-theater Patriot interceptor stockpile 2026
5. Russia North Korea China weapons supply sanctions evasion 2026
6. Lockheed Martin PAC-3 MSE Patriot production industrial base 2026
7. Ukraine war escalation nuclear signaling NATO 2026
8. Defense industrial base 155mm artillery ammunition production 2026

══════════════════════════════════════════════════════════════
PART I — SENIOR LEADER SNAPSHOT
══════════════════════════════════════════════════════════════

A. BOTTOM LINE UP FRONT (3–5 bullets)
Each bullet:
  [Tag] Summary. Why it matters.
  Source: [Name], "[Title]," [Date], [URL]
  Confidence: High / Medium / Low

B. TOP ISSUES FOR OUSW COMPTROLLER P/B ANALYSTS (5–7 bullets)
Tag each: [Funding] [PDA] [USAI] [Defense Articles] [Stockpiles] [Replenishment]
          [Congressional RFI] [Readiness] [Appropriations] [Execution] [Epic Fury/Iran Linkage]
Format: What happened | Why it matters | Question Congress will ask

C. WATCH ITEMS — NEXT 7 DAYS (5 items)
Each: Indicator | Why it matters | Budget/defense article implication | Source link

D. MOST LIKELY CONGRESSIONAL RFI QUESTIONS TODAY (5–10)

══════════════════════════════════════════════════════════════
PART II — ANALYST ANNEX
══════════════════════════════════════════════════════════════

1. EXECUTIVE SUMMARY
7–10 bullets: [Tag] Summary. Significance. Source+URL. Confidence.

2. BATTLEFIELD AND MILITARY OPERATIONS
Table per event: Event | Location | Date | Source+URL | Confidence | Significance
Cover: frontline changes, Russian missile/drone strikes, Ukrainian deep strikes,
air defense activity, Black Sea/Crimea, force posture, cyber

3. DEFENSE ARTICLES, WEAPONS, STOCKPILES
A. U.S.-provided: Patriot PAC-3/PAC-2, NASAMS, HIMARS, GMLRS, ATACMS, 155mm,
   F-16, Bradley, counter-UAS/drone systems, EW
B. Allied/partner: NATO PURL mechanism, UK, Germany, France, Poland, Baltics, Nordic
C. Stockpile/readiness: depletion status, multi-theater demand, replenishment delays
D. Per system: System | Status | Source+URL | Confidence | Ukraine impact |
   U.S. readiness impact | Congressional interest | Appropriations implication

4. DEFENSE INDUSTRIAL BASE
Per entity: Company/Agency | System | Production status | Ukraine impact |
U.S. readiness impact | Source+URL | Confidence
Cover: Lockheed PAC-3 MSE ($4.76B contract, 600→2,000/yr ramp to 2030),
Boeing seeker production, 155mm propellant/explosives, drone manufacturing,
rare earth component dependencies

5. FUNDING, BUDGET, APPROPRIATIONS, CONGRESSIONAL RELEVANCE
Table: Funding item | Account/Mechanism | Amount (if sourced) | Source+URL |
Confidence | Comptroller relevance | Potential RFI
Cover: PDA (FY2026 status), USAI execution, NDAA provisions, NATO burden sharing,
GAO/CRS findings, reprogramming or apportionment actions

6. OPERATION EPIC FURY / IRAN — UKRAINE LINKAGE [MANDATORY SECTION]
A. Weapons/stockpile competition: Are both theaters drawing same inventories?
   Supply priority effects? Production timeline effects? Congressional concern?
B. Drone/missile linkage: Shahed-136 cross-use, Geran-2 reciprocal tech, AMD lessons
C. Russia-Iran relationship: Does Epic Fury weaken Iran’s ability to supply Russia?
D. Energy/economic effects: Hormuz risk, oil prices, Russian revenue, European fiscal
E. Strategic bandwidth: Epic Fury effects on U.S. Ukraine attention and force allocation
Label each finding: Confirmed evidence | Credible reporting | Analyst judgment
If no linkage found: "I cannot confirm a direct linkage between Operation Epic Fury
and the Ukraine–Russia War in today’s reporting."

7. RUSSIA / CHINA / DPRK / IRAN — SUPPLY CHAIN AND SANCTIONS EVASION
Per actor: Actor | Assistance type | Scale/scope | Source+URL | Confidence |
Ukraine war impact | Congressional/sanctions relevance

8. ESCALATION RISKS AND WARNING INDICATORS
Per risk: Indicator | Risk (Low/Medium/High) | Source+URL | Confidence |
Why it matters | Policy/budget/defense article implication

9. CONGRESSIONAL RFI READINESS TABLE
| Likely RFI Question | Short Answer | Source URLs | Confidence |
Cover: Patriot inventory, PDA status, Epic Fury linkage, DPRK/China supply,
sanctions effectiveness, DIB capacity, readiness risk, stockpile replenishment timeline

10. DELTA FROM PRIOR REPORT
If first run: "No prior report available for comparison."
Otherwise: new developments, changed assessments, new risks, funding/DIB changes

11. ANALYST ASSESSMENT
• What matters most today
• Watch items (next 7 days)
• Congressional risk
• Budget execution risk
• Defense article and replenishment risk
• U.S. readiness risk
• Most important cross-theater linkage
• Confirmed Facts | Analyst Judgment | Cannot Confirm

12. SOURCE LOG [EVERY SOURCE CITED MUST APPEAR HERE]
| # | Source | Title | Date | URL | Topic | Confidence | Notes |
Notes label: official source / analysis / paywalled / Russian official claim / Ukrainian official claim

13. CONFIDENCE MATRIX
| Claim/Topic | Confidence | Reason |

══════════════════════════════════════════════════════════════
FINAL QUALITY CHECK before submitting:
✓ Every major claim has a direct URL
✓ Russian/Ukrainian official claims labeled as such
✓ All 13 sections present
✓ Epic Fury linkage section complete (or explicit "cannot confirm")
✓ Source log contains every cited source
══════════════════════════════════════════════════════════════"""

# ─── Report generation (Claude API + tool loop) ─────────────────────────

def generate_report(formatted_date: str) -> str:
    """
    Call Claude with the web_search_20250305 tool to produce the daily brief.
    Runs the standard tool-use loop until stop_reason == 'end_turn'.
    web_search_20250305 is a server-side tool: Anthropic executes searches automatically.
    The client loop just acknowledges tool_use blocks and re-submits.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    messages = [{"role": "user", "content": build_prompt(formatted_date)}]
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 25}]

    for round_num in range(1, MAX_TOOL_ROUNDS + 1):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        if resp.stop_reason == "end_turn":
            text = "".join(
                block.text
                for block in resp.content
                if hasattr(block, "text")
            )
            if not text.strip():
                raise RuntimeError("Claude returned empty response on end_turn.")
            return text

        if resp.stop_reason == "tool_use":
            # Append assistant message, pass empty acknowledgment for server-side tool results
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": block.id, "content": ""}
                    for block in resp.content
                    if block.type == "tool_use"
                ],
            })
            print(f"  Search round {round_num}/{MAX_TOOL_ROUNDS}.", flush=True)
        else:
            raise RuntimeError(f"Unexpected stop_reason={resp.stop_reason!r}")

    raise RuntimeError("Exceeded maximum tool rounds without reaching end_turn.")

# ─── Save report to disk ─────────────────────────────────────────────────

def save_report(report: str, file_date: str) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"{file_date}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md"
    path.write_text(report, encoding="utf-8")
    print(f"Report saved: {path}")
    return path

# ─── Email delivery ──────────────────────────────────────────────────────

def send_email(report: str, formatted_date: str) -> None:
    sender   = os.environ.get("GMAIL_SENDER", "").strip()
    password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()

    if not sender or not password:
        print("WARNING: Email credentials not configured — report saved but not emailed.")
        return

    subject = f"Daily Ukraine–Russia War Analyst Brief — {formatted_date} | OUSW P/B"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = sender
    msg["To"]      = RECIPIENT_EMAIL

    # Plain-text part
    msg.attach(MIMEText(report, "plain", "utf-8"))

    # HTML part — monospace with a header block for readability
    escaped = (
        report
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>\n")
    )
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:'Courier New',monospace;font-size:13px;max-width:960px;
             margin:0 auto;padding:20px;color:#1a1a1a;background:#fff">
  <div style="background:#1a1a2e;color:#fff;padding:16px 20px;margin-bottom:24px">
    <h2 style="margin:0;color:#ffd700;font-size:15px;letter-spacing:.5px">
      DAILY UKRAINE–RUSSIA WAR ANALYST BRIEF
    </h2>
    <p style="margin:6px 0 0;color:#bbb;font-size:12px">
      OUSW Comptroller / Program-Budget&nbsp;│&nbsp;{formatted_date}&nbsp;│&nbsp;UNCLASSIFIED
    </p>
  </div>
  <div style="white-space:pre-wrap;line-height:1.65">{escaped}</div>
</body>
</html>"""
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, RECIPIENT_EMAIL, msg.as_string())
        print(f"Report emailed to {RECIPIENT_EMAIL}")
    except Exception as exc:
        print(f"ERROR: Email delivery failed — {exc}", file=sys.stderr)
        raise

# ─── Entry point ────────────────────────────────────────────────────────

def main() -> None:
    formatted_date, file_date = get_report_date()
    print(f"Generating Daily Ukraine–Russia War Analyst Brief for {formatted_date} …")

    report = generate_report(formatted_date)
    save_report(report, file_date)
    send_email(report, formatted_date)

    print("Done.")

if __name__ == "__main__":
    main()
