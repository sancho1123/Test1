# Daily Analyst Brief — Setup Instructions

## What This Does
Generates and emails the **Daily Ukraine–Russia War Analyst Brief** every morning
at **5:00 AM Eastern Time** (10:00 UTC) to `ericjsanchez23@gmail.com`.

---

## One-Time Setup: GitHub Repository Secrets

Go to your repository → **Settings → Secrets and variables → Actions → New repository secret**
and add the following four secrets:

| Secret Name | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) → API Keys |
| `GMAIL_CLIENT_ID` | Google Cloud Console → OAuth 2.0 Client ID |
| `GMAIL_CLIENT_SECRET` | Google Cloud Console → OAuth 2.0 Client Secret |
| `GMAIL_REFRESH_TOKEN` | Run the helper script below once to obtain |

---

## Getting Your Gmail Refresh Token

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use an existing one)
3. Enable the **Gmail API**
4. Create **OAuth 2.0 credentials** (Desktop app type)
5. Download the credentials JSON
6. Run this one-time script locally:

```bash
pip install google-auth-oauthlib
python - <<'EOF'
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/gmail.send']
)
creds = flow.run_local_server(port=0)
print("REFRESH TOKEN:", creds.refresh_token)
EOF
```

7. Copy the printed refresh token and add it as the `GMAIL_REFRESH_TOKEN` secret.

---

## Manual Test Run

After setting up secrets, trigger a test run:

**GitHub Actions tab → "Ukraine–Russia Daily Analyst Brief" → Run workflow**

The report will be:
- Emailed to `ericjsanchez23@gmail.com`
- Saved as a downloadable artifact (retained 90 days) under the Actions run

---

## Adjusting the Schedule

Edit `.github/workflows/ukraine-russia-daily-brief.yml`:
```yaml
- cron: '0 10 * * *'   # 10:00 UTC = 5:00 AM ET (EDT); change to '0 11 * * *' for EST (UTC-5)
```

Note: Eastern Daylight Time (EDT) = UTC−4 → use `0 9 * * *`
Eastern Standard Time (EST) = UTC−5 → use `0 10 * * *`
The workflow currently uses `0 10 * * *` (correct for EST; 1 hour late during EDT).
To always hit 5 AM ET exactly, update the cron seasonally or use `0 9 * * *` year-round
if the server observes DST.
