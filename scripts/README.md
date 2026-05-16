# Daily Ukraine–Russia War Analyst Brief — Automation Scripts

## Overview

These scripts power the daily automated analyst brief for OUSW Comptroller Program/Budget analysts. The GitHub Actions workflow runs every morning at 5:00 AM Eastern Time.

## Files

| File | Purpose |
|------|---------|
| `generate_brief.py` | Calls Claude API (claude-opus-4-7) to research and generate the daily brief |
| `send_email.py` | Sends the generated brief to the recipient via Gmail SMTP |

## GitHub Secrets Required

Configure these in your GitHub repository under **Settings → Secrets and variables → Actions**:

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (from console.anthropic.com) |
| `GMAIL_USER` | Gmail address used to send the report (e.g., yourname@gmail.com) |
| `GMAIL_APP_PASSWORD` | Gmail App Password (NOT your regular password). Create at myaccount.google.com/apppasswords |

## Generating App Password for Gmail

1. Go to your Google Account → Security → 2-Step Verification (must be enabled)
2. Go to **App passwords** (myaccount.google.com/apppasswords)
3. Create a new app password for "Mail" / "Other"
4. Copy the 16-character password into the `GMAIL_APP_PASSWORD` secret

## Manual Trigger

You can trigger the workflow manually from GitHub Actions → **Daily Ukraine–Russia War Analyst Brief** → **Run workflow**.

## Output

- `reports/latest_brief.md` — The most recent brief (overwritten each day)
- `reports/YYYY-MM-DD_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md` — Dated archive

## Schedule

The GitHub Actions cron is set to `0 9 * * *` (09:00 UTC = 5:00 AM EDT during Daylight Saving Time, Mar–Nov).

For Eastern Standard Time (Nov–Mar), update to `0 10 * * *` in `.github/workflows/daily-ukraine-brief.yml`.
