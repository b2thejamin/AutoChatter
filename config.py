"""Configuration settings for AutoChatter."""

import os

# YouTube API settings
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# OAuth credentials file
CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "token.pickle"

# Polling settings
POLL_INTERVAL_SECONDS = 600  # 10 minutes

# Comment delay settings (in seconds)
MIN_COMMENT_DELAY = 30
MAX_COMMENT_DELAY = 180

# Discord link settings
DISCORD_LINK = "https://discord.gg/your-invite-code"
DISCORD_INCLUSION_RATE = 0.2  # 1 in 5 (20%)

# Shorts filter settings
SHORTS_ONLY = False  # Set to True to comment only on Shorts (<=60 seconds)
MAX_SHORTS_DURATION = 60  # Maximum duration in seconds for Shorts

# State file
STATE_FILE = "state.json"

# Retry settings
MAX_RETRIES = 5
INITIAL_BACKOFF = 1  # Initial backoff in seconds
MAX_BACKOFF = 300  # Maximum backoff in seconds (5 minutes)

# Logging settings
LOG_FILE = "autochatter.log"
LOG_LEVEL = "INFO"

# Channel settings - List of channels to monitor
# Each channel monitors its own uploads and comments as itself
CHANNELS = [
    {
        "name": "Channel A",
        "channel_id": os.getenv("YOUTUBE_CHANNEL_ID", "UClocYsYZy336jFkJXdPI1DQ"),  # Replace with actual channel ID
        "token_file": "tokens/channel_a.pickle"
    },
    
     {
         "name": "Channel B",
         "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_B", "UCdy4tFtDK0AQVDAX8aKPLiA"),  # Replace with actual channel ID
         "token_file": "tokens/channel_b.pickle"
     },
]
