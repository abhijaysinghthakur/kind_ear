"""Matching routes."""
from flask import Blueprint, request, jsonify
from ..middleware.auth import jwt_required_custom, role_required
from ..services.matching_service import MatchingService
from ..models.chat import ChatSession
from ..models.user import User
from ..extensions import socketio

bp = Blueprint('match', __name__)


@bp.route('/find-listeners', methods=['POST'])
@jwt_required_custom
@role_required('sharer')
def find_listeners(current_user):
    """Get top 3 suggested listeners based on preferences."""
    data = request.get_json() or {}

    preferences = {
        'topic': data.get('topic'),
        'language': data.get('language'),
        'preferred_min_rating': data.get('preferred_min_rating')
    }

    # Find matches
    matches = MatchingService.find_matches(current_user['_id'], preferences)

    if not matches:
        return jsonify({
            'matches': [],
            'message': 'No available listeners match your preferences right now. Please try again later.'
        }), 200

    return jsonify({'matches': matches}), 200


@bp.route('/request-chat', methods=['POST'])
@jwt_required_custom
@role_required('sharer')
def request_chat(current_user):
    """Sharer requests chat with specific listener."""
    data = request.get_json()

    if not data or 'listener_id' not in data:
        return jsonify({'error': 'listener_id required'}), 400

    listener_id = data['listener_id']
    topic = data.get('topic')

    # Check if sharer already has active chat
    active_session = ChatSession.find_active_by_user(current_user['_id'])
    if active_session:
        return jsonify({'error': 'You already have an active chat session'}), 409

    # Verify listener exists and is available
    listener = User.find_by_id(listener_id)
    if not listener:
        return jsonify({'error': 'Listener not found'}), 404

    if listener.get('listener_availability') != 'available':
        return jsonify({'error': 'Listener is not available'}), 400

    if not listener.get('is_active', True):
        return jsonify({'error': 'Listener account is inactive'}), 400

    # Check if listener has active chat
    listener_active_session = ChatSession.find_active_by_user(listener_id)
    if listener_active_session:
        return jsonify({'error': 'Listener is currently in another chat'}), 409

    # Create chat session
    language = current_user.get('languages', ['English'])[0]  # Use first language
    session = ChatSession.create(
        sharer_id=current_user['_id'],
        listener_id=listener_id,
        topic=topic,
        language=language
    )

    # Update listener availability to in_chat
    User.update_availability(listener_id, 'in_chat')

    # Send Socket.IO notification to listener
    socketio.emit('chat_request', {
        'session_id': str(session['_id']),
        'sharer': {
            'id': str(current_user['_id']),
            'pseudonym': current_user['pseudonym']
        },
        'topic': topic
    }, room=str(listener_id))

    # Return session details
    return jsonify({
        'session_id': str(session['_id']),
        'listener': {
            'id': str(listener['_id']),
            'pseudonym': listener['pseudonym'],
            'profile_picture_url': listener.get('profile_picture_url')
        },
        'topic': topic,
        'started_at': session['started_at'].isoformat(),
        'status': 'active'
    }), 201
