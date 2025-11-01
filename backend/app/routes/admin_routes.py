"""Admin routes."""
from flask import Blueprint, request, jsonify
from ..middleware.auth import jwt_required_custom, admin_required
from ..middleware.admin import admin_action_logged
from ..models.user import User
from ..models.chat import ChatSession
from ..models.report import Report
from ..extensions import db, socketio

bp = Blueprint('admin', __name__)


@bp.route('/stats', methods=['GET'])
@jwt_required_custom
@admin_required
def get_stats(current_user):
    """Get platform statistics."""
    # Count users
    total_users = db.users.count_documents({})
    total_sharers = db.users.count_documents({'roles': 'sharer'})
    total_listeners = db.users.count_documents({'roles': 'listener'})

    # Count active chats
    active_chats = db.chat_sessions.count_documents({'status': 'active'})

    # Count available listeners
    available_listeners = db.users.count_documents({
        'listener_availability': 'available',
        'is_active': True
    })

    # Count chats today
    from datetime import datetime, timedelta
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    total_chats_today = db.chat_sessions.count_documents({
        'started_at': {'$gte': today_start}
    })

    # Count total chats
    total_chats_all_time = db.chat_sessions.count_documents({})

    # Count pending reports
    pending_reports = Report.count_pending()

    # Calculate average rating
    pipeline = [
        {'$match': {'listener_rating': {'$gt': 0}}},
        {'$group': {
            '_id': None,
            'average_rating': {'$avg': '$listener_rating'}
        }}
    ]
    rating_result = list(db.users.aggregate(pipeline))
    average_rating = round(rating_result[0]['average_rating'], 1) if rating_result else 0.0

    return jsonify({
        'total_users': total_users,
        'total_sharers': total_sharers,
        'total_listeners': total_listeners,
        'active_chats': active_chats,
        'available_listeners': available_listeners,
        'total_chats_today': total_chats_today,
        'total_chats_all_time': total_chats_all_time,
        'pending_reports': pending_reports,
        'average_rating': average_rating
    }), 200


@bp.route('/users', methods=['GET'])
@jwt_required_custom
@admin_required
def get_users(current_user):
    """Get all users with filtering and pagination."""
    # Parse query parameters
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 20)), 100)

    filters = {}
    if request.args.get('role'):
        filters['role'] = request.args.get('role')
    if request.args.get('is_active'):
        filters['is_active'] = request.args.get('is_active').lower() == 'true'
    if request.args.get('search'):
        filters['search'] = request.args.get('search')

    # Get users
    users, total = User.get_all(filters, page, limit)

    # Format users
    formatted_users = [
        {
            'id': str(user['_id']),
            'email': user['email'],
            'pseudonym': user['pseudonym'],
            'roles': user['roles'],
            'is_active': user.get('is_active', True),
            'is_admin': user.get('is_admin', False),
            'listener_rating': user.get('listener_rating', 0.0),
            'listener_total_chats': user.get('listener_total_chats', 0),
            'created_at': user['created_at'].isoformat() if user.get('created_at') else None
        }
        for user in users
    ]

    pages = (total + limit - 1) // limit

    return jsonify({
        'users': formatted_users,
        'total': total,
        'page': page,
        'pages': pages
    }), 200


@bp.route('/users/<user_id>/ban', methods=['PATCH'])
@jwt_required_custom
@admin_required
@admin_action_logged('ban_user')
def ban_user(current_user, user_id):
    """Ban or unban user."""
    data = request.get_json()

    if not data or 'is_active' not in data:
        return jsonify({'error': 'is_active field required'}), 400

    is_active = data['is_active']
    reason = data.get('reason', '')

    # Verify user exists
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update user status
    if is_active:
        User.unban(user_id)
    else:
        User.ban(user_id)

        # End any active chat sessions
        active_session = ChatSession.find_active_by_user(user_id)
        if active_session:
            ChatSession.end_session(active_session['_id'])

        # Disconnect Socket.IO connection
        socketio.emit('account_banned', {
            'reason': reason
        }, room=user_id)

    action = 'unbanned' if is_active else 'banned'
    return jsonify({
        'message': f'User {action} successfully',
        'user_id': user_id
    }), 200


@bp.route('/reports', methods=['GET'])
@jwt_required_custom
@admin_required
def get_reports(current_user):
    """Get all reports with filtering."""
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))

    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args.get('status')

    # Get reports
    reports, total = Report.get_all(filters, page, limit)

    # Format reports with user info
    formatted_reports = []
    for report in reports:
        reporter = User.find_by_id(report['reporter_id'])
        reported_user = User.find_by_id(report['reported_user_id'])

        formatted_reports.append({
            'id': str(report['_id']),
            'reporter': {
                'id': str(reporter['_id']),
                'pseudonym': reporter['pseudonym']
            },
            'reported_user': {
                'id': str(reported_user['_id']),
                'pseudonym': reported_user['pseudonym']
            },
            'reason': report['reason'],
            'description': report['description'],
            'status': report['status'],
            'created_at': report['created_at'].isoformat()
        })

    pages = (total + limit - 1) // limit

    return jsonify({
        'reports': formatted_reports,
        'total': total,
        'page': page,
        'pages': pages
    }), 200


@bp.route('/reports/<report_id>', methods=['PATCH'])
@jwt_required_custom
@admin_required
@admin_action_logged('resolve_report')
def update_report(current_user, report_id):
    """Update report status and add resolution."""
    data = request.get_json()

    if not data or 'status' not in data:
        return jsonify({'error': 'status field required'}), 400

    status = data['status']
    resolution = data.get('resolution')

    # Validate status
    allowed_statuses = ['pending', 'under_review', 'resolved', 'dismissed']
    if status not in allowed_statuses:
        return jsonify({'error': f'Invalid status. Allowed: {", ".join(allowed_statuses)}'}), 400

    # Update report
    Report.update_status(report_id, status, current_user['_id'], resolution)

    return jsonify({
        'message': 'Report updated successfully',
        'report_id': report_id
    }), 200
