"""Authentication routes."""
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..services.auth_service import AuthService
from ..models.user import User
from ..extensions import redis_client

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register new user with email/password."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email')
    password = data.get('password')
    pseudonym = data.get('pseudonym')
    roles = data.get('roles')

    if not all([email, password, pseudonym, roles]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Register user
    user, error = AuthService.register_user(email, password, pseudonym, roles)

    if error:
        status_code = 409 if 'already exists' in error else 400
        return jsonify({'error': error}), status_code

    # Return user info (not sensitive data)
    return jsonify({
        'message': 'User registered successfully',
        'user': {
            'id': str(user['_id']),
            'email': user['email'],
            'pseudonym': user['pseudonym'],
            'roles': user['roles']
        }
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """Login with email/password, receive JWT tokens."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    # Authenticate user
    user, error = AuthService.login_user(email, password)

    if error:
        status_code = 403 if 'inactive' in error else 401
        return jsonify({'error': error}), status_code

    # Create tokens
    access_token, refresh_token = AuthService.create_tokens(user['_id'])

    # Create response with tokens in httpOnly cookies
    response = make_response(jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': User.to_dict(user)
    }))

    # Set cookies
    response.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite='Lax',
        max_age=900  # 15 minutes
    )
    response.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=604800  # 7 days
    )

    return response, 200


@bp.route('/google', methods=['POST'])
def google_oauth():
    """OAuth login/register with Google."""
    data = request.get_json()

    if not data or 'credential' not in data:
        return jsonify({'error': 'Google credential required'}), 400

    credential = data['credential']

    # Verify Google token
    user_info, error = AuthService.verify_google_token(credential)

    if error:
        return jsonify({'error': error}), 400

    # Handle OAuth (login or register)
    user, error = AuthService.handle_google_oauth(user_info)

    if error:
        return jsonify({'error': error}), 409

    # Create tokens
    access_token, refresh_token = AuthService.create_tokens(user['_id'])

    # Create response
    response = make_response(jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': User.to_dict(user)
    }))

    # Set cookies
    response.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=900
    )
    response.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=604800
    )

    return response, 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh expired access token using refresh token."""
    user_id = get_jwt_identity()

    # Verify user still exists and is active
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not user.get('is_active', True):
        return jsonify({'error': 'Account is inactive'}), 403

    # Create new access token
    from flask_jwt_extended import create_access_token
    access_token = create_access_token(identity=user_id)

    # Return with new cookie
    response = make_response(jsonify({
        'access_token': access_token
    }))

    response.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=900
    )

    return response, 200


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user, invalidate tokens."""
    # Get JTI (JWT ID) to blacklist
    jti = get_jwt()['jti']

    # Add refresh token to Redis blacklist (expires in 7 days)
    redis_client.setex(f'blacklist:{jti}', 604800, 'true')

    # Clear cookies
    response = make_response(jsonify({
        'message': 'Logged out successfully'
    }))

    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)

    return response, 200
