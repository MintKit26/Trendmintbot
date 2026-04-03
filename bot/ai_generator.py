import logging
import json
import os
import random
import urllib.request
import urllib.error
from bot.templates import SYSTEM_PROMPT, get_fallback_post, get_fallback_reply

logger = logging.getLogger(__name__)

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"


def _call_claude(user_prompt: str) -> str | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set — using fallback templates")
        return None

    payload = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 100,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        CLAUDE_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        logger.error(f"Claude API error {e.code}: {e.read().decode()}")
    except Exception as e:
        logger.error(f"Unexpected error calling Claude: {e}")

    return None


def generate_post() -> str:
    """Generate an original commentary post about meme/internet culture."""
    from bot.grok import get_trending_context
    trending = get_trending_context()
    trending_context = (
        f"Here's what's currently trending in internet culture: {trending}\n\n"
        if trending else ""
    )

    styles = [
        "Write a single dry observation about something happening in internet culture right now. One or two sentences max.",
        "Write a short deadpan take on meme culture or online behavior. Make it feel like an offhand thought, not a statement.",
        "Write something Jules would post at 2am after scrolling too long. Tired but accurate.",
        "Write a philosophical one-liner about the internet. Keep it under 150 characters.",
        "Write a two-sentence observation where the second sentence undercuts the first in a dry way.",
        "Write something that sounds like a nature documentary narration about internet behavior. Keep it short.",
        "Write a brief observation about how people talk online versus how they actually are.",
        "Write something about the gap between what gets posted and what's actually true.",
        "Write a short take on nostalgia and how the internet handles the past.",
        "Write something about a specific type of online person jules has observed many times.",
        "Write a quiet observation about something everyone does online but nobody talks about.",
        "Write something about the lifecycle of an online trend — but pick a specific unexpected moment in that cycle.",
        "Write something that feels like a field note from an anthropologist studying internet culture.",
        "Write a short observation about how online communities form, behave, or collapse.",
        "Write something about the difference between going viral and actually mattering.",
        "Write a wry observation about how people perform authenticity online.",
        "Write something about the strange relationship between real life events and how the internet reacts to them.",
        "Write a dry take on how online discourse has changed — or hasn't.",
        "Write something about a specific trending topic from the context provided, observed through Jules' dry lens.",
    ]

    prompt = (
        f"{trending_context}"
        f"{random.choice(styles)} "
        "No hashtags. No exclamation points. Lowercase. Under 250 characters. "
        "Vary your sentence structure and topic significantly."
    )
    result = _call_claude(prompt)
    return result if result else get_fallback_post()


def generate_reply(username: str, tweet_text: str) -> str:
    """Generate a reply to a mention, staying in character."""
    styles = [
        "Reply briefly and personally, like a tired person who has seen this before.",
        "Reply with a single dry observation about what they said.",
        "Acknowledge them and give a short take. Keep it conversational.",
        "Reply like you're mildly interested but not surprised. One or two sentences.",
    ]
    prompt = (
        f"{random.choice(styles)}\n"
        f"Someone tagged you. Their tweet said: \"{tweet_text}\"\n"
        f"Reply to @{username} as Jules. Lowercase. No exclamation points. "
        f"Under 250 characters. Start with @{username}."
    )
    result = _call_claude(prompt)
    return result if result else get_fallback_reply(username)
