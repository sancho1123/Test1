# Daily Ukraine–Russia War Analyst Brief — Setup Guide

## What This Does

A GitHub Action runs every morning at **5:00 AM Eastern Time**, automatically:
1. Researches the latest Ukraine-Russia war news across 14 topic areas
2. Generates a full analyst-grade HTML report (~10-minute read)
3. Creates a Gmail **draft** addressed to `ericjsanchez23@gmail.com`

> **Note:** The action creates a Gmail **draft** (not auto-send). Review and send from your Gmail Drafts folder each morning. Auto-send can be enabled by switching to a Gmail `send` MCP tool if preferred.

---

## Required GitHub Secrets

Go to your repository → **Settings → Secrets and variables → Actions → New repository secret**

Add these four secrets:

| Secret Name | What It Is | How to Get It |
|---|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | [console.anthropic.com](https://console.anthropic.com) |
| `GMAIL_CLIENT_ID` | OAuth 2.0 Client ID | See Gmail OAuth setup below |
| `GMAIL_CLIENT_SECRET` | OAuth 2.0 Client Secret | See Gmail OAuth setup below |
| `GMAIL_OAUTH_REFRESH_TOKEN` | Gmail OAuth Refresh Token | See Gmail OAuth setup below |

---

## Gmail OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use existing)
3. Enable the **Gmail API**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Desktop App**
6. Download the credentials JSON — you'll get `client_id` and `client_secret`
7. Use the OAuth Playground or a local script to exchange for a refresh token with scope:
   - `https://www.googleapis.com/auth/gmail.compose`
8. Add the refresh token as `GMAIL_OAUTH_REFRESH_TOKEN`

---

## Schedule

| Setting | Value |
|---|---|
| Cron (summer EDT) | `0 9 * * *` (09:00 UTC = 05:00 AM EDT) |
| Cron (winter EST) | `0 10 * * *` (10:00 UTC = 05:00 AM EST) |
| Manual trigger | Available via **Actions → Run workflow** |

Update the cron in `.github/workflows/daily-ukraine-brief.yml` each time clocks change.

---

## Manual Test Run

To test immediately without waiting for the schedule:
1. Go to your repo → **Actions**
2. Click **Daily Ukraine–Russia War Analyst Brief**
3. Click **Run workflow** → **Run workflow**

---

## Modifying the Report

Edit `prompts/ukraine-brief-daily.md` to:
- Add or remove research topics
- Change the report format or structure
- Adjust the source priority list
- Change the recipient email

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Draft not appearing in Gmail | Check `GMAIL_OAUTH_REFRESH_TOKEN` is valid; tokens expire if unused >6 months |
| Action fails at research step | Check `ANTHROPIC_API_KEY` is valid and has quota |
| Report missing sections | Check the prompt file at `prompts/ukraine-brief-daily.md` |
| Wrong time zone | Adjust cron schedule in `.github/workflows/daily-ukraine-brief.yml` |
