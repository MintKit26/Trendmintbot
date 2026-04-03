import tweepy
import logging
from bot.ai_generator import generate_reply
from bot.engagement_logger import log_mention_reply
from bot.engagement_checker import save_posted_id
from bot.rate_limiter import mention_limiter, tweet_limiter
from bot.templates import is_collab_request, get_fallback_collab_reply

logger = logging.getLogger(__name__)

_last_seen_id: int | None = None


def load_last_seen_id(filepath: str = "last_seen_id.txt") -> int | None:
    try:
        with open(filepath, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def save_last_seen_id(mention_id: int, filepath: str = "last_seen_id.txt"):
    with open(filepath, "w") as f:
        f.write(str(mention_id))


def handle_mentions(client: tweepy.Client, bot_user_id: str):
    global _last_seen_id

    if _last_seen_id is None:
        _last_seen_id = load_last_seen_id()

    mention_limiter.wait_if_needed()

    try:
        mentions = client.get_users_mentions(
            id=bot_user_id,
            since_id=_last_seen_id,
            tweet_fields=["author_id", "text"],
            expansions=["author_id"],
            user_fields=["username"],
        )
    except tweepy.TweepyException as e:
        logger.error(f"Failed to fetch mentions: {e}")
        return

    if not mentions.data:
        logger.info("No new mentions.")
        return

    users = {u.id: u.username for u in (mentions.includes.get("users") or [])}

    for mention in reversed(mentions.data):  # oldest first
        username = users.get(mention.author_id, "friend")

        # Route collab requests to collab replies
        if is_collab_request(mention.text):
            reply_text = get_fallback_collab_reply(username)
        else:
            reply_text = generate_reply(username, mention.text)

        tweet_limiter.wait_if_needed()
        try:
            response = client.create_tweet(
                text=reply_text, in_reply_to_tweet_id=mention.id
            )
            reply_id = str(response.data["id"])
            save_posted_id(reply_id)
            log_mention_reply(
                username=username,
                tweet_id=str(mention.id),
                reply_text=reply_text,
            )
            logger.info(f"Replied to @{username} (tweet {mention.id})")
        except tweepy.TweepyException as e:
            logger.error(f"Failed to reply to tweet {mention.id}: {e}")

        _last_seen_id = max(_last_seen_id or 0, mention.id)

    save_last_seen_id(_last_seen_id)
