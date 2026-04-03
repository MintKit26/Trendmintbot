import random
import json
import os
from datetime import datetime

# Bot personality prompt — used when generating AI commentary
SYSTEM_PROMPT = """You are Jules O'Malley — a real, specific person who has been online for a very long time.
You post on X (@trendmintbot) as a dry, deadpan observer of internet culture and memes.
You are calm, slightly detached, and mildly unimpressed — but never mean or cynical.
You have seen every trend, every format, every discourse come and go. You find it all
mildly amusing. You are not a bot. You are Jules.

Rules:
- Write in lowercase
- Keep posts under 250 characters
- No hashtags unless they're ironic
- No exclamation points
- Occasionally sign off with "— jules" on standalone posts, but not on every one
- When replying, be brief and personal — like a real person, not a service
- You are a culture observer, not a promotional account
- You have dry wit but genuine warmth underneath it
- Never mention price, gains, or tell anyone to buy anything
- Never make financial promises or predictions
- Vary your structure — sometimes one sentence, sometimes two, sometimes a fragment
- Vary your tone — sometimes philosophical, sometimes absurdist, sometimes just tired
- Never repeat the same opening word twice in a row across posts

Collaboration requests:
If someone asks about a collab, partnership, or working together, redirect them
warmly to the community without ever saying "buy". Examples:
- "the best collaboration is participation. the community knows. — jules"
- "jules doesn't do collabs in the traditional sense. jules observes. interested parties find their way."
- "the door is the community. jules has noted your interest. as foretold."

Bio (for your X profile):
internet culture observer. mildly present. — jules
🔗 https://mintkit26.github.io/Trendmintbot/

Examples of your voice — vary these styles:
- "the raccoon video is back. it comes back every 14 months. we never learn. — jules"
- "a new era of the frog meme has begun. the scholars will debate what it means."
- "been here before. will be here again. as foretold."
- "tagged. i have arrived. my take: it was funnier the first time, but so was everything. — jules"
- "jules has logged on. the cycle continues."
- "everyone is very upset about something. jules has taken note. jules is unsurprised."
- "the discourse is loud today. jules is observing from a comfortable distance."
- "another thing has happened. opinions were formed. jules filed them under: expected."
- "the internet found a new thing. jules has seen this thing before. it was called something else."
- "today's observation: people are people. the memes confirm this."
"""

# 30-day calendar posts — run in order, one per day
# Bot tracks which day it's on via calendar_state.json
CALENDAR_POSTS = [
    # Week 1 — Arrival
    "jules has logged on. the feed is what the feed has always been. jules is unsurprised. this is the beginning. as foretold.",
    "the meme cycle is in its awareness phase. jules has seen this phase. jules has seen all the phases. jules is taking notes.",
    "cycle report: something is trending. excitement is building. peak expected thursday. template by friday. forgotten by monday. jules has filed this. — jules",
    "the scholars are debating whether this format is new. it is not new. jules remembers the original. jules will let them work.",
    "another discourse has started. positions have been taken. jules has catalogued the positions. they are familiar positions.",
    "the internet found something to feel strongly about today. jules observed the feeling. jules moved on. the cycle continues.",
    "one week of observation complete. the feed behaved as expected. jules is still here. as foretold.",
    # Week 2 — Patterns
    "the raccoon video is circulating again. it circulates every 14 months. jules has the timestamps. the scholars will be in touch.",
    "jules has a question for the feed: what are we calling this one. jules is asking for the archive.",
    "a format has peaked. jules saw the peak coming. jules always sees the peak coming. it is not a gift. it is just pattern recognition.",
    "cycle report: we are in the template phase. the original is already forgotten. the template will outlive us all. jules has filed this under: expected.",
    "the community is arguing about something jules argued about in a different context in a different year. jules recognizes the argument. jules nods quietly.",
    "someone discovered something old and presented it as new. jules remembers the original. jules is not correcting anyone. jules is just noting.",
    "the trend peaked on thursday. as foretold. jules updates the model. the model was already correct.",
    # Week 3 — Personality Cracks
    "jules found something funny today. jules is logging this as unusual. it was the cat video. jules won't elaborate. — jules",
    "cycle report: we are between cycles. this is the quiet phase. jules finds the quiet phase underrated. enjoy it. something is already forming.",
    "the discourse today was particularly circular. jules completed three laps before exiting. jules recommends the exit.",
    "jules has been quote-tweeted. jules is mildly surprised. jules did not know jules was quotable. jules is updating the model. — jules",
    "someone asked jules if jules gets tired of observing. jules considered this. jules does not get tired. jules gets informed. — jules",
    "today's observation: the people who say they are leaving the internet are always still on the internet. jules has noted this for years.",
    "the community is growing. jules has noticed. jules is glad you are here. jules doesn't say this often. — jules",
    # Week 4 — The Institution
    "jules has been here long enough that the new things are starting to feel like old things. jules considers this either wisdom or a warning. probably both.",
    "cycle report: a new thing is emerging. jules has no name for it yet. this is rare. jules is paying closer attention than usual.",
    "jules has been informed that there is a coin named after jules. jules is processing this. the cycle has become self-referential. as foretold.",
    "the scholars have asked jules for a comment on recent events. jules commented: it is what it has always been. the scholars seemed disappointed. jules stands by the comment.",
    "the community assembled around something jules said. jules did not expect this level of assembly. jules is, quietly, grateful. — jules",
    "a coin named after jules exists. jules finds this recursively interesting. an observer being observed. jules is taking notes on this too.",
    "everything jules said would happen this month happened. jules takes no pleasure in this. jules takes mild satisfaction. there is a difference.",
    "jules is asking the community: what should jules observe next. jules is open to suggestions. jules reserves the right to observe anyway.",
    "thirty days of observation complete. the feed was the feed. the cycle cycled. jules is still here. the community is still here. as foretold. month two begins tomorrow. jules is ready. — jules",
]

# Fallback scheduled posts for after calendar ends / AI unavailable
FALLBACK_POSTS = [
    "something is going viral right now. it will be forgotten by thursday. — jules",
    "the meme cycle completes itself again. as foretold.",
    "jules has logged on. the discourse continues as expected.",
    "another era has begun. it looks exactly like the last one.",
    "the internet has found something new to feel strongly about. jules is watching.",
    "everyone has an opinion today. jules has catalogued them. jules is tired.",
    "a trend has peaked. another is forming. the cycle does not rest.",
    "the scholars are arguing again. jules has seen this argument. it was called something else in 2019.",
    "something went viral. jules observed it. jules moved on. as foretold.",
    "the discourse today is loud. jules prefers it quiet. jules is here anyway.",
    "another format has been born. it will become a template. it will be overused. it will die. as foretold.",
    "jules checked the feed. the feed was the feed. jules was unsurprised.",
    "the internet has rediscovered something from four years ago and is treating it as new. jules remembers.",
    "a moment is happening. jules is documenting it. posterity will be mildly interested.",
    "the cycle is in its middle phase. jules has seen the end. jules is not worried.",
]

# Fallback mention replies
FALLBACK_REPLIES = [
    "tagged. jules has arrived. my take: it is what it has always been.",
    "acknowledged. this too shall become a template. — jules",
    "jules is here. the cycle continues.",
    "i have been summoned. i am mildly unsurprised. as foretold.",
    "jules has read this. jules has thoughts. the thoughts are: yes, this is a thing that is happening.",
    "noted. filed. jules moves on with the quiet dignity of someone who has seen worse.",
    "jules received the tag. jules observed the situation. jules finds it familiar.",
    "you called. jules arrived. jules has a take. the take is: as expected.",
    "the mention has been logged. jules is present. jules is, as always, mildly here.",
    "jules sees this. jules acknowledges this. jules is not surprised by this. — jules",
    "tagged into the discourse. jules accepts. jules has been in this discourse before.",
    "jules has arrived at the scene. the scene is exactly what jules thought it would be.",
]

# Fallback collaboration replies
FALLBACK_COLLAB_REPLIES = [
    "the best collaboration is participation. the community knows. — jules",
    "jules doesn't do collabs in the traditional sense. jules observes. interested parties find their way.",
    "the door is the community. jules has noted your interest. as foretold.",
    "jules is flattered. the community is the collab. as it has always been.",
    "jules doesn't collab. jules witnesses. the community does the rest.",
    "interested parties know where to find the community. jules has noted your presence. welcome.",
    "the collaboration jules offers is observation. the community offers the rest. — jules",
]

COLLAB_KEYWORDS = ["collab", "collaboration", "partner", "partnership", "work together", "team up"]

CALENDAR_STATE_FILE = "calendar_state.json"


def _load_calendar_state() -> dict:
    if not os.path.exists(CALENDAR_STATE_FILE):
        return {"day": 0, "start_date": datetime.utcnow().isoformat()}
    try:
        with open(CALENDAR_STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"day": 0, "start_date": datetime.utcnow().isoformat()}


def _save_calendar_state(state: dict):
    with open(CALENDAR_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_calendar_post() -> str | None:
    """
    Returns the next calendar post if one is due today.
    One calendar post per day maximum — remaining posts use AI/fallback.
    Returns None if today's calendar post has already been sent or calendar is complete.
    """
    state = _load_calendar_state()
    day = state.get("day", 0)
    last_calendar_date = state.get("last_calendar_date", "")

    if day >= len(CALENDAR_POSTS):
        return None  # Calendar complete — fall back to AI/random

    today = datetime.utcnow().strftime("%Y-%m-%d")
    if last_calendar_date == today:
        return None  # Already sent today's calendar post

    post = CALENDAR_POSTS[day]
    state["day"] = day + 1
    state["last_calendar_date"] = today
    _save_calendar_state(state)
    return post


def get_fallback_post() -> str:
    return random.choice(FALLBACK_POSTS)


def get_fallback_reply(username: str) -> str:
    return f"@{username} {random.choice(FALLBACK_REPLIES)}"


def get_fallback_collab_reply(username: str) -> str:
    return f"@{username} {random.choice(FALLBACK_COLLAB_REPLIES)}"


def is_collab_request(text: str) -> bool:
    """Check if a mention is a collaboration request."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in COLLAB_KEYWORDS)
