"""Flask application factory."""
import os
from flask import Flask
from .config import config_by_name
from .extensions import jwt, cors, socketio, init_db


def create_app(config_name=None):
    """Create and configure Flask application."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    jwt.init_app(app)
    cors.init_app(
        app,
        origins=app.config['CORS_ORIGINS'],
        supports_credentials=True
    )
    socketio.init_app(
        app,
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'],
        message_queue=app.config['SOCKETIO_MESSAGE_QUEUE']
    )

    # Initialize database
    init_db(app)

    # Register blueprints
    from .routes import auth, users, match, chat, feedback, reports, admin_routes
    app.register_blueprint(auth.bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users.bp, url_prefix='/api/v1/users')
    app.register_blueprint(match.bp, url_prefix='/api/v1/match')
    app.register_blueprint(chat.bp, url_prefix='/api/v1/chat')
    app.register_blueprint(feedback.bp, url_prefix='/api/v1/feedback')
    app.register_blueprint(reports.bp, url_prefix='/api/v1/reports')
    app.register_blueprint(admin_routes.bp, url_prefix='/api/v1/admin')

    # Register Socket.IO events
    from .sockets import chat_events, status_events

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.logger.info(f'Application started in {config_name} mode')

    return app
