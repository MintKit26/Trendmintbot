import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("X_API_KEY")
API_SECRET = os.getenv("X_API_SECRET")
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

POST_INTERVAL_HOURS = int(os.getenv("POST_INTERVAL_HOURS", 1))
MENTION_POLL_INTERVAL = int(os.getenv("MENTION_POLL_INTERVAL", 60))

def validate():
    required = [API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN]
    if not all(required):
        raise EnvironmentError("Missing one or more X API credentials in .env")
