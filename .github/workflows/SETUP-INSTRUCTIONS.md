# Daily Brief Automation — Setup Instructions

## What This Does
Generates and emails the **Daily Ukraine–Russia War Analyst Brief** every morning at **5:00 AM Eastern Time** (automatically adjusts for EST/EDT).

## One-Time Setup Required

### Step 1 — Add GitHub Secrets

Go to: `https://github.com/sancho1123/Test1/settings/secrets/actions`

Add these three secrets:

| Secret Name | Value | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | From console.anthropic.com |
| `GMAIL_SENDER_ADDRESS` | ericjsanchez23@gmail.com | Your Gmail address (the sender) |
| `GMAIL_APP_PASSWORD` | 16-character app password | See Step 2 below |

### Step 2 — Create Gmail App Password

> Required because GitHub Actions uses SMTP, not OAuth.

1. Go to your Google Account: https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already on
3. Go to **App Passwords**: https://myaccount.google.com/apppasswords
4. Select app: **Mail** | Device: **Other (custom name)** → type "GitHub Actions"
5. Click **Generate** — copy the 16-character password
6. Paste it as the `GMAIL_APP_PASSWORD` secret in Step 1

### Step 3 — Verify the Workflow Runs

After adding secrets, trigger a test run manually:
1. Go to: `https://github.com/sancho1123/Test1/actions`
2. Click **Daily Ukraine–Russia War Analyst Brief**
3. Click **Run workflow** → **Run workflow**
4. Check your inbox at ericjsanchez23@gmail.com within ~10 minutes

## Schedule
- **Automatic**: Every day at 5:00 AM ET (cron: `0 10 * * *` UTC)
- **Manual**: Use "Run workflow" button in GitHub Actions anytime

## Output
- Report emailed to: ericjsanchez23@gmail.com
- Report also saved to: `reports/YYYY-MM-DD_Ukraine-Russia_War_Daily_Analyst_Brief_OUSW-PB.md`
- Report committed to the `main` branch automatically

## Troubleshooting

| Problem | Fix |
|---|---|
| Email not received | Check spam folder; verify GMAIL_APP_PASSWORD is correct |
| Workflow fails | Check ANTHROPIC_API_KEY is valid at console.anthropic.com |
| Report empty | Check GitHub Actions logs for Claude output |
| Wrong time | Workflow uses UTC 10:00 = 6:00 AM ET in winter (EST), 10:00 AM UTC = 6:00 AM EDT in summer. Adjust cron if needed: `0 9 * * *` for 5 AM EDT |
