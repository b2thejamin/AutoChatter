# AutoChatter

AutoChatter is a Python application that automatically posts comments on new YouTube video uploads using the YouTube Data API v3 with OAuth authentication. The bot monitors a specified channel, detects new uploads, and posts randomized comments with optional Discord invite links.

## Features

- 🔄 **Automatic Polling**: Checks for new videos every 10 minutes
- 🎯 **Smart Filtering**: Optional Shorts-only mode (videos ≤60 seconds)
- 💬 **10 Comment Templates**: Randomly selected for variety
- 🔗 **Discord Integration**: Includes Discord link in 1/5 (20%) of comments
- ⏱️ **Random Delays**: 30-180 second delay before commenting (appears more natural)
- 🔁 **Retry Logic**: Handles 429 (rate limit) and 5xx errors with exponential backoff
- 💾 **State Management**: JSON-based tracking to avoid duplicate comments
- 📝 **Comprehensive Logging**: File and console logging with rotation

## Requirements

- Python 3.11+
- Windows (designed for local Windows environment)
- YouTube Data API v3 credentials
- Google Cloud Platform project with YouTube Data API enabled

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/b2thejamin/AutoChatter.git
   cd AutoChatter
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up YouTube API credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or select existing)
   - Enable the **YouTube Data API v3**
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials JSON file
   - Rename it to `client_secret.json` and place it in the project root directory

## Configuration

Edit `config.py` to customize the bot behavior:

### Essential Settings

```python
# Target YouTube channel ID to monitor
CHANNEL_ID = "UCxxxxxxxxxxxxxxxxxx"  # Replace with actual channel ID

# Discord invite link (included in 20% of comments)
DISCORD_LINK = "https://discord.gg/your-invite-code"
```

### Optional Settings

```python
# Polling interval (default: 600 seconds = 10 minutes)
POLL_INTERVAL_SECONDS = 600

# Comment delay range in seconds (default: 30-180)
MIN_COMMENT_DELAY = 30
MAX_COMMENT_DELAY = 180

# Discord link inclusion rate (default: 0.2 = 20% = 1/5)
DISCORD_INCLUSION_RATE = 0.2

# Shorts-only mode (default: False)
SHORTS_ONLY = False  # Set to True to comment only on Shorts (≤60s)
MAX_SHORTS_DURATION = 60

# Retry settings
MAX_RETRIES = 5
INITIAL_BACKOFF = 1
MAX_BACKOFF = 300
```

### Environment Variable Alternative

You can also set the channel ID via environment variable:

**Windows Command Prompt**:
```cmd
set YOUTUBE_CHANNEL_ID=UCxxxxxxxxxxxxxxxxxx
```

**Windows PowerShell**:
```powershell
$env:YOUTUBE_CHANNEL_ID="UCxxxxxxxxxxxxxxxxxx"
```

## Usage

### First Run (OAuth Authentication)

On the first run, the application will open a browser window for OAuth authentication:

```bash
python main.py
```

1. A browser window will open
2. Sign in with your Google account
3. Grant the requested permissions
4. The authentication token will be saved to `token.pickle` for future use

### Normal Operation

After initial authentication, simply run:

```bash
python main.py
```

The bot will:
1. Start polling the configured channel every 10 minutes
2. Detect new video uploads
3. Wait a random delay (30-180 seconds)
4. Post a random comment from the template list
5. Optionally include Discord link (20% chance)
6. Log all activities to console and `autochatter.log`

### Stopping the Bot

Press `Ctrl+C` to stop the bot gracefully.

## Project Structure

```
AutoChatter/
├── main.py              # Main application entry point with polling loop
├── yt_client.py         # YouTube API client with OAuth and retry logic
├── templates.py         # Comment templates and Discord link logic
├── state.py             # JSON state management for tracking seen videos
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore patterns
├── client_secret.json  # OAuth credentials (user-provided, not in repo)
├── token.pickle        # OAuth token (auto-generated, not in repo)
├── state.json          # State tracking file (auto-generated, not in repo)
└── autochatter.log     # Application log file (auto-generated, not in repo)
```

## How It Works

1. **Initialization**: Loads OAuth credentials and authenticates with YouTube API
2. **State Loading**: Reads `state.json` to get list of previously seen videos
3. **Polling Loop**: Every 10 minutes:
   - Fetches latest 5 uploads from the target channel
   - Identifies new videos not in the state file
   - For each new video:
     - Checks duration if Shorts-only mode is enabled
     - Waits random delay (30-180 seconds)
     - Selects random comment template
     - Decides whether to include Discord link (20% probability)
     - Posts comment via `CommentThreads.insert` API
     - Handles rate limits and errors with retry/backoff
     - Marks video as seen in state file
4. **Error Handling**: Retries on 429/5xx errors with exponential backoff

## API Rate Limits

YouTube Data API v3 has quotas:
- Default quota: 10,000 units per day
- Comment posting: 50 units per comment
- Video listing: 1 unit per request

With default settings (10-minute polling):
- ~144 checks per day = 144 units
- If posting 5 comments per day = 250 units
- Total: ~394 units/day (well within quota)

## Security Notes

⚠️ **Important**: 
- Never commit `client_secret.json` or `token.pickle` to version control
- These files are automatically excluded via `.gitignore`
- Keep your OAuth credentials secure
- Use a dedicated Google account for bot operations

## Troubleshooting

### "Client secrets file not found"
- Ensure `client_secret.json` is in the project root directory
- Download OAuth credentials from Google Cloud Console

### "CHANNEL_ID not configured"
- Set `CHANNEL_ID` in `config.py` or use environment variable
- Find channel ID from the YouTube channel URL

### "HTTP 403 Forbidden"
- Verify YouTube Data API v3 is enabled in Google Cloud Console
- Check OAuth scopes include `youtube.force-ssl`
- Ensure the authenticated account has permission to comment

### "HTTP 429 Too Many Requests"
- API rate limit exceeded
- Bot will automatically retry with exponential backoff
- Consider increasing `POLL_INTERVAL_SECONDS`

### Comments not appearing
- Verify the target channel allows comments
- Check that videos have comments enabled
- Review `autochatter.log` for errors

## Customization

### Adding More Comment Templates

Edit `templates.py` and add to the `COMMENT_TEMPLATES` list:

```python
COMMENT_TEMPLATES = [
    "Great video! Really enjoyed this content. 🎉",
    # Add your custom templates here
    "Your custom comment here! 🚀",
]
```

### Adjusting Polling Interval

Edit `config.py`:

```python
POLL_INTERVAL_SECONDS = 1800  # 30 minutes
```

### Enabling Shorts-Only Mode

Edit `config.py`:

```python
SHORTS_ONLY = True
```

## License

This project is provided as-is for educational purposes. Use responsibly and in accordance with YouTube's Terms of Service and API usage policies.

## Disclaimer

⚠️ **Use at your own risk**: Automated commenting may violate YouTube's spam policies. Ensure your usage complies with YouTube's Terms of Service, Community Guidelines, and API Terms of Service. The authors are not responsible for any account suspensions or bans resulting from misuse of this software.