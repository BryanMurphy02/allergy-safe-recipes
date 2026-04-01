"""
scheduler.py

Runs main.run_scraper() on a repeating interval defined by
SCRAPE_INTERVAL_HOURS in the .env file.

This keeps the scraper container alive and re-triggers the
full scrape pipeline on schedule, rather than running once
and exiting. Docker will restart the container if it crashes.

Usage:
    python scheduler.py

The container entrypoint in the Dockerfile points here,
not at main.py directly.
"""

import logging
import os
import time

from dotenv import load_dotenv
from main import run_scraper

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    interval_hours = float(os.getenv("SCRAPE_INTERVAL_HOURS", "24"))
    interval_seconds = interval_hours * 3600

    logger.info(f"Scheduler started. Interval: {interval_hours}h")

    while True:
        logger.info("Starting scheduled scrape run...")
        try:
            run_scraper()
        except Exception as e:
            logger.error(f"Scrape run failed with unhandled exception: {e}")

        logger.info(f"Scrape complete. Sleeping for {interval_hours}h...")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()