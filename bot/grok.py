"""
bot/grok.py — xAI Grok integration for Jules.

Two functions:
1. get_trending_context() — asks Grok what's happening in culture right now
2. generate_meme_image() — generates a meme image from Jules' post text
"""

import json
import logging
import os
import random
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

GROK_API_URL = "https://api.x.ai/v1"
GROK_TEXT_MODEL = "grok-3"
GROK_IMAGE_MODEL = "grok-2-image"

# Set to 1.0 for testing, change back to 0.33 for production
MEME_PROBABILITY = 1.0


def _get_api_key() -> str | None:
    key = os.environ.get("XAI_API_KEY")
    if not key:
        logger.warning("XAI_API_KEY not set — Grok features disabled")
    return key


def _call_grok_text(messages: list, system: str = "") -> str | None:
    api_key = _get_api_key()
    if not api_key:
        return None

    payload = {
        "model": GROK_TEXT_MODEL,
        "max_tokens": 300,
        "messages": messages,
    }
    if system:
        payload["system"] = system

    req = urllib.request.Request(
        f"{GROK_API_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        logger.error(f"Grok text API error {e.code}: {e.read().decode()}")
    except Exception as e:
        logger.error(f"Unexpected Grok text error: {e}")

    return None


def _call_grok_image(prompt: str) -> bytes | None:
    """Generate an image using xAI Aurora and return raw bytes."""
    api_key = _get_api_key()
    if not api_key:
        return None

    payload = {
        "model": GROK_IMAGE_MODEL,
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
    }

    req = urllib.request.Request(
        f"{GROK_API_URL}/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            import base64
            b64 = data["data"][0]["b64_json"]
            return base64.b64decode(b64)
    except urllib.error.HTTPError as e:
        logger.error(f"Grok image API error {e.code}: {e.read().decode()}")
    except Exception as e:
        logger.error(f"Unexpected Grok image error: {e}")

    return None


def get_trending_context() -> str | None:
    """
    Ask Grok what's trending in internet culture right now.
    Returns a brief summary Jules can use as context for his posts.
    """
    messages = [
        {
            "role": "user",
            "content": (
                "What are 2-3 things currently trending or being talked about in "
                "internet culture, memes, or social media right now? "
                "Give me very brief bullet points — just the topics, no explanation. "
                "Focus on meme formats, viral moments, or cultural discourse."
            )
        }
    ]

    result = _call_grok_text(messages)
    if result:
        logger.info(f"Grok trending context: {result[:100]}...")
    return result


def should_generate_meme() -> bool:
    """Randomly decide whether this post should have a meme image."""
    return random.random() < MEME_PROBABILITY


def generate_meme_image(post_text: str) -> bytes | None:
    """
    Generate a dry, Jules-appropriate meme image based on the post text.
    Returns raw image bytes or None if generation fails.
    """
    image_prompt_request = (
        f"Jules O'Malley just posted: \"{post_text}\"\n\n"
        "Generate a short image generation prompt (under 100 words) for a dry, deadpan "
        "meme image that visually represents this observation. "
        "Style: flat illustration, muted colors, slightly absurdist. "
        "No text in the image. No logos. No people's faces. "
        "Think New Yorker cartoon meets internet culture. "
        "Return only the image prompt, nothing else."
    )

    image_prompt = _call_grok_text([
        {"role": "user", "content": image_prompt_request}
    ])

    if not image_prompt:
        return None

    logger.info(f"Generating meme image with prompt: {image_prompt[:80]}...")
    return _call_grok_image(image_prompt)
