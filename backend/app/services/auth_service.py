"""Authentication service for JWT and OAuth handling."""
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from authlib.integrations.requests_client import OAuth2Session
from ..models.user import User
import re


class AuthService:
    """Handle authentication operations."""

    @staticmethod
    def register_user(email, password, pseudonym, roles):
        """Register a new user with email/password."""
        # Validate email format
        if not AuthService.validate_email(email):
            return None, 'Invalid email format'

        # Check if email already exists
        if User.find_by_email(email):
            return None, 'Email already exists'

        # Check if pseudonym already exists
        if User.find_by_pseudonym(pseudonym):
            return None, 'Pseudonym already exists'

        # Validate password
        error = AuthService.validate_password(password)
        if error:
            return None, error

        # Validate pseudonym
        error = AuthService.validate_pseudonym(pseudonym)
        if error:
            return None, error

        # Validate roles
        if not roles or not isinstance(roles, list):
            return None, 'At least one role required'
        if not all(role in ['sharer', 'listener'] for role in roles):
            return None, 'Invalid role specified'

        # Create user
        user = User.create({
            'email': email,
            'password': password,
            'pseudonym': pseudonym,
            'roles': roles
        })

        return user, None

    @staticmethod
    def login_user(email, password):
        """Login user with email/password."""
        user = User.find_by_email(email)

        if not user:
            return None, 'Invalid credentials'

        if not user.get('is_active', True):
            return None, 'Account is inactive'

        # Verify password (only for non-OAuth users)
        if 'password_hash' not in user:
            return None, 'Please login with OAuth provider'

        if not User.verify_password(password, user['password_hash']):
            return None, 'Invalid credentials'

        return user, None

    @staticmethod
    def verify_google_token(credential):
        """Verify Google OAuth token and return user info."""
        try:
            client = OAuth2Session(
                current_app.config['GOOGLE_CLIENT_ID'],
                current_app.config['GOOGLE_CLIENT_SECRET']
            )

            # Exchange credential for user info
            token_url = 'https://oauth2.googleapis.com/token'
            userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'

            # Get user info from Google
            response = client.get(userinfo_url, token=credential)
            if response.status_code != 200:
                return None, 'Failed to verify Google token'

            user_info = response.json()

            return {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'google_id': user_info.get('sub')
            }, None

        except Exception as e:
            current_app.logger.error(f'Google OAuth error: {str(e)}')
            return None, 'Failed to verify Google token'

    @staticmethod
    def handle_google_oauth(user_info):
        """Handle Google OAuth login/registration."""
        email = user_info['email']
        google_id = user_info['google_id']

        # Check if user exists with this OAuth
        user = User.find_by_oauth('google', google_id)

        if user:
            # Existing OAuth user - login
            if not user.get('is_active', True):
                return None, 'Account is inactive'
            return user, None

        # Check if email already exists (different auth method)
        user = User.find_by_email(email)
        if user:
            return None, 'Email already in use with different login method'

        # New user - register
        # Generate unique pseudonym from name
        base_pseudonym = user_info['name'].replace(' ', '').replace('.', '')
        pseudonym = AuthService.generate_unique_pseudonym(base_pseudonym)

        user = User.create({
            'email': email,
            'oauth_provider': 'google',
            'oauth_id': google_id,
            'pseudonym': pseudonym,
            'real_name': user_info['name'],
            'profile_picture_url': user_info.get('picture'),
            'roles': ['sharer']  # Default role for new OAuth users
        })

        return user, None

    @staticmethod
    def generate_unique_pseudonym(base):
        """Generate a unique pseudonym."""
        pseudonym = base
        counter = 1

        while User.find_by_pseudonym(pseudonym):
            pseudonym = f"{base}{counter}"
            counter += 1

        return pseudonym

    @staticmethod
    def create_tokens(user_id):
        """Create access and refresh tokens for user."""
        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))
        return access_token, refresh_token

    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password(password):
        """Validate password strength."""
        if len(password) < 8:
            return 'Password must be at least 8 characters'
        if not re.search(r'[A-Z]', password):
            return 'Password must contain at least one uppercase letter'
        if not re.search(r'[a-z]', password):
            return 'Password must contain at least one lowercase letter'
        if not re.search(r'\d', password):
            return 'Password must contain at least one number'
        return None

    @staticmethod
    def validate_pseudonym(pseudonym):
        """Validate pseudonym format."""
        if len(pseudonym) < 3 or len(pseudonym) > 20:
            return 'Pseudonym must be 3-20 characters'
        if not re.match(r'^[a-zA-Z0-9_]+$', pseudonym):
            return 'Pseudonym can only contain letters, numbers, and underscores'
        return None
