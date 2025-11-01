"""Chat routes."""
from flask import Blueprint, request, jsonify
from ..middleware.auth import jwt_required_custom
from ..models.chat import ChatSession
from ..models.message import Message
from ..models.user import User
from ..extensions import socketio

bp = Blueprint('chat', __name__)


@bp.route('/sessions/active', methods=['GET'])
@jwt_required_custom
def get_active_session(current_user):
    """Get user's current active chat session."""
    session = ChatSession.find_active_by_user(current_user['_id'])

    if not session:
        return jsonify({'session_id': None}), 200

    # Determine partner (the other person in chat)
    is_sharer = str(session['sharer_id']) == str(current_user['_id'])
    partner_id = session['listener_id'] if is_sharer else session['sharer_id']
    partner = User.find_by_id(partner_id)

    return jsonify({
        'session_id': str(session['_id']),
        'partner': {
            'id': str(partner['_id']),
            'pseudonym': partner['pseudonym'],
            'profile_picture_url': partner.get('profile_picture_url'),
            'role': 'listener' if is_sharer else 'sharer'
        },
        'topic': session.get('topic'),
        'started_at': session['started_at'].isoformat(),
        'user_role': 'sharer' if is_sharer else 'listener'
    }), 200


@bp.route('/sessions/<session_id>/messages', methods=['GET'])
@jwt_required_custom
def get_messages(current_user, session_id):
    """Get messages for specific chat session."""
    # Verify session exists
    session = ChatSession.find_by_id(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Verify user is participant
    user_id_str = str(current_user['_id'])
    if user_id_str not in [str(session['sharer_id']), str(session['listener_id'])]:
        return jsonify({'error': 'You are not a participant in this session'}), 403

    # Get pagination params
    limit = min(int(request.args.get('limit', 50)), 200)
    before = request.args.get('before')

    # Get messages
    messages = Message.find_by_session(session_id, limit=limit, before=before)

    # Get partner info for pseudonym
    partner_id = session['listener_id'] if str(session['sharer_id']) == user_id_str else session['sharer_id']
    partner = User.find_by_id(partner_id)

    # Format messages
    formatted_messages = []
    for msg in messages:
        is_own = str(msg['sender_id']) == user_id_str
        sender_pseudonym = current_user['pseudonym'] if is_own else partner['pseudonym']

        formatted_messages.append({
            'id': str(msg['_id']),
            'sender_pseudonym': sender_pseudonym,
            'content': msg['content'],
            'sent_at': msg['sent_at'].isoformat(),
            'is_own_message': is_own
        })

    has_more = len(messages) == limit

    return jsonify({
        'messages': formatted_messages,
        'has_more': has_more
    }), 200


@bp.route('/sessions/<session_id>/end', methods=['POST'])
@jwt_required_custom
def end_chat(current_user, session_id):
    """End active chat session."""
    # Verify session exists
    session = ChatSession.find_by_id(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Verify user is participant
    user_id_str = str(current_user['_id'])
    if user_id_str not in [str(session['sharer_id']), str(session['listener_id'])]:
        return jsonify({'error': 'You are not a participant in this session'}), 403

    # Verify session is active
    if session['status'] != 'active':
        return jsonify({'error': 'Session already ended'}), 400

    # End session
    result = ChatSession.end_session(session_id)

    # Update listener availability if they are a listener
    sharer_id = str(session['sharer_id'])
    listener_id = str(session['listener_id'])

    listener = User.find_by_id(listener_id)
    if listener and 'listener' in listener.get('roles', []):
        User.update_availability(listener_id, 'available')
        # Increment chat count for listener
        User.increment_chat_count(listener_id)

    # Send Socket.IO notification to both participants
    socketio.emit('chat_ended', {
        'session_id': session_id,
        'ended_by': user_id_str,
        'feedback_required': True
    }, room=sharer_id)

    socketio.emit('chat_ended', {
        'session_id': session_id,
        'ended_by': user_id_str,
        'feedback_required': True
    }, room=listener_id)

    return jsonify({
        'message': 'Chat ended successfully',
        'session_id': result['session_id'],
        'duration_minutes': result['duration_minutes']
    }), 200
