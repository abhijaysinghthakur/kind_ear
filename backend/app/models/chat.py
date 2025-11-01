"""Chat session model."""
from datetime import datetime, timedelta
from bson import ObjectId
from ..extensions import db


class ChatSession:
    """Chat session model."""

    collection = db.chat_sessions

    @staticmethod
    def create(sharer_id, listener_id, topic=None, language=None):
        """Create a new chat session."""
        if isinstance(sharer_id, str):
            sharer_id = ObjectId(sharer_id)
        if isinstance(listener_id, str):
            listener_id = ObjectId(listener_id)

        session_doc = {
            'sharer_id': sharer_id,
            'listener_id': listener_id,
            'started_at': datetime.utcnow(),
            'ended_at': None,
            'status': 'active',
            'initiated_by': sharer_id,
            'expires_at': datetime.utcnow() + timedelta(hours=24),
            'topic': topic,
            'language': language
        }

        result = ChatSession.collection.insert_one(session_doc)
        session_doc['_id'] = result.inserted_id
        return session_doc

    @staticmethod
    def find_by_id(session_id):
        """Find chat session by ID."""
        if isinstance(session_id, str):
            session_id = ObjectId(session_id)
        return ChatSession.collection.find_one({'_id': session_id})

    @staticmethod
    def find_active_by_user(user_id):
        """Find active chat session for a user (as either sharer or listener)."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        return ChatSession.collection.find_one({
            '$or': [
                {'sharer_id': user_id},
                {'listener_id': user_id}
            ],
            'status': 'active'
        })

    @staticmethod
    def end_session(session_id):
        """End a chat session."""
        if isinstance(session_id, str):
            session_id = ObjectId(session_id)

        session = ChatSession.find_by_id(session_id)
        if not session:
            return None

        started_at = session['started_at']
        ended_at = datetime.utcnow()
        duration = (ended_at - started_at).total_seconds() / 60  # in minutes

        ChatSession.collection.update_one(
            {'_id': session_id},
            {'$set': {
                'status': 'ended',
                'ended_at': ended_at
            }}
        )

        return {
            'session_id': str(session_id),
            'duration_minutes': int(duration)
        }

    @staticmethod
    def get_recent_partners(user_id, hours=24):
        """Get list of users this user chatted with in last N hours."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        sessions = ChatSession.collection.find({
            '$or': [
                {'sharer_id': user_id},
                {'listener_id': user_id}
            ],
            'started_at': {'$gte': cutoff_time}
        })

        partner_ids = set()
        for session in sessions:
            if session['sharer_id'] == user_id:
                partner_ids.add(session['listener_id'])
            else:
                partner_ids.add(session['sharer_id'])

        return list(partner_ids)

    @staticmethod
    def to_dict(session_doc):
        """Convert session document to dictionary."""
        if not session_doc:
            return None

        return {
            'session_id': str(session_doc['_id']),
            'sharer_id': str(session_doc['sharer_id']),
            'listener_id': str(session_doc['listener_id']),
            'started_at': session_doc['started_at'].isoformat(),
            'ended_at': session_doc['ended_at'].isoformat() if session_doc.get('ended_at') else None,
            'status': session_doc['status'],
            'topic': session_doc.get('topic'),
            'language': session_doc.get('language')
        }
