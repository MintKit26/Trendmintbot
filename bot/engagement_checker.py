import tweepy
import logging
import json
import os
from bot.engagement_logger import log_engagement_check
from bot.rate_limiter import read_limiter

logger = logging.getLogger(__name__)

POSTED_IDS_FILE = "posted_tweet_ids.json"


def load_posted_ids() -> list:
    if not os.path.exists(POSTED_IDS_FILE):
        return []
    try:
        with open(POSTED_IDS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_posted_id(tweet_id: str):
    ids = load_posted_ids()
    if tweet_id not in ids:
        ids.append(tweet_id)
        # Keep last 100 only
        ids = ids[-100:]
        with open(POSTED_IDS_FILE, "w") as f:
            json.dump(ids, f, indent=2)


def check_engagements(client: tweepy.Client):
    """
    Fetch public metrics for all tracked tweet IDs and log them.
    Only checks the 10 most recent to stay within rate limits.
    """
    tweet_ids = load_posted_ids()
    if not tweet_ids:
        logger.info("No tracked tweet IDs yet.")
        return

    # Check latest 10 only
    to_check = tweet_ids[-10:]

    for tweet_id in to_check:
        read_limiter.wait_if_needed()
        try:
            response = client.get_tweet(
                id=tweet_id,
                tweet_fields=["public_metrics"],
            )
            if not response.data:
                continue

            metrics = response.data.public_metrics or {}
            log_engagement_check(
                tweet_id=tweet_id,
                likes=metrics.get("like_count", 0),
                retweets=metrics.get("retweet_count", 0),
                replies=metrics.get("reply_count", 0),
                impressions=metrics.get("impression_count", 0),
            )
        except tweepy.TweepyException as e:
            logger.error(f"Failed to fetch metrics for tweet {tweet_id}: {e}")
