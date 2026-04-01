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
from templates import generate_comment

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


def process_video(yt_client: YouTubeClient, state: StateManager, video: dict, channel_id: str, channel_name: str) -> None:
    """Process a single video: check if it should be commented on and post comment.

    Args:
        yt_client: YouTube API client.
        state: State manager.
        video: Video dictionary with id, title, and published_at.
        channel_id: Channel ID being processed.
        channel_name: Channel name being processed.
    """
    video_id = video['id']
    video_title = video['title']

    # Check if video has already been processed (channel-specific tracking)
    if state.is_video_seen(video_id, channel_id):
        logger.debug(f"[{channel_name}] Video {video_id} already processed, skipping")
        return

    logger.info(f"[{channel_name}] Processing new video: {video_title} ({video_id})")
    
    # Check if Shorts-only mode is enabled
    if config.SHORTS_ONLY:
        is_short = yt_client.is_short(video_id)
        if not is_short:
            logger.info(f"[{channel_name}] Skipping non-Short video: {video_id}")
            state.mark_video_seen(video_id, channel_id)
            return
        logger.info(f"[{channel_name}] Video {video_id} is a Short, proceeding with comment")
    
    # Random delay before commenting (30-180 seconds)
    delay = random.randint(config.MIN_COMMENT_DELAY, config.MAX_COMMENT_DELAY)
    logger.info(f"[{channel_name}] Waiting {delay} seconds before commenting...")
    time.sleep(delay)

    # Generate comment (Discord link is already included)
    comment_text = generate_comment()

    logger.info(f"[{channel_name}] Posting comment on video {video_id}")
    logger.debug(f"[{channel_name}] Comment text: {comment_text}")

    # Post the comment
    success = yt_client.post_comment(video_id, comment_text)

    if success:
        logger.info(f"[{channel_name}] Successfully commented on video: {video_title}")
    else:
        logger.error(f"[{channel_name}] Failed to comment on video: {video_title}")

    # Mark video as seen regardless of comment success to avoid retry loops (channel-specific tracking)
    state.mark_video_seen(video_id, channel_id)


def check_for_new_videos(yt_client: YouTubeClient, state: StateManager, channel_id: str, channel_name: str) -> None:
    """Check for new videos and process them.

    Args:
        yt_client: YouTube API client.
        state: State manager.
        channel_id: YouTube channel ID.
        channel_name: Channel name for logging.
    """
    logger.info(f"[{channel_name}] ===== Starting check =====")
    logger.info(f"[{channel_name}] Checking for new videos on channel {channel_id}")

    # Fetch recent uploads
    videos = yt_client.get_channel_uploads(channel_id, max_results=5)

    if not videos:
        logger.info(f"[{channel_name}] No videos found or error fetching videos")
        logger.info(f"[{channel_name}] ===== Finished check =====")
        return

    # Process each video (newest first)
    new_videos_count = 0
    for video in videos:
        if not state.is_video_seen(video['id'], channel_id):
            new_videos_count += 1
            process_video(yt_client, state, video, channel_id, channel_name)

    if new_videos_count == 0:
        logger.info(f"[{channel_name}] No new videos to process")
    else:
        logger.info(f"[{channel_name}] Processed {new_videos_count} new video(s)")

    logger.info(f"[{channel_name}] ===== Finished check =====")



def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("AutoChatter - YouTube Auto-Comment Bot")
    logger.info("=" * 60)
    logger.info(f"Poll interval: {config.POLL_INTERVAL_SECONDS} seconds")
    logger.info(f"Shorts only mode: {config.SHORTS_ONLY}")
    logger.info("Discord link: Always included in every comment")
    logger.info(f"Number of channels configured: {len(config.CHANNELS)}")
    logger.info("=" * 60)

    # Validate configuration
    if not config.CHANNELS:
        logger.error("ERROR: No channels configured!")
        logger.error("Please add at least one channel to the CHANNELS list in config.py")
        sys.exit(1)

    # Initialize components for each channel
    channel_clients = []
    state = None

    try:
        logger.info("Initializing state manager...")
        state = StateManager(config.STATE_FILE)

        logger.info("Initializing YouTube clients for each channel...")

        for channel_config in config.CHANNELS:
            channel_name = channel_config.get('name', 'Unknown')
            channel_id = channel_config.get('channel_id')
            token_file = channel_config.get('token_file')

            # Validate channel configuration
            if not channel_id:
                logger.error(f"[{channel_name}] Missing channel_id, skipping this channel")
                continue

            if not token_file:
                logger.error(f"[{channel_name}] Missing token_file, skipping this channel")
                continue

            logger.info("=" * 60)
            logger.info(f"Initializing channel: {channel_name}")
            logger.info(f"  Channel ID: {channel_id}")
            logger.info(f"  Token file: {token_file}")

            try:
                # Initialize YouTube client with channel-specific token
                yt_client = YouTubeClient(token_file=token_file)

                # Verify authentication matches expected channel
                auth_info = yt_client.get_authenticated_channel_info()

                if not auth_info:
                    logger.error(f"[{channel_name}] Failed to get authenticated channel info, skipping")
                    continue

                auth_channel_id = auth_info['id']
                auth_channel_title = auth_info['title']

                logger.info(f"  Authenticated as: {auth_channel_title} ({auth_channel_id})")

                # Verify channel ID matches
                if auth_channel_id != channel_id:
                    logger.error("=" * 60)
                    logger.error(f"[{channel_name}] AUTHENTICATION MISMATCH!")
                    logger.error(f"  Expected channel ID: {channel_id}")
                    logger.error(f"  Authenticated channel ID: {auth_channel_id}")
                    logger.error(f"  Authenticated channel name: {auth_channel_title}")
                    logger.error(f"  Token file: {token_file}")
                    logger.error("  Please re-authenticate with the correct account or update channel_id in config.py")
                    logger.error("=" * 60)
                    continue

                logger.info(f"  [OK] Authentication verified for {channel_name}")

                # Store the client with its configuration
                channel_clients.append({
                    'name': channel_name,
                    'channel_id': channel_id,
                    'client': yt_client
                })

            except FileNotFoundError as e:
                logger.error(f"[{channel_name}] Configuration error: {e}")
                logger.error("Please ensure client_secret.json is in the current directory.")
                continue
            except Exception as e:
                logger.error(f"[{channel_name}] Error initializing YouTube client: {e}")
                continue

        logger.info("=" * 60)

        if not channel_clients:
            logger.error("ERROR: No channels were successfully initialized!")
            logger.error("Please check your configuration and authentication.")
            sys.exit(1)

        logger.info(f"Successfully initialized {len(channel_clients)} channel(s)")
        for channel_info in channel_clients:
            logger.info(f"  - {channel_info['name']} ({channel_info['channel_id']})")

    except Exception as e:
        logger.error(f"Error initializing application: {e}")
        sys.exit(1)

    # Main polling loop
    logger.info("=" * 60)
    logger.info("Starting polling loop...")
    logger.info("=" * 60)

    try:
        while True:
            try:
                logger.info("")
                logger.info(">>>>> Starting new polling cycle for all channels <<<<<")
                logger.info("")

                # Process each channel
                for channel_info in channel_clients:
                    channel_name = channel_info['name']
                    channel_id = channel_info['channel_id']
                    yt_client = channel_info['client']

                    try:
                        check_for_new_videos(yt_client, state, channel_id, channel_name)
                    except Exception as e:
                        logger.error(f"[{channel_name}] Error checking for new videos: {e}")

                logger.info("")
                logger.info("<<<<< Finished polling cycle for all channels >>>>>")
                logger.info("")

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
