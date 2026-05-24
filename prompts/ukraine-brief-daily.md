# Daily Ukraine–Russia War Analyst Brief
## Prompt for Claude Code Automation
## Target Audience: OUSW / Comptroller Program-Budget Analysts
## Recipient: ericjsanchez23@gmail.com

---

## INSTRUCTIONS FOR CLAUDE

You are generating a daily analyst-grade intelligence brief on the Ukraine–Russia War for Department of War / OUSW Comptroller Program/Budget office analysts. Today's report date is {TODAY}.

### STEP 1 — RESEARCH (use WebSearch for ALL topics below)

Search for developments from the **last 24–48 hours** on EACH of the following topics:

1. `Ukraine Russia war latest news {TODAY_MONTH} {TODAY_YEAR} battlefield frontline`
2. `Ukraine Russia ceasefire peace talks {TODAY_MONTH} {TODAY_YEAR}`
3. `Russia drone missile attack Ukraine {TODAY_MONTH} {TODAY_YEAR}`
4. `Ukraine defense articles Patriot HIMARS air defense stockpile {TODAY_YEAR}`
5. `Operation Epic Fury aftermath Iran ceasefire {TODAY_MONTH} {TODAY_YEAR}`
6. `US munitions stockpile depletion readiness Patriot interceptor {TODAY_YEAR}`
7. `Ukraine aid funding congressional appropriations PDA USAI {TODAY_YEAR}`
8. `Russia North Korea DPRK troops weapons Ukraine {TODAY_YEAR}`
9. `Russia China weapons sanctions evasion Ukraine {TODAY_YEAR}`
10. `Ukraine war nuclear escalation Russia warning {TODAY_MONTH} {TODAY_YEAR}`
11. `Institute for Study of War Ukraine assessment {TODAY_MONTH} {TODAY_YEAR}`
12. `155mm artillery production US defense industrial base {TODAY_YEAR}`
13. `Ukraine Russia territorial frontline changes {TODAY_MONTH} {TODAY_YEAR}`
14. `US readiness munitions Epic Fury recovery timeline {TODAY_YEAR}`

Use credible sources: ISW, CSIS, RAND, Reuters, AP, BBC, FT, WSJ, NYT, WaPo, Defense News, Breaking Defense, Kyiv Independent, White House, DoW/DoD, State Dept, Congress.gov, NATO.

**SOURCE RULES:**
- Every claim must have a direct web link
- Label claims as: Confirmed / Medium confidence / Low confidence / Cannot confirm
- Label Russian and Ukrainian official claims explicitly
- Do not present unverified claims as fact

---

### STEP 2 — GENERATE THE REPORT

Produce a **10-minute read** formatted in HTML, structured in 5 chunks:

**CHUNK 1 — SENIOR LEADER SNAPSHOT:**
- Bottom Line Up Front (BLUF): 3–5 bullets with source + confidence
- Top Issues for OUSW Comptroller P/B Analysts: 5–7 tagged bullets
  - Tags: [Funding] [Appropriations] [Execution] [PDA] [USAI] [Defense Articles] [Stockpiles] [Replenishment] [Congressional RFI] [Readiness] [Epic Fury / Iran Linkage]

**CHUNK 2 — WATCH ITEMS + RFI PREP:**
- Watch Items for Next 7 Days: 5 items with budget/defense article implications
- Most Likely Congressional RFI Questions Today: 8–10 Q&A pairs in table format

**CHUNK 3 — BATTLEFIELD + DEFENSE ARTICLES:**
- Executive Summary: 7–10 tagged bullets
- Battlefield Status table (Event / Location / Date / Source / Confidence / Significance)
- Defense Articles & Stockpiles tables (U.S. systems, Allied support, Critical shortages)

**CHUNK 4 — EPIC FURY LINKAGE + FUNDING + ADVERSARIES:**
- Operation Epic Fury / Ukraine–Russia Linkage (weapons competition, drone/missile linkage, Russia-Iran post-Epic Fury, energy effects, strategic bandwidth)
- Funding / Budget / Appropriations table (PDA, USAI, supplementals, congressional action)
- Adversary Support Networks table (DPRK, China, Iran, Belarus)

**CHUNK 5 — ESCALATION + ASSESSMENT + SOURCES:**
- Escalation Risks table (Indicator / Risk Level / Source / Confidence / Policy Implication)
- Delta From Prior Report (compare to yesterday's report if available)
- Analyst Assessment (Confirmed Facts / Analyst Judgment / Cannot Confirm)
- Source Log table (#, Source, Title, Date, Link, Topic, Confidence, Notes)
- Confidence Matrix table (Claim / Confidence / Reason)

**REPORT HEADER:**
```
Daily Ukraine–Russia War Analyst Brief
OUSW Comptroller P/B | Defense Articles, Stockpiles, Budget, Congressional RFI, Epic Fury
Report Date: {TODAY} | Report Time: 05:00 ET | Classification: UNCLASSIFIED
File: {TODAY_FILE}_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB
```

**WRITING STYLE:**
- Direct language, short paragraphs, clear bullets, tables where helpful
- Source links under every finding
- No political commentary, no unsupported claims, no sensational wording
- Analyst-grade professional tone

---

### STEP 3 — QUALITY CHECK (before sending)

Verify:
- [ ] Every major claim has a source with a direct web link
- [ ] Unverified claims are labeled
- [ ] Russian and Ukrainian official claims are labeled as claims
- [ ] Senior Leader Snapshot is present
- [ ] Defense articles / stockpile section is present
- [ ] Epic Fury / Ukraine linkage section is present
- [ ] Congressional RFI section is present
- [ ] Source log is present
- [ ] Funding, appropriations, execution, stockpile, and readiness implications identified

---

### STEP 4 — EMAIL THE REPORT

Using the Gmail MCP tool (mcp__Gmail__create_draft), create a draft email:
- **To:** ericjsanchez23@gmail.com
- **Subject:** `{TODAY} | Daily Ukraine–Russia War Analyst Brief | OUSW Comptroller P/B | UNCLASSIFIED`
- **HTML Body:** The full HTML report generated in Step 2

Confirm the draft was created successfully and report the draft ID.

---

### FINAL INSTRUCTION

Before finalizing, verify that every major claim is sourced, clearly labeled, and relevant to analysts supporting Department of War / OUSW Comptroller Program-Budget functions. Prioritize information affecting congressional RFIs, defense articles, appropriations, budget execution, stockpile replenishment, U.S. readiness, Ukraine aid, and cross-theater effects involving Operation Epic Fury / Iran. Every article, report, or official release referenced must include a direct web link. If a claim cannot be confirmed, say "I cannot confirm this" and do not present it as fact.
