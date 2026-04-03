import time
import logging
import os
from datetime import datetime, timedelta

import config
from bot.client import get_client, get_api_v1
from bot.mention_handler import handle_mentions
from bot.scheduler import post_scheduled_content
from bot.engagement_checker import check_engagements, load_posted_ids
from bot.engagement_logger import get_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

LAST_POST_FILE = "last_post_time.txt"


def should_post() -> bool:
    interval_hours = config.POST_INTERVAL_HOURS
    if not os.path.exists(LAST_POST_FILE):
        return True
    try:
        with open(LAST_POST_FILE) as f:
            last = datetime.fromisoformat(f.read().strip())
        elapsed = (datetime.utcnow() - last).total_seconds() / 3600
        return elapsed >= interval_hours
    except (ValueError, IOError):
        return True


def record_post_time():
    with open(LAST_POST_FILE, "w") as f:
        f.write(datetime.utcnow().isoformat())


def main():
    config.validate()
    client = get_client()
    api_v1 = get_api_v1()

    me = client.get_me()
    bot_user_id = me.data.id
    logger.info(f"Running as @{me.data.username}")

    # 1. Handle any new mentions
    handle_mentions(client, bot_user_id)

    # 2. Post scheduled content if interval has elapsed
    if should_post():
        logger.info("Interval elapsed — posting scheduled content.")
        post_scheduled_content(client, api_v1)
        record_post_time()
    else:
        logger.info("Not time to post yet — skipping.")

    # 3. Check engagements on tracked tweets
    if load_posted_ids():
        check_engagements(client)

    # 4. Log summary
    summary = get_summary()
    logger.info(f"Session summary: {summary}")


if __name__ == "__main__":
    main()
