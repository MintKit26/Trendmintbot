import time
import logging
import schedule
import config
from bot.client import get_client
from bot.mention_handler import handle_mentions
from bot.scheduler import post_scheduled_content
from bot.engagement_checker import check_engagements
from bot.engagement_logger import get_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    config.validate()
    client = get_client()

    me = client.get_me()
    bot_user_id = me.data.id
    logger.info(f"Logged in as @{me.data.username} (id: {bot_user_id})")

    # Print engagement summary from previous runs
    summary = get_summary()
    logger.info(f"Engagement summary so far: {summary}")

    # Schedule periodic posts
    schedule.every(config.POST_INTERVAL_HOURS).hours.do(
        post_scheduled_content, client=client
    )

    # Schedule engagement checks every 2 hours
    schedule.every(2).hours.do(check_engagements, client=client)

    logger.info(
        f"Bot started. Polling mentions every {config.MENTION_POLL_INTERVAL}s, "
        f"posting every {config.POST_INTERVAL_HOURS}h, "
        f"checking engagements every 2h."
    )

    while True:
        handle_mentions(client, bot_user_id)
        schedule.run_pending()
        time.sleep(config.MENTION_POLL_INTERVAL)


if __name__ == "__main__":
    main()
