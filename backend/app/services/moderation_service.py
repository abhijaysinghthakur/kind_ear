"""Text moderation service with keyword filtering."""
import re


class ModerationService:
    """Handle content moderation for messages."""

    # Blocked keywords and patterns
    BLOCKED_PATTERNS = [
        # Phone numbers
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'phone number'),
        # Email addresses
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email address'),
        # Social media with usernames
        (r'\b(whatsapp|telegram|snapchat|instagram|facebook|twitter)\s*[@:]?\s*\w+', 'social media contact'),
        # Meeting requests
        (r'\b(meet me|my address|come to|visit me)\b', 'meeting request'),
    ]

    # Flagged keywords (allowed but logged)
    FLAGGED_KEYWORDS = [
        # Self-harm indicators
        'kill myself',
        'end it all',
        'suicide',
        'hurt myself',
        "can't go on",
        'want to die',
        'better off dead'
    ]

    @staticmethod
    def moderate_message(content):
        """
        Moderate message content.

        Returns:
            dict with:
                - status: 'approved', 'blocked', or 'flagged'
                - reason: str or None
        """
        if not content:
            return {'status': 'blocked', 'reason': 'Empty message'}

        content_lower = content.lower()

        # Check blocked patterns
        for pattern, reason in ModerationService.BLOCKED_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return {'status': 'blocked', 'reason': f'Contains {reason}'}

        # Check flagged keywords
        for keyword in ModerationService.FLAGGED_KEYWORDS:
            if keyword in content_lower:
                return {'status': 'flagged', 'reason': f'Contains concerning content: {keyword}'}

        # All clear
        return {'status': 'approved', 'reason': None}

    @staticmethod
    def is_enabled():
        """Check if moderation is enabled."""
        from flask import current_app
        return current_app.config.get('MODERATION_ENABLED', True)
