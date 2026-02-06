"""State management for tracking processed videos."""

import json
import os
import logging
from typing import Set, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """Manages the state of processed videos."""
    
    def __init__(self, state_file: str):
        """Initialize the state manager.
        
        Args:
            state_file: Path to the JSON state file.
        """
        self.state_file = state_file
        self.last_seen_videos: Set[str] = set()
        self.last_check_time: Optional[str] = None
        self.load_state()
    
    def load_state(self) -> None:
        """Load state from JSON file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.last_seen_videos = set(data.get('last_seen_videos', []))
                    self.last_check_time = data.get('last_check_time')
                logger.info(f"Loaded state with {len(self.last_seen_videos)} tracked videos")
            except Exception as e:
                logger.error(f"Error loading state: {e}")
                self.last_seen_videos = set()
                self.last_check_time = None
        else:
            logger.info("No existing state file found, starting fresh")
    
    def save_state(self) -> None:
        """Save state to JSON file."""
        try:
            data = {
                'last_seen_videos': list(self.last_seen_videos),
                'last_check_time': self.last_check_time
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"State saved with {len(self.last_seen_videos)} tracked videos")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def is_video_seen(self, video_id: str) -> bool:
        """Check if a video has been seen before.
        
        Args:
            video_id: YouTube video ID.
            
        Returns:
            True if video has been seen, False otherwise.
        """
        return video_id in self.last_seen_videos
    
    def mark_video_seen(self, video_id: str) -> None:
        """Mark a video as seen.
        
        Args:
            video_id: YouTube video ID.
        """
        self.last_seen_videos.add(video_id)
        self.last_check_time = datetime.utcnow().isoformat()
        self.save_state()
    
    def get_last_check_time(self) -> Optional[str]:
        """Get the last check time.
        
        Returns:
            ISO format timestamp or None if never checked.
        """
        return self.last_check_time
