"""YouTube API client for AutoChatter."""

import logging
import time
import pickle
import os
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import config

logger = logging.getLogger(__name__)


class YouTubeClient:
    """YouTube API client with OAuth authentication."""
    
    def __init__(self):
        """Initialize the YouTube client."""
        self.youtube = None
        self.authenticate()
    
    def authenticate(self) -> None:
        """Authenticate with YouTube API using OAuth 2.0."""
        credentials = None
        
        # Load token from file if it exists
        if os.path.exists(config.TOKEN_FILE):
            try:
                with open(config.TOKEN_FILE, 'rb') as token:
                    credentials = pickle.load(token)
                logger.info("Loaded credentials from token file")
            except Exception as e:
                logger.error(f"Error loading credentials: {e}")
        
        # If there are no (valid) credentials, let the user log in
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    logger.info("Refreshed expired credentials")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    credentials = None
            
            if not credentials:
                if not os.path.exists(config.CLIENT_SECRETS_FILE):
                    raise FileNotFoundError(
                        f"Client secrets file not found: {config.CLIENT_SECRETS_FILE}\n"
                        "Please download your OAuth 2.0 credentials from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CLIENT_SECRETS_FILE,
                    config.SCOPES
                )
                credentials = flow.run_local_server(port=0)
                logger.info("Completed OAuth authentication flow")
            
            # Save the credentials for the next run
            with open(config.TOKEN_FILE, 'wb') as token:
                pickle.dump(credentials, token)
                logger.info("Saved credentials to token file")
        
        self.youtube = build(
            config.YOUTUBE_API_SERVICE_NAME,
            config.YOUTUBE_API_VERSION,
            credentials=credentials
        )
        logger.info("YouTube API client initialized")
    
    def get_channel_uploads(self, channel_id: str, max_results: int = 5) -> List[Dict]:
        """Fetch recent uploads from a channel.
        
        Args:
            channel_id: YouTube channel ID.
            max_results: Maximum number of videos to fetch.
            
        Returns:
            List of video dictionaries with id and details.
        """
        try:
            # Get the uploads playlist ID
            channels_response = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            ).execute()
            
            if not channels_response.get('items'):
                logger.warning(f"Channel not found: {channel_id}")
                return []
            
            uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()
            
            videos = []
            for item in playlist_response.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                video_title = item['snippet']['title']
                published_at = item['snippet']['publishedAt']
                
                videos.append({
                    'id': video_id,
                    'title': video_title,
                    'published_at': published_at
                })
            
            logger.info(f"Fetched {len(videos)} videos from channel {channel_id}")
            return videos
            
        except HttpError as e:
            logger.error(f"HTTP error fetching channel uploads: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching channel uploads: {e}")
            return []
    
    def get_video_duration(self, video_id: str) -> Optional[int]:
        """Get video duration in seconds.
        
        Args:
            video_id: YouTube video ID.
            
        Returns:
            Duration in seconds, or None if error.
        """
        try:
            video_response = self.youtube.videos().list(
                part="contentDetails",
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                return None
            
            duration_str = video_response['items'][0]['contentDetails']['duration']
            # Parse ISO 8601 duration format (PT1M30S -> 90 seconds)
            duration = self._parse_duration(duration_str)
            return duration
            
        except Exception as e:
            logger.error(f"Error fetching video duration for {video_id}: {e}")
            return None
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds.
        
        Args:
            duration: ISO 8601 duration string (e.g., PT1M30S).
            
        Returns:
            Duration in seconds.
        """
        import re
        
        # Remove PT prefix
        duration = duration.replace('PT', '')
        
        # Extract hours, minutes, seconds
        hours = 0
        minutes = 0
        seconds = 0
        
        h_match = re.search(r'(\d+)H', duration)
        if h_match:
            hours = int(h_match.group(1))
        
        m_match = re.search(r'(\d+)M', duration)
        if m_match:
            minutes = int(m_match.group(1))
        
        s_match = re.search(r'(\d+)S', duration)
        if s_match:
            seconds = int(s_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds
    
    def post_comment(self, video_id: str, comment_text: str) -> bool:
        """Post a comment on a video with retry logic.
        
        Args:
            video_id: YouTube video ID.
            comment_text: Comment text to post.
            
        Returns:
            True if comment posted successfully, False otherwise.
        """
        retries = 0
        backoff = config.INITIAL_BACKOFF
        
        while retries < config.MAX_RETRIES:
            try:
                request = self.youtube.commentThreads().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "topLevelComment": {
                                "snippet": {
                                    "textOriginal": comment_text
                                }
                            }
                        }
                    }
                )
                response = request.execute()
                logger.info(f"Successfully posted comment on video {video_id}")
                return True
                
            except HttpError as e:
                status_code = e.resp.status
                
                # Handle rate limiting (429) and server errors (5xx)
                if status_code == 429 or status_code >= 500:
                    retries += 1
                    if retries < config.MAX_RETRIES:
                        logger.warning(
                            f"HTTP {status_code} error, retrying in {backoff}s "
                            f"(attempt {retries}/{config.MAX_RETRIES})"
                        )
                        time.sleep(backoff)
                        backoff = min(backoff * 2, config.MAX_BACKOFF)  # Exponential backoff
                    else:
                        logger.error(
                            f"Failed to post comment after {config.MAX_RETRIES} retries: {e}"
                        )
                        return False
                else:
                    # Other HTTP errors (e.g., 403 forbidden, 404 not found)
                    logger.error(f"HTTP error posting comment on video {video_id}: {e}")
                    return False
                    
            except Exception as e:
                logger.error(f"Unexpected error posting comment on video {video_id}: {e}")
                return False
        
        return False
    
    def is_short(self, video_id: str) -> bool:
        """Check if a video is a Short (duration <= 60 seconds).
        
        Args:
            video_id: YouTube video ID.
            
        Returns:
            True if video is a Short, False otherwise.
        """
        duration = self.get_video_duration(video_id)
        if duration is None:
            return False
        
        return duration <= config.MAX_SHORTS_DURATION
