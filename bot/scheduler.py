import tweepy
import logging
import tempfile
import os
import tweepy.errors
from bot.ai_generator import generate_post
from bot.engagement_logger import log_scheduled_post
from bot.engagement_checker import save_posted_id
from bot.rate_limiter import tweet_limiter
from bot.templates import get_calendar_post
from bot.grok import should_generate_meme, generate_meme_image

logger = logging.getLogger(__name__)


def _upload_media(api_v1, image_bytes: bytes) -> str | None:
    """Upload image bytes to X and return media_id."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(image_bytes)
            tmp_path = f.name
        media = api_v1.media_upload(filename=tmp_path)
        os.unlink(tmp_path)
        return str(media.media_id)
    except Exception as e:
        logger.error(f"Failed to upload media: {e}")
        return None


def post_scheduled_content(client: tweepy.Client, api_v1=None):
    calendar = get_calendar_post()
    text = calendar if calendar else generate_post()

    # Randomly decide whether to attach a meme image
    media_ids = None
    if api_v1 and should_generate_meme():
        logger.info("Meme probability triggered — attempting image generation...")
        image_bytes = generate_meme_image(text)
        if image_bytes:
            media_id = _upload_media(api_v1, image_bytes)
            if media_id:
                media_ids = [media_id]
                logger.info(f"Meme image attached (media_id: {media_id})")
            else:
                logger.warning("Media upload failed — posting text only")
        else:
            logger.warning("Image generation returned None — posting text only")
    elif not api_v1:
        logger.warning("api_v1 not available — skipping image generation")

    tweet_limiter.wait_if_needed()
    try:
        response = client.create_tweet(
            text=text,
            media_ids=media_ids,
        )
        tweet_id = str(response.data["id"])
        save_posted_id(tweet_id)
        source = "calendar" if calendar else "ai"
        has_image = "with image" if media_ids else "text only"
        log_scheduled_post(tweet_id=tweet_id, post_text=text)
        logger.info(f"Post sent [{source}] [{has_image}] (id: {tweet_id}): {text}")
    except tweepy.TweepyException as e:
        logger.error(f"Failed to send scheduled post: {e}")
