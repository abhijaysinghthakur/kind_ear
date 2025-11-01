"""User model."""
from datetime import datetime
from bson import ObjectId
import bcrypt
from ..extensions import db


class User:
    """User model for both Sharers and Listeners."""

    collection = db.users

    @staticmethod
    def create(data):
        """Create a new user."""
        user_doc = {
            'email': data['email'],
            'pseudonym': data['pseudonym'],
            'roles': data['roles'],
            'oauth_provider': data.get('oauth_provider'),
            'oauth_id': data.get('oauth_id'),
            'real_name': data.get('real_name'),
            'bio': data.get('bio', ''),
            'profile_picture_url': data.get('profile_picture_url'),
            'interests': data.get('interests', []),
            'languages': data.get('languages', []),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'is_admin': data.get('is_admin', False),
            'listener_availability': 'unavailable',
            'listener_rating': 0.0,
            'listener_total_chats': 0,
            'listener_topics': data.get('listener_topics', []),
            'privacy_settings': {
                'show_profile_picture': True,
                'allow_feedback': True
            }
        }

        # Hash password if provided (for email/password users)
        if 'password' in data:
            user_doc['password_hash'] = User.hash_password(data['password'])

        result = User.collection.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return user_doc

    @staticmethod
    def find_by_id(user_id):
        """Find user by ID."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return User.collection.find_one({'_id': user_id})

    @staticmethod
    def find_by_email(email):
        """Find user by email."""
        return User.collection.find_one({'email': email})

    @staticmethod
    def find_by_pseudonym(pseudonym):
        """Find user by pseudonym."""
        return User.collection.find_one({'pseudonym': pseudonym})

    @staticmethod
    def find_by_oauth(provider, oauth_id):
        """Find user by OAuth provider and ID."""
        return User.collection.find_one({
            'oauth_provider': provider,
            'oauth_id': oauth_id
        })

    @staticmethod
    def update(user_id, data):
        """Update user information."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        update_data = {**data, 'updated_at': datetime.utcnow()}
        User.collection.update_one(
            {'_id': user_id},
            {'$set': update_data}
        )
        return User.find_by_id(user_id)

    @staticmethod
    def update_availability(user_id, availability):
        """Update listener availability status."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        User.collection.update_one(
            {'_id': user_id},
            {'$set': {
                'listener_availability': availability,
                'updated_at': datetime.utcnow()
            }}
        )

    @staticmethod
    def update_rating(user_id, new_rating):
        """Update listener rating (called after new feedback)."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        User.collection.update_one(
            {'_id': user_id},
            {'$set': {
                'listener_rating': new_rating,
                'updated_at': datetime.utcnow()
            }}
        )

    @staticmethod
    def increment_chat_count(user_id):
        """Increment listener's total chat count."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        User.collection.update_one(
            {'_id': user_id},
            {'$inc': {'listener_total_chats': 1}}
        )

    @staticmethod
    def ban(user_id):
        """Ban a user (set is_active to False)."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        User.collection.update_one(
            {'_id': user_id},
            {'$set': {
                'is_active': False,
                'updated_at': datetime.utcnow()
            }}
        )

    @staticmethod
    def unban(user_id):
        """Unban a user (set is_active to True)."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        User.collection.update_one(
            {'_id': user_id},
            {'$set': {
                'is_active': True,
                'updated_at': datetime.utcnow()
            }}
        )

    @staticmethod
    def find_available_listeners(filters=None):
        """Find available listeners with optional filters."""
        query = {
            'roles': 'listener',
            'listener_availability': 'available',
            'is_active': True
        }

        if filters:
            if 'language' in filters:
                query['languages'] = filters['language']
            if 'min_rating' in filters:
                query['listener_rating'] = {'$gte': filters['min_rating']}

        return list(User.collection.find(query))

    @staticmethod
    def get_all(filters=None, page=1, limit=20):
        """Get all users with pagination and optional filters."""
        query = {}

        if filters:
            if 'role' in filters:
                query['roles'] = filters['role']
            if 'is_active' in filters:
                query['is_active'] = filters['is_active']
            if 'search' in filters:
                query['$or'] = [
                    {'pseudonym': {'$regex': filters['search'], '$options': 'i'}},
                    {'email': {'$regex': filters['search'], '$options': 'i'}}
                ]

        skip = (page - 1) * limit
        users = list(User.collection.find(query).skip(skip).limit(limit))
        total = User.collection.count_documents(query)

        return users, total

    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def to_dict(user_doc, include_sensitive=False):
        """Convert user document to dictionary."""
        if not user_doc:
            return None

        result = {
            'id': str(user_doc['_id']),
            'email': user_doc['email'],
            'pseudonym': user_doc['pseudonym'],
            'real_name': user_doc.get('real_name'),
            'bio': user_doc.get('bio', ''),
            'profile_picture_url': user_doc.get('profile_picture_url'),
            'roles': user_doc['roles'],
            'interests': user_doc.get('interests', []),
            'languages': user_doc.get('languages', []),
            'listener_availability': user_doc.get('listener_availability'),
            'listener_rating': user_doc.get('listener_rating', 0.0),
            'listener_total_chats': user_doc.get('listener_total_chats', 0),
            'listener_topics': user_doc.get('listener_topics', []),
            'privacy_settings': user_doc.get('privacy_settings', {}),
            'created_at': user_doc['created_at'].isoformat() if user_doc.get('created_at') else None,
            'is_active': user_doc.get('is_active', True),
            'is_admin': user_doc.get('is_admin', False)
        }

        if not include_sensitive:
            # Remove sensitive fields for public view
            pass

        return result
