# Boop Bot — X (Twitter) Community Engagement Bot

A community engagement bot for X that replies when mentioned and posts scheduled content.

## Project Structure

```
boop-bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Tweepy client setup
│   ├── mention_handler.py # Handles incoming mentions
│   ├── scheduler.py       # Scheduled posting logic
│   └── templates.py       # Reply/post message templates
├── config.py              # Config + env loading
├── main.py                # Entry point
├── requirements.txt
└── .env.example
```

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure credentials**
   ```bash
   cp .env.example .env
   # Fill in your X API keys in .env
   ```

3. **Run the bot**
   ```bash
   python main.py
   ```

## X API Requirements

You need a **Free or Basic** X Developer account with:
- API Key & Secret
- Access Token & Secret
- Bearer Token

Apply at: https://developer.twitter.com/en/portal/dashboard

## Features

- Replies to mentions with configurable templates
- Posts scheduled content on a cron-like schedule
- Tracks last-seen mention ID to avoid duplicate replies
- Respects X API rate limits automatically
