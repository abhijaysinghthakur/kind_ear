"""Reports routes."""
from flask import Blueprint, request, jsonify
from ..middleware.auth import jwt_required_custom
from ..models.report import Report
from ..models.user import User

bp = Blueprint('reports', __name__)


@bp.route('', methods=['POST'])
@jwt_required_custom
def submit_report(current_user):
    """Report user or message for abuse."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Required fields
    if 'reported_user_id' not in data or 'reason' not in data or 'description' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    reported_user_id = data['reported_user_id']
    reason = data['reason']
    description = data['description']
    chat_session_id = data.get('chat_session_id')
    message_id = data.get('message_id')

    # Validate reason
    allowed_reasons = ['harassment', 'inappropriate', 'spam', 'safety_concern', 'other']
    if reason not in allowed_reasons:
        return jsonify({'error': f'Invalid reason. Allowed: {", ".join(allowed_reasons)}'}), 400

    # Validate description length
    if len(description) > 1000:
        return jsonify({'error': 'Description must be 1000 characters or less'}), 400

    # Verify reported user exists
    reported_user = User.find_by_id(reported_user_id)
    if not reported_user:
        return jsonify({'error': 'Reported user not found'}), 404

    # Create report
    report = Report.create(
        reporter_id=current_user['_id'],
        reported_user_id=reported_user_id,
        reason=reason,
        description=description,
        chat_session_id=chat_session_id,
        message_id=message_id
    )

    return jsonify({
        'message': 'Report submitted successfully',
        'report_id': str(report['_id'])
    }), 201
