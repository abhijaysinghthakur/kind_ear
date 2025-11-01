"""Feedback routes."""
from flask import Blueprint, request, jsonify
from ..middleware.auth import jwt_required_custom
from ..models.feedback import Feedback
from ..models.chat import ChatSession
from ..models.user import User

bp = Blueprint('feedback', __name__)


@bp.route('', methods=['POST'])
@jwt_required_custom
def submit_feedback(current_user):
    """Submit feedback for chat partner after session ends."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Required fields
    required = ['chat_session_id', 'rating', 'helpfulness', 'empathy', 'safety']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    session_id = data['chat_session_id']
    rating = data['rating']
    helpfulness = data['helpfulness']
    empathy = data['empathy']
    safety = data['safety']
    comment = data.get('comment', '')

    # Validate ratings
    for value in [rating, helpfulness, empathy, safety]:
        if not isinstance(value, int) or value < 1 or value > 5:
            return jsonify({'error': 'Ratings must be integers between 1 and 5'}), 400

    # Validate comment length
    if comment and len(comment) > 500:
        return jsonify({'error': 'Comment must be 500 characters or less'}), 400

    # Verify session exists
    session = ChatSession.find_by_id(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Verify user is participant
    user_id_str = str(current_user['_id'])
    sharer_id_str = str(session['sharer_id'])
    listener_id_str = str(session['listener_id'])

    if user_id_str not in [sharer_id_str, listener_id_str]:
        return jsonify({'error': 'You are not a participant in this session'}), 403

    # Verify session is ended
    if session['status'] != 'ended':
        return jsonify({'error': 'Cannot submit feedback for active session'}), 400

    # Check if feedback already submitted
    if Feedback.exists_for_session_and_reviewer(session_id, current_user['_id']):
        return jsonify({'error': 'Feedback already submitted for this session'}), 400

    # Determine reviewee (the other person)
    reviewee_id = listener_id_str if user_id_str == sharer_id_str else sharer_id_str

    # Create feedback
    feedback = Feedback.create(
        chat_session_id=session_id,
        reviewer_id=current_user['_id'],
        reviewee_id=reviewee_id,
        rating=rating,
        helpfulness=helpfulness,
        empathy=empathy,
        safety=safety,
        comment=comment if comment else None
    )

    # Update reviewee's rating (recalculate average)
    new_avg_rating = Feedback.calculate_average_rating(reviewee_id)
    User.update_rating(reviewee_id, new_avg_rating)

    return jsonify({
        'message': 'Feedback submitted successfully',
        'feedback_id': str(feedback['_id'])
    }), 201
