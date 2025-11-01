"""Socket.IO status event handlers."""
from flask import request
from flask_socketio import emit, join_room
from flask_jwt_extended import decode_token
from ..extensions import socketio
from ..models.user import User


@socketio.on('join_matching_queue')
def handle_join_matching_queue():
    """Join the matching queue room to receive listener status updates."""
    try:
        auth = request.args.get('token')
        decoded = decode_token(auth)
        user_id = decoded['sub']

        # Verify user
        user = User.find_by_id(user_id)
        if not user:
            return

        # Join matching queue room
        join_room('matching_queue')
        print(f"User {user_id} joined matching queue")

    except Exception as e:
        print(f"Error joining matching queue: {str(e)}")


@socketio.on('status_change')
def handle_status_change(data):
    """Handle listener availability status change."""
    try:
        auth = request.args.get('token')
        decoded = decode_token(auth)
        user_id = decoded['sub']

        # Verify user is a listener
        user = User.find_by_id(user_id)
        if not user or 'listener' not in user.get('roles', []):
            emit('error', {'message': 'User is not a listener'})
            return

        availability = data.get('availability')
        allowed_statuses = ['available', 'unavailable', 'in_chat']

        if availability not in allowed_statuses:
            emit('error', {'message': 'Invalid availability status'})
            return

        # Update availability
        User.update_availability(user_id, availability)

        # Broadcast to matching queue
        emit('listener_status_update', {
            'listener_id': str(user_id),
            'availability': availability
        }, room='matching_queue')

        print(f"Listener {user_id} status changed to {availability}")

    except Exception as e:
        emit('error', {'message': str(e)})
