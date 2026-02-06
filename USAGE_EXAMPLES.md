# AutoChatter Usage Examples

This document provides practical examples and scenarios for using AutoChatter.

## Quick Start Example

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OAuth Credentials

Download your `client_secret.json` from Google Cloud Console and place it in the project root.

### 3. Set Target Channel

Edit `config.py`:

```python
CHANNEL_ID = "UCxxxxxxxxxxxxxxxxxxxxx"  # Your target channel ID
DISCORD_LINK = "https://discord.gg/your-invite"
```

Or use environment variable:

```bash
set YOUTUBE_CHANNEL_ID=UCxxxxxxxxxxxxxxxxxxxxx
```

### 4. Run the Bot

```bash
python main.py
```

On first run, a browser will open for OAuth authentication. After authentication, the bot will start polling.

## Usage Scenarios

### Scenario 1: Monitor Gaming Channel for New Uploads

**Goal**: Comment on all new uploads from a gaming channel

**Configuration** (`config.py`):
```python
CHANNEL_ID = "UCxxxxxxxxxxxxxxx"  # Gaming channel
SHORTS_ONLY = False  # Comment on all videos
POLL_INTERVAL_SECONDS = 600  # Check every 10 minutes
DISCORD_LINK = "https://discord.gg/gaming-community"
DISCORD_INCLUSION_RATE = 0.2  # 20% of comments
```

**Expected Behavior**:
- Checks every 10 minutes for new videos
- Comments on all new uploads (regular videos and Shorts)
- 1 in 5 comments includes Discord link
- Random 30-180 second delay before each comment

### Scenario 2: Shorts-Only Mode

**Goal**: Only comment on YouTube Shorts (videos ≤60 seconds)

**Configuration** (`config.py`):
```python
CHANNEL_ID = "UCxxxxxxxxxxxxxxx"
SHORTS_ONLY = True  # Only comment on Shorts
MAX_SHORTS_DURATION = 60  # Maximum 60 seconds
```

**Expected Behavior**:
- Fetches new uploads
- Checks video duration for each upload
- Only comments on videos ≤60 seconds
- Skips regular-length videos

### Scenario 3: High Activity Channel

**Goal**: Monitor a high-frequency channel that posts multiple times per day

**Configuration** (`config.py`):
```python
CHANNEL_ID = "UCxxxxxxxxxxxxxxx"
POLL_INTERVAL_SECONDS = 300  # Check every 5 minutes (more frequent)
MIN_COMMENT_DELAY = 60  # Longer minimum delay
MAX_COMMENT_DELAY = 300  # Longer maximum delay
```

**Expected Behavior**:
- More frequent polling (5 minutes instead of 10)
- Longer delays between comments to appear more natural
- Handles multiple new videos per check

### Scenario 4: Minimal Discord Promotion

**Goal**: Very occasionally include Discord link

**Configuration** (`config.py`):
```python
DISCORD_INCLUSION_RATE = 0.1  # 10% of comments (1 in 10)
```

**Expected Behavior**:
- Only 1 in 10 comments includes Discord link
- More subtle promotion strategy

### Scenario 5: Always Include Discord

**Goal**: Include Discord link in every comment

**Configuration** (`config.py`):
```python
DISCORD_INCLUSION_RATE = 1.0  # 100% of comments
```

**Expected Behavior**:
- Every comment includes the Discord link
- Maximum promotion strategy

## Log Output Examples

### Normal Operation

```
2024-02-06 10:00:00 - __main__ - INFO - ============================================================
2024-02-06 10:00:00 - __main__ - INFO - AutoChatter - YouTube Auto-Comment Bot
2024-02-06 10:00:00 - __main__ - INFO - ============================================================
2024-02-06 10:00:00 - __main__ - INFO - Poll interval: 600 seconds
2024-02-06 10:00:00 - __main__ - INFO - Shorts only mode: False
2024-02-06 10:00:00 - __main__ - INFO - Discord inclusion rate: 20.0%
2024-02-06 10:00:05 - yt_client - INFO - YouTube API client initialized
2024-02-06 10:00:05 - state - INFO - Loaded state with 10 tracked videos
2024-02-06 10:00:05 - __main__ - INFO - Starting polling loop...
2024-02-06 10:00:05 - __main__ - INFO - Checking for new videos on channel UCxxxx
2024-02-06 10:00:06 - yt_client - INFO - Fetched 5 videos from channel UCxxxx
2024-02-06 10:00:06 - __main__ - INFO - Processing new video: Amazing Content! (dQw4w9WgXcQ)
2024-02-06 10:00:06 - __main__ - INFO - Waiting 127 seconds before commenting...
2024-02-06 10:02:13 - __main__ - INFO - Posting comment on video dQw4w9WgXcQ
2024-02-06 10:02:14 - yt_client - INFO - Successfully posted comment on video dQw4w9WgXcQ
2024-02-06 10:02:14 - __main__ - INFO - Successfully commented on video: Amazing Content!
2024-02-06 10:02:14 - state - INFO - State saved with 11 tracked videos
2024-02-06 10:02:14 - __main__ - INFO - Processed 1 new video(s)
2024-02-06 10:02:14 - __main__ - INFO - Waiting 600 seconds until next check...
```

### Rate Limit Handling

```
2024-02-06 10:05:00 - yt_client - WARNING - HTTP 429 error, retrying in 1s (attempt 1/5)
2024-02-06 10:05:02 - yt_client - WARNING - HTTP 429 error, retrying in 2s (attempt 2/5)
2024-02-06 10:05:06 - yt_client - WARNING - HTTP 429 error, retrying in 4s (attempt 3/5)
2024-02-06 10:05:14 - yt_client - INFO - Successfully posted comment on video dQw4w9WgXcQ
```

### Shorts-Only Mode

```
2024-02-06 10:10:00 - __main__ - INFO - Processing new video: Quick Tutorial (abc123)
2024-02-06 10:10:01 - __main__ - INFO - Video abc123 is a Short, proceeding with comment
2024-02-06 10:10:01 - __main__ - INFO - Waiting 89 seconds before commenting...
...
2024-02-06 10:11:30 - __main__ - INFO - Processing new video: Long Form Content (xyz789)
2024-02-06 10:11:31 - __main__ - INFO - Skipping non-Short video: xyz789
```

## Customizing Comment Templates

Edit `templates.py` to add or modify comment templates:

```python
COMMENT_TEMPLATES = [
    "Great video! Really enjoyed this content. 🎉",
    "Amazing work! Keep it up! 👏",
    # Add your custom templates
    "This tutorial was exactly what I needed! 📚",
    "Subscribed! Looking forward to more! 🔔",
    "Your content quality is outstanding! 💯",
]
```

**Tips**:
- Keep templates positive and relevant
- Use emojis sparingly for personality
- Avoid spammy language
- Ensure templates are appropriate for all video types

## State File Structure

The `state.json` file tracks processed videos:

```json
{
  "last_seen_videos": [
    "dQw4w9WgXcQ",
    "abc123xyz",
    "video_id_3"
  ],
  "last_check_time": "2024-02-06T10:00:00.000000"
}
```

**Note**: This file is automatically managed. Manual editing is not recommended but can be done to:
- Clear history: Delete `state.json` to reprocess all videos
- Skip specific videos: Add video IDs to prevent commenting

## Troubleshooting Examples

### Problem: Bot comments on old videos

**Solution**: The state file might be missing or corrupted. The bot will comment on the 5 most recent videos it hasn't seen before. To prevent this:
- Don't delete `state.json` during normal operation
- Start with a pre-populated state file if needed

### Problem: Too many API quota exceeded errors

**Solution**: Reduce polling frequency or number of videos checked:

```python
POLL_INTERVAL_SECONDS = 1800  # 30 minutes instead of 10
```

### Problem: Comments appear too robotic

**Solution**: Increase delay variance and reduce Discord inclusion:

```python
MIN_COMMENT_DELAY = 60
MAX_COMMENT_DELAY = 300
DISCORD_INCLUSION_RATE = 0.1  # Less frequent promotion
```

## Running as a Background Service (Windows)

### Option 1: Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "At startup" or specific time
4. Action: Start a program
   - Program: `pythonw.exe` (no console window)
   - Arguments: `C:\path\to\AutoChatter\main.py`
   - Start in: `C:\path\to\AutoChatter`

### Option 2: NSSM (Non-Sucking Service Manager)

```bash
# Download NSSM, then:
nssm install AutoChatter "C:\Python311\python.exe" "C:\path\to\AutoChatter\main.py"
nssm start AutoChatter
```

## Best Practices

1. **Start Small**: Begin with a low posting frequency to test
2. **Monitor Logs**: Check `autochatter.log` regularly for issues
3. **Respect Rate Limits**: Don't set polling interval too low
4. **Natural Behavior**: Use appropriate delays and template variety
5. **Backup State**: Periodically backup `state.json`
6. **Test First**: Run manually before setting up as service
7. **Stay Compliant**: Follow YouTube's Terms of Service and API policies

## Advanced Configuration

### Multiple Channels

To monitor multiple channels, run separate instances with different config files:

```bash
# Create config_channel1.py, config_channel2.py, etc.
# Modify main.py to accept config file as argument
python main.py --config config_channel1.py
```

### Custom Retry Strategy

Edit `yt_client.py` to customize retry behavior:

```python
MAX_RETRIES = 10  # More retries
INITIAL_BACKOFF = 2  # Start with 2 seconds
MAX_BACKOFF = 600  # Up to 10 minutes
```

### Logging Configuration

Edit `main.py` to customize logging:

```python
logging.basicConfig(
    level=logging.DEBUG,  # More verbose
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autochatter.log'),
        logging.StreamHandler()
    ]
)
```

## Safety and Ethics

⚠️ **Important Reminders**:

- Use AutoChatter responsibly and ethically
- Ensure comments add value and are relevant
- Don't spam or harass content creators
- Respect YouTube's Terms of Service
- Monitor your bot's behavior regularly
- Be transparent if asked about automation
- Consider the impact on the YouTube community

## Support

For issues or questions:
1. Check `autochatter.log` for error details
2. Review this documentation
3. Check the main README.md for setup instructions
4. Verify your OAuth credentials and API quota
5. Ensure Python 3.11+ is installed
