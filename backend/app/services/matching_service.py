"""Matching service for connecting sharers with listeners."""
import random
from ..models.user import User
from ..models.chat import ChatSession


class MatchingService:
    """Handle matching algorithm logic."""

    @staticmethod
    def find_matches(sharer_id, preferences=None):
        """
        Find top 3 listener matches based on preferences.

        Args:
            sharer_id: ID of the sharer
            preferences: dict with optional fields:
                - topic: str
                - language: str
                - preferred_min_rating: float

        Returns:
            list of matched listeners with scores
        """
        if preferences is None:
            preferences = {}

        # Get all available listeners
        available_listeners = User.find_available_listeners()

        if not available_listeners:
            return []

        # Get recent chat partners (last 24 hours) to exclude
        recent_partners = ChatSession.get_recent_partners(sharer_id, hours=24)

        # Filter and score listeners
        scored_listeners = []

        for listener in available_listeners:
            listener_id = listener['_id']

            # Skip if chatted recently
            if listener_id in recent_partners:
                continue

            # Skip if listener is the sharer (same user)
            if str(listener_id) == str(sharer_id):
                continue

            # Apply filters from preferences
            if not MatchingService._matches_filters(listener, preferences):
                continue

            # Calculate match score
            score = MatchingService._calculate_score(listener, preferences)

            scored_listeners.append({
                'listener': listener,
                'score': score
            })

        # Sort by score and return top 3
        scored_listeners.sort(key=lambda x: x['score'], reverse=True)
        top_matches = scored_listeners[:3]

        # Format response
        return [
            {
                'id': str(match['listener']['_id']),
                'pseudonym': match['listener']['pseudonym'],
                'bio': match['listener'].get('bio', ''),
                'profile_picture_url': match['listener'].get('profile_picture_url'),
                'languages': match['listener'].get('languages', []),
                'listener_topics': match['listener'].get('listener_topics', []),
                'listener_rating': match['listener'].get('listener_rating', 0.0),
                'listener_total_chats': match['listener'].get('listener_total_chats', 0),
                'match_score': match['score']
            }
            for match in top_matches
        ]

    @staticmethod
    def _matches_filters(listener, preferences):
        """Check if listener matches the required filters."""
        # Language filter
        if 'language' in preferences and preferences['language']:
            listener_languages = listener.get('languages', [])
            if preferences['language'] not in listener_languages:
                return False

        # Minimum rating filter
        if 'preferred_min_rating' in preferences:
            min_rating = preferences['preferred_min_rating']
            listener_rating = listener.get('listener_rating', 0.0)
            if listener_rating < min_rating:
                return False

        return True

    @staticmethod
    def _calculate_score(listener, preferences):
        """
        Calculate match score for a listener.

        Scoring system:
        - Base score: 100
        - Topic match (exact in listener_topics): +50
        - Topic match (in interests): +25
        - Language match: +30
        - Rating bonus: (listener_rating - 3.0) * 10
        - Experience bonus: min(listener_total_chats / 10, 20)
        - Random factor: +/- 10 (for variety)
        """
        score = 100

        # Topic matching
        if 'topic' in preferences and preferences['topic']:
            topic = preferences['topic'].lower()
            listener_topics = [t.lower() for t in listener.get('listener_topics', [])]
            listener_interests = [i.lower() for i in listener.get('interests', [])]

            if topic in listener_topics:
                score += 50  # Exact topic match
            elif topic in listener_interests:
                score += 25  # Interest match

        # Language matching
        if 'language' in preferences and preferences['language']:
            listener_languages = listener.get('languages', [])
            if preferences['language'] in listener_languages:
                score += 30

        # Rating bonus
        listener_rating = listener.get('listener_rating', 0.0)
        rating_bonus = (listener_rating - 3.0) * 10
        score += max(rating_bonus, 0)  # Only positive bonus

        # Experience bonus
        total_chats = listener.get('listener_total_chats', 0)
        experience_bonus = min(total_chats / 10, 20)
        score += experience_bonus

        # Random factor for variety
        random_factor = random.randint(-10, 10)
        score += random_factor

        return int(score)
