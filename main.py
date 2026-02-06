"""AutoChatter - Automated YouTube comment bot.

This application monitors a YouTube channel for new uploads and automatically
posts comments using the YouTube Data API v3 with OAuth authentication.
"""

import logging
import time
import random
import sys

import config
from state import StateManager
from yt_client import YouTubeClient
from templates import get_random_comment, should_include_discord

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def process_video(yt_client: YouTubeClient, state: StateManager, video: dict) -> None:
    """Process a single video: check if it should be commented on and post comment.
    
    Args:
        yt_client: YouTube API client.
        state: State manager.
        video: Video dictionary with id, title, and published_at.
    """
    video_id = video['id']
    video_title = video['title']
    
    # Check if video has already been processed
    if state.is_video_seen(video_id):
        logger.debug(f"Video {video_id} already processed, skipping")
        return
    
    logger.info(f"Processing new video: {video_title} ({video_id})")
    
    # Check if Shorts-only mode is enabled
    if config.SHORTS_ONLY:
        is_short = yt_client.is_short(video_id)
        if not is_short:
            logger.info(f"Skipping non-Short video: {video_id}")
            state.mark_video_seen(video_id)
            return
        logger.info(f"Video {video_id} is a Short, proceeding with comment")
    
    # Random delay before commenting (30-180 seconds)
    delay = random.randint(config.MIN_COMMENT_DELAY, config.MAX_COMMENT_DELAY)
    logger.info(f"Waiting {delay} seconds before commenting...")
    time.sleep(delay)
    
    # Determine if Discord link should be included
    include_discord = should_include_discord(config.DISCORD_INCLUSION_RATE)
    comment_text = get_random_comment(include_discord, config.DISCORD_LINK)
    
    logger.info(f"Posting comment on video {video_id}")
    logger.debug(f"Comment text: {comment_text}")
    
    # Post the comment
    success = yt_client.post_comment(video_id, comment_text)
    
    if success:
        logger.info(f"Successfully commented on video: {video_title}")
    else:
        logger.error(f"Failed to comment on video: {video_title}")
    
    # Mark video as seen regardless of comment success to avoid retry loops
    state.mark_video_seen(video_id)


def check_for_new_videos(yt_client: YouTubeClient, state: StateManager) -> None:
    """Check for new videos and process them.
    
    Args:
        yt_client: YouTube API client.
        state: State manager.
    """
    if not config.CHANNEL_ID:
        logger.error("CHANNEL_ID not configured. Please set it in config.py or environment.")
        return
    
    logger.info(f"Checking for new videos on channel {config.CHANNEL_ID}")
    
    # Fetch recent uploads
    videos = yt_client.get_channel_uploads(config.CHANNEL_ID, max_results=5)
    
    if not videos:
        logger.info("No videos found or error fetching videos")
        return
    
    # Process each video (newest first)
    new_videos_count = 0
    for video in videos:
        if not state.is_video_seen(video['id']):
            new_videos_count += 1
            process_video(yt_client, state, video)
    
    if new_videos_count == 0:
        logger.info("No new videos to process")
    else:
        logger.info(f"Processed {new_videos_count} new video(s)")


def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("AutoChatter - YouTube Auto-Comment Bot")
    logger.info("=" * 60)
    logger.info(f"Poll interval: {config.POLL_INTERVAL_SECONDS} seconds")
    logger.info(f"Shorts only mode: {config.SHORTS_ONLY}")
    logger.info(f"Discord inclusion rate: {config.DISCORD_INCLUSION_RATE * 100}%")
    logger.info("=" * 60)
    
    # Validate configuration
    if not config.CHANNEL_ID:
        logger.error("ERROR: CHANNEL_ID not configured!")
        logger.error("Please set YOUTUBE_CHANNEL_ID environment variable or edit config.py")
        sys.exit(1)
    
    # Initialize components
    try:
        logger.info("Initializing YouTube client...")
        yt_client = YouTubeClient()
        
        logger.info("Initializing state manager...")
        state = StateManager(config.STATE_FILE)
        
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please ensure client_secret.json is in the current directory.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error initializing application: {e}")
        sys.exit(1)
    
    # Main polling loop
    logger.info("Starting polling loop...")
    
    try:
        while True:
            try:
                check_for_new_videos(yt_client, state)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
            
            # Wait for next poll
            logger.info(f"Waiting {config.POLL_INTERVAL_SECONDS} seconds until next check...")
            time.sleep(config.POLL_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
