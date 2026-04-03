import tweepy
import config

def get_client() -> tweepy.Client:
    """Returns an authenticated Tweepy v2 client."""
    return tweepy.Client(
        bearer_token=config.BEARER_TOKEN,
        consumer_key=config.API_KEY,
        consumer_secret=config.API_SECRET,
        access_token=config.ACCESS_TOKEN,
        access_token_secret=config.ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )

def get_api_v1() -> tweepy.API:
    """Returns an authenticated Tweepy v1.1 API for media uploads."""
    auth = tweepy.OAuth1UserHandler(
        config.API_KEY,
        config.API_SECRET,
        config.ACCESS_TOKEN,
        config.ACCESS_TOKEN_SECRET,
    )
    return tweepy.API(auth)
