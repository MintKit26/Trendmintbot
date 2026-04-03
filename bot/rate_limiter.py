import time
import logging
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Sliding window rate limiter.

    Tracks action counts over a rolling time window and blocks
    if a limit is exceeded, protecting against X API bans.
    """

    def __init__(self, max_actions: int, window_seconds: int, name: str = "default"):
        self.max_actions = max_actions
        self.window_seconds = window_seconds
        self.name = name
        self._timestamps: deque = deque()

    def _purge_old(self):
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_seconds)
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

    def is_allowed(self) -> bool:
        self._purge_old()
        return len(self._timestamps) < self.max_actions

    def record(self):
        self._timestamps.append(datetime.utcnow())

    def wait_if_needed(self):
        """Block until an action is allowed, then record it."""
        while not self.is_allowed():
            oldest = self._timestamps[0]
            wait_until = oldest + timedelta(seconds=self.window_seconds)
            wait_secs = (wait_until - datetime.utcnow()).total_seconds()
            if wait_secs > 0:
                logger.warning(
                    f"[RateLimiter:{self.name}] Limit reached "
                    f"({self.max_actions}/{self.window_seconds}s). "
                    f"Waiting {wait_secs:.1f}s..."
                )
                time.sleep(wait_secs + 1)
            self._purge_old()
        self.record()

    def status(self) -> dict:
        self._purge_old()
        return {
            "limiter": self.name,
            "used": len(self._timestamps),
            "max": self.max_actions,
            "window_seconds": self.window_seconds,
            "remaining": self.max_actions - len(self._timestamps),
        }


# Pre-configured limiters matching X API Basic tier ($100/mo)
# Basic tier: 3,000 tweets/month write, 10,000 reads/month

# Tweets (posts + replies): ~100/day is a safe daily budget within 3,000/month
tweet_limiter = RateLimiter(max_actions=100, window_seconds=86400, name="tweets")

# Mention polls: 1 per minute is safe and responsive
mention_limiter = RateLimiter(max_actions=1, window_seconds=60, name="mention_polls")

# Engagement reads: 15 per 15 min — conservative within Basic tier read allowance
read_limiter = RateLimiter(max_actions=15, window_seconds=900, name="reads")
