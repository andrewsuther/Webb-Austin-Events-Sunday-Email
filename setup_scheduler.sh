#!/bin/bash
# Setup cron job for Webb Events Emailer (Alternative to Python scheduler)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH=$(which python3)

echo "Setting up Webb Events Emailer cron job..."
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"

# Create cron job that runs every Sunday at 9:00 AM
CRON_JOB="0 9 * * 0 cd $SCRIPT_DIR && $PYTHON_PATH $SCRIPT_DIR/webb_events_emailer.py >> $SCRIPT_DIR/cron.log 2>&1"

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -q "webb_events_emailer.py") && {
    echo "Cron job already exists. Removing old one..."
    crontab -l | grep -v "webb_events_emailer.py" | crontab -
}

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "The emailer will run every Sunday at 9:00 AM"
echo "To view your cron jobs: crontab -l"
echo "To remove the cron job: crontab -e (then delete the line)"
echo "Logs will be written to: $SCRIPT_DIR/cron.log"
