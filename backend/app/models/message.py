"""Message model."""
from datetime import datetime, timedelta
from bson import ObjectId
from ..extensions import db


class Message:
    """Chat message model."""

    collection = db.messages

    @staticmethod
    def create(chat_session_id, sender_id, sender_role, content, moderation_status='approved'):
        """Create a new message."""
        if isinstance(chat_session_id, str):
            chat_session_id = ObjectId(chat_session_id)
        if isinstance(sender_id, str):
            sender_id = ObjectId(sender_id)

        message_doc = {
            'chat_session_id': chat_session_id,
            'sender_id': sender_id,
            'sender_role': sender_role,
            'content': content,
            'sent_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=24),
            'is_flagged': moderation_status == 'flagged',
            'moderation_status': moderation_status,
            'flagged_reason': None
        }

        result = Message.collection.insert_one(message_doc)
        message_doc['_id'] = result.inserted_id
        return message_doc

    @staticmethod
    def find_by_session(session_id, limit=50, before=None):
        """Find messages for a chat session with pagination."""
        if isinstance(session_id, str):
            session_id = ObjectId(session_id)

        query = {'chat_session_id': session_id}

        if before:
            if isinstance(before, str):
                before = ObjectId(before)
            query['_id'] = {'$lt': before}

        messages = list(
            Message.collection.find(query)
            .sort('sent_at', -1)
            .limit(limit)
        )
        messages.reverse()  # Return in chronological order
        return messages

    @staticmethod
    def flag_message(message_id, reason):
        """Flag a message for moderation."""
        if isinstance(message_id, str):
            message_id = ObjectId(message_id)

        Message.collection.update_one(
            {'_id': message_id},
            {'$set': {
                'is_flagged': True,
                'moderation_status': 'flagged',
                'flagged_reason': reason
            }}
        )

    @staticmethod
    def remove_message(message_id):
        """Remove a message (admin action)."""
        if isinstance(message_id, str):
            message_id = ObjectId(message_id)

        Message.collection.update_one(
            {'_id': message_id},
            {'$set': {'moderation_status': 'removed'}}
        )

    @staticmethod
    def to_dict(message_doc, current_user_id):
        """Convert message document to dictionary."""
        if not message_doc:
            return None

        return {
            'id': str(message_doc['_id']),
            'content': message_doc['content'],
            'sent_at': message_doc['sent_at'].isoformat(),
            'is_own_message': str(message_doc['sender_id']) == str(current_user_id),
            'sender_role': message_doc['sender_role']
        }
