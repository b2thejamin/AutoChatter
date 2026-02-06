"""Comment templates for AutoChatter."""

import random
from typing import List

# Comment templates
COMMENT_TEMPLATES = [
    "Great video! Really enjoyed this content. 🎉",
    "Amazing work! Keep it up! 👏",
    "This is exactly what I was looking for! Thank you! 🙏",
    "Absolutely love your content! Can't wait for more! ❤️",
    "Incredible video! Very well done! 🌟",
    "This is so helpful! Thanks for sharing! 💯",
    "Wow, this is fantastic! Keep creating! 🚀",
    "Really appreciate this content! Well done! 👍",
    "Outstanding video! Very informative! 📚",
    "Love this! More content like this please! 🔥"
]


def get_random_comment(include_discord: bool = False, discord_link: str = "") -> str:
    """Get a random comment template.
    
    Args:
        include_discord: Whether to include the Discord link.
        discord_link: The Discord invite link to include.
        
    Returns:
        A random comment string.
    """
    comment = random.choice(COMMENT_TEMPLATES)
    
    if include_discord and discord_link:
        comment += f"\n\nJoin our community: {discord_link}"
    
    return comment


def should_include_discord(inclusion_rate: float) -> bool:
    """Determine if Discord link should be included based on rate.
    
    Args:
        inclusion_rate: Probability of including Discord link (0.0 to 1.0).
        
    Returns:
        True if Discord link should be included, False otherwise.
    """
    return random.random() < inclusion_rate


def get_all_templates() -> List[str]:
    """Get all available comment templates.
    
    Returns:
        List of all comment templates.
    """
    return COMMENT_TEMPLATES.copy()
