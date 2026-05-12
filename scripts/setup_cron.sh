#!/usr/bin/env bash
# Setup script for local cron-based daily brief delivery.
# Run once on the server that will host the scheduled job.
#
# USAGE:
#   chmod +x setup_cron.sh
#   ./setup_cron.sh
#
# PREREQUISITES:
#   1. Python 3.10+ installed
#   2. pip install anthropic python-dotenv
#   3. Create /home/user/Test1/scripts/.env with:
#        ANTHROPIC_API_KEY=sk-ant-...
#        SMTP_USER=your@gmail.com
#        SMTP_PASSWORD=your-gmail-app-password
#        REPORT_RECIPIENTS=ericjsanchez23@gmail.com
#   4. Enable a Gmail App Password at:
#        https://myaccount.google.com/apppasswords

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LOG_FILE="/var/log/ukraine_brief.log"
CRON_USER="${CRON_USER:-$(whoami)}"

# Ensure log file exists and is writable
sudo touch "$LOG_FILE"
sudo chown "$CRON_USER" "$LOG_FILE"

# Build the cron line:
# Run at 05:00 AM US/Eastern using TZ= prefix (requires GNU cron / cronie >= 1.5.7)
CRON_LINE="TZ=America/New_York 0 5 * * * $PYTHON_BIN $SCRIPT_DIR/ukraine_brief.py >> $LOG_FILE 2>&1"

echo "Installing cron job for user: $CRON_USER"
echo "Cron line: $CRON_LINE"
echo ""

# Add to crontab if not already present
( crontab -l 2>/dev/null | grep -v "ukraine_brief"; echo "$CRON_LINE" ) | crontab -

echo "Cron job installed successfully."
echo ""
echo "To verify, run: crontab -l"
echo "Logs will be written to: $LOG_FILE"
echo ""
echo "NOTE: TZ= prefix requires cronie >= 1.5.7. On older systems, use:"
echo "  sudo timedatectl set-timezone America/New_York"
echo "  Then use: 0 5 * * * $PYTHON_BIN $SCRIPT_DIR/ukraine_brief.py >> $LOG_FILE 2>&1"
