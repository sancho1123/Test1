# Daily Ukraine–Russia War Analyst Brief — Setup Guide

## Required GitHub Secrets

Go to: **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Value | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required. Get from console.anthropic.com |
| `TAVILY_API_KEY` | Your Tavily API key | Required for live web search. Get from app.tavily.com |
| `GMAIL_SENDER_EMAIL` | The Gmail address sending the report | Must be the account that created the App Password |
| `GMAIL_APP_PASSWORD` | Gmail App Password (16 chars, no spaces) | See instructions below |
| `REPORT_RECIPIENT_EMAIL` | ericjsanchez23@gmail.com | The report delivery address |

## Gmail App Password Setup

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** if not already on
3. Go to **Security → How you sign in to Google → App passwords**
4. Create a new App Password: App = "Mail", Device = "Other (Custom name)" → "OUSW Brief Bot"
5. Copy the 16-character password and store it as the `GMAIL_APP_PASSWORD` secret

## Schedule

The workflow runs at **09:00 UTC = 5:00 AM EDT** (summer / April–October).

For winter (November–March, when Eastern switches to EST = UTC-5), update the cron in
`.github/workflows/ukraine-war-daily-brief.yml` from `0 9 * * *` to `0 10 * * *`.

## Manual Trigger

You can run the brief on demand from:
**GitHub → Actions → "Ukraine–Russia War Daily Analyst Brief" → Run workflow**

Optional inputs:
- **Override recipient email** — send to a different address for one-off runs
- **Override report date** — generate a brief for a specific past date (YYYY-MM-DD)

## Artifacts

Every brief is saved as a GitHub Actions artifact (90-day retention):
`ukraine-war-brief-YYYY-MM-DD` containing the `.md` and `.html` versions.

Access via: **Actions → select the run → Artifacts section**

## Cost Estimate

- Claude API (claude-opus-4-8): ~$0.04–$0.08 per report
- Tavily API: ~$0.01–$0.05 per report (5 searches × up to 5 results each)
- Total: under $0.15/day (~$4.50/month)
