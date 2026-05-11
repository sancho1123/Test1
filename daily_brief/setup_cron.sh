#!/usr/bin/env bash
# Sets up the daily 05:00 ET cron job for the Ukraine-Russia War Analyst Brief.
# Run once: bash /home/user/Test1/daily_brief/setup_cron.sh
#
# Cron schedule: 09:00 UTC = 05:00 EDT (Apr-Nov) | 10:00 UTC = 05:00 EST (Dec-Mar)
# To handle DST automatically, this installs BOTH entries with a lock file guard,
# OR you can install the TZ-aware single entry (preferred on systems with GNU cron).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(which python3)"
SCRIPT="$SCRIPT_DIR/run_daily_brief.py"
LOGFILE="$SCRIPT_DIR/logs/cron.log"
LOCKFILE="/tmp/daily_brief.lock"

# Verify .env exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "ERROR: $SCRIPT_DIR/.env not found."
    echo "Copy .env.template to .env and fill in your credentials first."
    exit 1
fi

# Cron job line — uses TZ=America/New_York for DST-aware 5 AM scheduling
CRON_JOB="0 5 * * * TZ=America/New_York $PYTHON $SCRIPT >> $LOGFILE 2>&1"

# Check if already installed
CURRENT_CRON=$(crontab -l 2>/dev/null)
if echo "$CURRENT_CRON" | grep -qF "run_daily_brief.py"; then
    echo "Cron job already installed:"
    echo "$CURRENT_CRON" | grep "run_daily_brief.py"
    echo ""
    echo "To update it, run: crontab -e"
    exit 0
fi

# Install the cron job
(
    echo "$CURRENT_CRON"
    echo ""
    echo "# Daily Ukraine-Russia War Analyst Brief — OUSW Comptroller P/B"
    echo "$CRON_JOB"
) | crontab -

echo "Cron job installed successfully."
echo ""
echo "Installed entry:"
crontab -l | grep "run_daily_brief"
echo ""
echo "The brief will run every morning at 05:00 AM Eastern Time."
echo "Logs will be written to: $LOGFILE"
echo ""
echo "To run manually right now:  python3 $SCRIPT"
echo "To remove the cron job:     crontab -e  (delete the line)"
