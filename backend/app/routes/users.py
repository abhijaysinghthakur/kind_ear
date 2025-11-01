"""User profile routes."""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from ..middleware.auth import jwt_required_custom, role_required
from ..models.user import User
from ..extensions import socketio

bp = Blueprint('users', __name__)


@bp.route('/me', methods=['GET'])
@jwt_required_custom
def get_current_user(current_user):
    """Get current user's profile."""
    return jsonify(User.to_dict(current_user)), 200


@bp.route('/me', methods=['PATCH'])
@jwt_required_custom
def update_profile(current_user):
    """Update current user's profile."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Check if pseudonym is being changed and is unique
    if 'pseudonym' in data:
        if data['pseudonym'] != current_user['pseudonym']:
            existing = User.find_by_pseudonym(data['pseudonym'])
            if existing:
                return jsonify({'error': 'Pseudonym already taken'}), 409

    # Validate bio length
    if 'bio' in data and len(data['bio']) > 500:
        return jsonify({'error': 'Bio must be 500 characters or less'}), 400

    # Fields allowed to update
    allowed_fields = [
        'pseudonym', 'real_name', 'bio', 'interests', 'languages',
        'listener_topics', 'privacy_settings'
    ]

    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    # Update user
    updated_user = User.update(current_user['_id'], update_data)

    return jsonify(User.to_dict(updated_user)), 200


@bp.route('/me/avatar', methods=['POST'])
@jwt_required_custom
def upload_avatar(current_user):
    """Upload profile picture."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check file extension
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

    if ext not in allowed_extensions:
        return jsonify({'error': 'Invalid file format. Allowed: jpg, jpeg, png, gif'}), 400

    # Check file size (5MB max)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > 5 * 1024 * 1024:  # 5MB
        return jsonify({'error': 'File too large. Maximum size is 5MB'}), 413

    # Save file
    from flask import current_app
    filename = secure_filename(f"{current_user['_id']}.{ext}")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    file.save(filepath)

    # Update user profile with new picture URL
    picture_url = f"/uploads/avatars/{filename}"
    User.update(current_user['_id'], {'profile_picture_url': picture_url})

    return jsonify({'profile_picture_url': picture_url}), 200


@bp.route('/me/availability', methods=['PATCH'])
@jwt_required_custom
@role_required('listener')
def update_availability(current_user):
    """Update listener availability status."""
    data = request.get_json()

    if not data or 'availability' not in data:
        return jsonify({'error': 'Availability status required'}), 400

    availability = data['availability']
    allowed_statuses = ['available', 'unavailable', 'in_chat']

    if availability not in allowed_statuses:
        return jsonify({'error': f'Invalid status. Allowed: {", ".join(allowed_statuses)}'}), 400

    # Update availability
    User.update_availability(current_user['_id'], availability)

    # Broadcast status change via Socket.IO
    socketio.emit('listener_status_update', {
        'listener_id': str(current_user['_id']),
        'availability': availability
    }, room='matching_queue')

    return jsonify({'listener_availability': availability}), 200
