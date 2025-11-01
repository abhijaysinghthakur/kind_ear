"""Authentication middleware and decorators."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models.user import User


def jwt_required_custom(fn):
    """Custom JWT required decorator that loads user into request context."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.find_by_id(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            if not user.get('is_active', True):
                return jsonify({'error': 'Account is inactive'}), 403

            # Attach user to kwargs for easy access
            kwargs['current_user'] = user
            return fn(*args, **kwargs)

        except Exception as e:
            return jsonify({'error': 'Invalid or expired token'}), 401

    return wrapper


def role_required(*required_roles):
    """Decorator to check if user has required role."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401

            user_roles = current_user.get('roles', [])
            if not any(role in user_roles for role in required_roles):
                return jsonify({'error': f'Role required: {" or ".join(required_roles)}'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Decorator to check if user is admin."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401

        if not current_user.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403

        return fn(*args, **kwargs)
    return wrapper
