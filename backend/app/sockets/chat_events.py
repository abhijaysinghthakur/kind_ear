"""Socket.IO chat event handlers."""
from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from ..extensions import socketio
from ..models.user import User
from ..models.chat import ChatSession
from ..models.message import Message
from ..services.moderation_service import ModerationService


@socketio.on('connect')
def handle_connect():
    """Handle client connection and authentication."""
    try:
        # Get token from auth
        auth = request.args.get('token') or (request.headers.get('Authorization') or '').replace('Bearer ', '')

        if not auth:
            return False  # Reject connection

        # Decode JWT
        decoded = decode_token(auth)
        user_id = decoded['sub']

        # Verify user exists
        user = User.find_by_id(user_id)
        if not user or not user.get('is_active', True):
            return False

        # Join user to their personal room (for targeted events)
        join_room(user_id)

        print(f"User {user_id} connected to Socket.IO")
        return True

    except Exception as e:
        print(f"Connection error: {str(e)}")
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print("Client disconnected")


@socketio.on('join_chat')
def handle_join_chat(data):
    """User joins a chat room."""
    try:
        # Get user from token (similar to connect)
        auth = request.args.get('token')
        decoded = decode_token(auth)
        user_id = decoded['sub']

        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'session_id required'})
            return

        # Verify user is participant
        session = ChatSession.find_by_id(session_id)
        if not session:
            emit('error', {'message': 'Session not found'})
            return

        if str(user_id) not in [str(session['sharer_id']), str(session['listener_id'])]:
            emit('error', {'message': 'Not a participant'})
            return

        # Join chat room
        room = f"chat_{session_id}"
        join_room(room)

        # Notify other participant
        user = User.find_by_id(user_id)
        emit('user_joined', {
            'pseudonym': user['pseudonym']
        }, room=room, skip_sid=request.sid)

        print(f"User {user_id} joined chat {session_id}")

    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('send_message')
def handle_send_message(data):
    """Handle message sending."""
    try:
        # Get user
        auth = request.args.get('token')
        decoded = decode_token(auth)
        user_id = decoded['sub']
        user = User.find_by_id(user_id)

        session_id = data.get('session_id')
        content = data.get('content')

        if not session_id or not content:
            emit('error', {'message': 'session_id and content required'})
            return

        # Validate content length
        if len(content) > 2000:
            emit('error', {'message': 'Message too long (max 2000 characters)'})
            return

        # Verify session and participant
        session = ChatSession.find_by_id(session_id)
        if not session or session['status'] != 'active':
            emit('error', {'message': 'Invalid or inactive session'})
            return

        if str(user_id) not in [str(session['sharer_id']), str(session['listener_id'])]:
            emit('error', {'message': 'Not a participant'})
            return

        # Moderate message
        if ModerationService.is_enabled():
            moderation_result = ModerationService.moderate_message(content)

            if moderation_result['status'] == 'blocked':
                emit('error', {
                    'message': f"Message blocked: {moderation_result['reason']}"
                })
                return

            moderation_status = moderation_result['status']
        else:
            moderation_status = 'approved'

        # Determine sender role
        sender_role = 'sharer' if str(user_id) == str(session['sharer_id']) else 'listener'

        # Save message
        message = Message.create(
            chat_session_id=session_id,
            sender_id=user_id,
            sender_role=sender_role,
            content=content,
            moderation_status=moderation_status
        )

        # Emit to chat room
        room = f"chat_{session_id}"
        emit('new_message', {
            'message_id': str(message['_id']),
            'sender_id': str(user_id),
            'sender_pseudonym': user['pseudonym'],
            'content': content,
            'sent_at': message['sent_at'].isoformat(),
            'is_own_message': False  # Will be determined by client
        }, room=room)

    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator."""
    try:
        # Get user
        auth = request.args.get('token')
        decoded = decode_token(auth)
        user_id = decoded['sub']
        user = User.find_by_id(user_id)

        session_id = data.get('session_id')
        if not session_id:
            return

        # Verify participant
        session = ChatSession.find_by_id(session_id)
        if not session:
            return

        if str(user_id) not in [str(session['sharer_id']), str(session['listener_id'])]:
            return

        # Emit to other participant only
        partner_id = str(session['listener_id']) if str(user_id) == str(session['sharer_id']) else str(session['sharer_id'])

        emit('user_typing', {
            'pseudonym': user['pseudonym']
        }, room=partner_id)

    except Exception as e:
        pass  # Silent fail for typing indicators


@socketio.on('leave_chat')
def handle_leave_chat(data):
    """User leaves chat room."""
    try:
        session_id = data.get('session_id')
        if session_id:
            room = f"chat_{session_id}"
            leave_room(room)

    except Exception as e:
        pass
