import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

LOG_FILE = "engagement_log.json"


def _load_log() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_log(entries: list):
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(entries, f, indent=2)
    except IOError as e:
        logger.error(f"Failed to save engagement log: {e}")


def log_event(event_type: str, data: dict):
    """
    Log an engagement event.

    event_type: "mention_reply" | "scheduled_post" | "engagement_check"
    data: arbitrary dict of relevant fields
    """
    entries = _load_log()
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "type": event_type,
        **data,
    }
    entries.append(entry)
    _save_log(entries)
    logger.info(f"Logged [{event_type}]: {data}")


def log_mention_reply(username: str, tweet_id: str, reply_text: str):
    log_event("mention_reply", {
        "username": username,
        "tweet_id": tweet_id,
        "reply": reply_text,
    })


def log_scheduled_post(tweet_id: str, post_text: str):
    log_event("scheduled_post", {
        "tweet_id": tweet_id,
        "text": post_text,
    })


def log_engagement_check(tweet_id: str, likes: int, retweets: int, replies: int, impressions: int):
    log_event("engagement_check", {
        "tweet_id": tweet_id,
        "likes": likes,
        "retweets": retweets,
        "replies": replies,
        "impressions": impressions,
    })


def get_summary() -> dict:
    """Returns a quick summary of logged activity."""
    entries = _load_log()
    summary = {
        "total_events": len(entries),
        "mention_replies": 0,
        "scheduled_posts": 0,
        "engagement_checks": 0,
        "total_likes": 0,
        "total_retweets": 0,
        "total_replies_received": 0,
        "total_impressions": 0,
    }
    for e in entries:
        t = e.get("type")
        if t == "mention_reply":
            summary["mention_replies"] += 1
        elif t == "scheduled_post":
            summary["scheduled_posts"] += 1
        elif t == "engagement_check":
            summary["engagement_checks"] += 1
            summary["total_likes"] += e.get("likes", 0)
            summary["total_retweets"] += e.get("retweets", 0)
            summary["total_replies_received"] += e.get("replies", 0)
            summary["total_impressions"] += e.get("impressions", 0)
    return summary
