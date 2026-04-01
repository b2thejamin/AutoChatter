"""Comment templates for AutoChatter."""

import random
from typing import List

# Discord invite link
DISCORD_LINK = "https://discord.gg/3MqnQBFmGp"

# Comment templates - all include {discord_link} placeholder
# Written from creator's perspective (commenting on own videos)
COMMENT_TEMPLATES = [
    "Join the Discord to chat with everyone! {discord_link}",
    "Come hang out in the Discord! {discord_link}",
    "Let's discuss this in the Discord: {discord_link}",
    "Join our Discord community here: {discord_link}",
    "Drop by the Discord and say hi! {discord_link}",
    "We're chatting about this in the Discord, join us: {discord_link}",
    "Connect with the community on Discord: {discord_link}",
    "Join the Discord for more content and discussions: {discord_link}",
    "Come join the Discord fam! {discord_link}",
    "Link up with us on Discord: {discord_link}",
    "Discord community link: {discord_link}",
    "Join our Discord server: {discord_link}",
    "Come vibe with us in the Discord! {discord_link}",
    "Check out the Discord community: {discord_link}",
    "Join the Discord to stay connected: {discord_link}",
    "Discord link for the community: {discord_link}",
    "Hop in the Discord! {discord_link}",
    "Come through to the Discord: {discord_link}",
    "Join us on Discord: {discord_link}",
    "Discord invite: {discord_link}"
]


def generate_comment() -> str:
    """Generate a random comment with Discord link.

    Returns:
        A random comment string with Discord link included.
    """
    template = random.choice(COMMENT_TEMPLATES)
    return template.format(discord_link=DISCORD_LINK)


# Deprecated functions kept for backwards compatibility
def get_random_comment(include_discord: bool = True, discord_link: str = "") -> str:
    """Get a random comment template.

    DEPRECATED: Use generate_comment() instead.

    Args:
        include_discord: Ignored - Discord link is always included.
        discord_link: Ignored - uses hardcoded Discord link.

    Returns:
        A random comment string with Discord link.
    """
    return generate_comment()


def should_include_discord(inclusion_rate: float) -> bool:
    """Determine if Discord link should be included.

    DEPRECATED: Discord link is now always included.

    Args:
        inclusion_rate: Ignored.

    Returns:
        Always returns True.
    """
    return True


def get_all_templates() -> List[str]:
    """Get all available comment templates.

    Returns:
        List of all comment templates with placeholders.
    """
    return COMMENT_TEMPLATES.copy()
