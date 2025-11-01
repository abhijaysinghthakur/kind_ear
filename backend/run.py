"""Application entry point."""
import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Use socketio.run instead of app.run for Socket.IO support
    port = int(os.environ.get('PORT', 5000))
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
