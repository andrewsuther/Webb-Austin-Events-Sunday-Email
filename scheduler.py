#!/usr/bin/env python3
"""
Webb Events Email Scheduler
Runs the emailer every Sunday at 9:00 AM
"""

import schedule
import time
import logging
from datetime import datetime
from webb_events_emailer import WebbEventsEmailer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

def job():
    """The scheduled job to run."""
    logging.info("Scheduled job triggered - Running Webb Events Emailer")
    try:
        emailer = WebbEventsEmailer()
        emailer.run()
    except Exception as e:
        logging.error(f"Error in scheduled job: {e}")

def main():
    """Main scheduler loop."""
    # Schedule the job for every Sunday at 9:00 AM
    schedule.every().sunday.at("09:00").do(job)

    logging.info("Webb Events Email Scheduler Started")
    logging.info("Scheduled to run every Sunday at 9:00 AM")
    logging.info(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Show next run time
    next_run = schedule.next_run()
    if next_run:
        logging.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")

if __name__ == "__main__":
    main()
