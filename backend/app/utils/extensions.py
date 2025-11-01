"""Initialize Flask extensions."""
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from pymongo import MongoClient
from redis import Redis

# Initialize extensions (will be configured in app factory)
jwt = JWTManager()
cors = CORS()
socketio = SocketIO(
    cors_allowed_origins='*',  # Will be configured in app factory
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)

# Database connections (will be initialized in app factory)
mongo_client = None
db = None
redis_client = None


def init_db(app):
    """Initialize database connections."""
    global mongo_client, db, redis_client

    # MongoDB
    mongo_client = MongoClient(app.config['MONGODB_URI'])
    db_name = app.config['MONGODB_URI'].split('/')[-1].split('?')[0]
    db = mongo_client[db_name]

    # Create indexes for performance
    _create_indexes(db)

    # Redis
    redis_client = Redis.from_url(app.config['REDIS_URL'], decode_responses=True)

    app.logger.info(f'Connected to MongoDB database: {db_name}')
    app.logger.info('Connected to Redis')


def _create_indexes(db):
    """Create database indexes for performance."""
    # Users collection
    db.users.create_index('email', unique=True)
    db.users.create_index('pseudonym', unique=True)
    db.users.create_index('listener_availability')
    db.users.create_index([('oauth_provider', 1), ('oauth_id', 1)], sparse=True)

    # Chat sessions collection
    db.chat_sessions.create_index('sharer_id')
    db.chat_sessions.create_index('listener_id')
    db.chat_sessions.create_index('status')
    db.chat_sessions.create_index('expires_at', expireAfterSeconds=0)  # TTL index

    # Messages collection
    db.messages.create_index('chat_session_id')
    db.messages.create_index('expires_at', expireAfterSeconds=0)  # TTL index

    # Feedback collection
    db.feedback.create_index('reviewee_id')
    db.feedback.create_index('chat_session_id')

    # Reports collection
    db.reports.create_index('status')
    db.reports.create_index('reported_user_id')

    # Admin logs collection
    db.admin_logs.create_index('timestamp')
    db.admin_logs.create_index('admin_id')
