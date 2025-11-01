"""Feedback model."""
from datetime import datetime
from bson import ObjectId
from ..extensions import db


class Feedback:
    """Feedback model for post-chat ratings."""

    collection = db.feedback

    @staticmethod
    def create(chat_session_id, reviewer_id, reviewee_id, rating, helpfulness, empathy, safety, comment=None):
        """Create new feedback."""
        if isinstance(chat_session_id, str):
            chat_session_id = ObjectId(chat_session_id)
        if isinstance(reviewer_id, str):
            reviewer_id = ObjectId(reviewer_id)
        if isinstance(reviewee_id, str):
            reviewee_id = ObjectId(reviewee_id)

        feedback_doc = {
            'chat_session_id': chat_session_id,
            'reviewer_id': reviewer_id,
            'reviewee_id': reviewee_id,
            'rating': rating,
            'helpfulness': helpfulness,
            'empathy': empathy,
            'safety': safety,
            'comment': comment,
            'is_anonymous': True,
            'created_at': datetime.utcnow()
        }

        result = Feedback.collection.insert_one(feedback_doc)
        feedback_doc['_id'] = result.inserted_id
        return feedback_doc

    @staticmethod
    def find_by_session(session_id):
        """Find feedback for a chat session."""
        if isinstance(session_id, str):
            session_id = ObjectId(session_id)
        return list(Feedback.collection.find({'chat_session_id': session_id}))

    @staticmethod
    def exists_for_session_and_reviewer(session_id, reviewer_id):
        """Check if feedback already exists for this session from this reviewer."""
        if isinstance(session_id, str):
            session_id = ObjectId(session_id)
        if isinstance(reviewer_id, str):
            reviewer_id = ObjectId(reviewer_id)

        return Feedback.collection.find_one({
            'chat_session_id': session_id,
            'reviewer_id': reviewer_id
        }) is not None

    @staticmethod
    def calculate_average_rating(user_id):
        """Calculate average rating for a user (listener)."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        pipeline = [
            {'$match': {'reviewee_id': user_id}},
            {'$group': {
                '_id': None,
                'average_rating': {'$avg': '$rating'},
                'average_helpfulness': {'$avg': '$helpfulness'},
                'average_empathy': {'$avg': '$empathy'},
                'average_safety': {'$avg': '$safety'}
            }}
        ]

        result = list(Feedback.collection.aggregate(pipeline))
        if result:
            return result[0]['average_rating']
        return 0.0

    @staticmethod
    def to_dict(feedback_doc):
        """Convert feedback document to dictionary."""
        if not feedback_doc:
            return None

        return {
            'id': str(feedback_doc['_id']),
            'chat_session_id': str(feedback_doc['chat_session_id']),
            'rating': feedback_doc['rating'],
            'helpfulness': feedback_doc['helpfulness'],
            'empathy': feedback_doc['empathy'],
            'safety': feedback_doc['safety'],
            'comment': feedback_doc.get('comment'),
            'created_at': feedback_doc['created_at'].isoformat()
        }
