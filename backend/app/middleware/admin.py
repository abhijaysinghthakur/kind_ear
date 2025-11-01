"""Admin middleware."""
from functools import wraps
from flask import jsonify
from ..models.user import User
from bson import ObjectId
from datetime import datetime
from ..extensions import db


def log_admin_action(admin_id, action, target_id, details=None):
    """Log admin action to admin_logs collection."""
    log_entry = {
        'admin_id': ObjectId(admin_id) if isinstance(admin_id, str) else admin_id,
        'action': action,
        'target_id': ObjectId(target_id) if isinstance(target_id, str) else target_id,
        'details': details or {},
        'timestamp': datetime.utcnow()
    }
    db.admin_logs.insert_one(log_entry)


def admin_action_logged(action_name):
    """Decorator to automatically log admin actions."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Execute the function
            result = fn(*args, **kwargs)

            # Log the action if successful
            current_user = kwargs.get('current_user')
            if current_user and isinstance(result, tuple) and result[1] == 200:
                # Extract target_id from kwargs or args
                target_id = kwargs.get('user_id') or kwargs.get('report_id')
                log_admin_action(
                    str(current_user['_id']),
                    action_name,
                    target_id,
                    {'function': fn.__name__}
                )

            return result
        return wrapper
    return decorator
