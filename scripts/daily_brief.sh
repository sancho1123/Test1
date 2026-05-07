#!/usr/bin/env bash
# Daily Ukraine-Russia War Analyst Brief — automated runner
# Runs at 5:00 AM ET (09:00 UTC / 10:00 UTC during EDT)
# Cron entry: 0 9 * * * /home/user/Test1/scripts/daily_brief.sh >> /home/user/Test1/briefs/cron.log 2>&1

set -euo pipefail

CLAUDE_BIN="/opt/node22/bin/claude"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
DATE_TAG="$(TZ='America/New_York' date '+%Y-%m-%d')"
BRIEF_FILE="${REPO_DIR}/briefs/${DATE_TAG}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md"

echo "[$(date)] Starting daily analyst brief for ${DATE_TAG}"

# Run Claude Code in non-interactive mode with the brief-generation prompt.
# Claude will use its WebSearch, WebFetch, and Gmail MCP tools automatically.
"$CLAUDE_BIN" \
  --print \
  --dangerously-skip-permissions \
  --model sonnet \
  --max-budget-usd 5.00 \
  --output-format text \
  "You are generating the Daily Ukraine-Russia War Analyst Brief for OUSW Comptroller Program/Budget analysts.
Today's date: $(TZ='America/New_York' date '+%B %d, %Y').
Reporting window: last 24-48 hours.

TASK:
1. Use WebSearch and WebFetch to research ALL of the following topics from the last 24-48 hours:
   a. Ukraine-Russia War battlefield developments (frontlines, strikes, drone/missile attacks, ceasefire updates)
   b. U.S. and allied defense articles provided/requested/depleted (Patriot, NASAMS, HIMARS, ATACMS, Javelins, F-16 support, etc.)
   c. Stockpile and replenishment status (interceptors, artillery, munitions)
   d. U.S. funding/budget/appropriations for Ukraine (USAI, PDA, FMF, supplementals, NDAA provisions)
   e. Congressional activity (HASC, SASC, House/Senate Appropriations, GAO, CRS)
   f. Operation Epic Fury / Iran war developments and cross-theater impacts (munitions competition, energy prices, Strait of Hormuz)
   g. Russia support networks: China, North Korea, Iran, Belarus (weapons, drones, troops, sanctions evasion)
   h. Defense industrial base and production capacity issues
   i. Escalation risks (nuclear signaling, NATO territory, Belarus, NK troops)

2. Produce a full analyst brief following this structure:
   PART I — SENIOR LEADER SNAPSHOT:
   A. Bottom Line Up Front (3-5 bullets, each with source + link + confidence)
   B. Top Issues for OUSW Comptroller P/B Analysts (5-7 tagged bullets: [Funding][USAI][PDA][Defense Articles][Stockpiles][Replenishment][Congressional RFI][Readiness][Epic Fury/Iran Linkage])
   C. Watch Items for the Next 7 Days (5 items)
   D. Most Likely Congressional RFI Questions Today (5-10 questions)

   PART II — ANALYST ANNEX:
   1. Executive Summary (7-10 bullets with tags, source, link, confidence)
   2. Battlefield and Military Operations (table format)
   3. Defense Articles, Weapons, Stockpiles, and Munitions (tables)
   4. Defense Industrial Base and Production Capacity (table)
   5. Funding, Budget, Appropriations, and Congressional Relevance (table)
   6. Operation Epic Fury / Iran and Ukraine-Russia War Linkage (subsections A-E)
   7. Russia, Iran, China, North Korea, Belarus, Sanctions-Evasion Networks (table)
   8. Escalation Risks and Warning Indicators (table)
   9. Congressional RFI Readiness Section (table)
   10. Delta From Prior Report (compare to previous day)
   11. Analyst Assessment
   12. Required News Article / Source Log (numbered table, ALL sources with working links)
   13. Confidence Matrix (table)

RULES:
- Every claim MUST have a source with a working URL.
- Clearly label confidence: High / Medium / Low / Cannot Confirm.
- Distinguish Confirmed / Claimed / Analyst Judgment.
- Russian and Ukrainian official claims must be labeled as such.
- Do not speculate without evidence.
- If a claim cannot be confirmed, state 'I cannot confirm this.'
- Tag every major item with: [Military][Funding][Defense Articles][Stockpiles][DIB][Replenishment][Readiness][Congressional Interest][Epic Fury/Iran Linkage][Escalation Risk][Sanctions][Energy]

3. After completing the report, create a Gmail draft addressed to ericjsanchez23@gmail.com with:
   - Subject: 'Daily Ukraine-Russia War Analyst Brief — OUSW P/B — ${DATE_TAG}'
   - Body: the complete report in HTML format
   Use the mcp__Gmail__create_draft tool to create this draft.

4. Save the report to: ${BRIEF_FILE}

The report is for OUSW Comptroller Program/Budget analysts. Tone: direct, professional, no political commentary, evidence-based. No unsupported claims. Every source must have a working link." \
> "$BRIEF_FILE" 2>/dev/null || true

echo "[$(date)] Brief generation complete. File: ${BRIEF_FILE}"

# Git: commit the new brief to the repo
cd "$REPO_DIR"
git add "briefs/${DATE_TAG}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md" 2>/dev/null || true
git commit -m "Add daily analyst brief for ${DATE_TAG}" 2>/dev/null || true
git push -u origin claude/kind-brahmagupta-bdPpT 2>/dev/null || true

echo "[$(date)] Done."
