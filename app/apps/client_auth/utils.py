# customjwtapp/utils.py
import jwt
from datetime import datetime, timedelta, timezone
from .models import Token
from ..register_student.models import Student
from django.conf import settings

class TokenUtil:
    @staticmethod
    def generate_tokens(user):
        # Check if tokens already exist for the user
        # existing_tokens = Token.objects.filter(user=user).first()
        # if existing_tokens:
        #     existing_tokens.delete()

        # Generate new tokens
        access_token = TokenUtil.generate_access_token(user)
        refresh_token = TokenUtil.generate_refresh_token(user)
        
        # Store the new tokens in the database
        Token.objects.create(user=user, access_token=access_token, refresh_token=refresh_token)
        
        return access_token, refresh_token
    
    @staticmethod
    def validate_access_token(access_token):
        # Check if tokens already exist for the user
        existing_tokens = Token.objects.filter(access_token=access_token).first()
        if existing_tokens:
            return existing_tokens.access_token
        else:
            return False
        
    @staticmethod
    def generate_access_token(user):
        expiration_time = datetime.now(timezone.utc) + timedelta(days=settings.ACCESS_TOKEN_EXPIRATION)
        payload = {
            'id': user.id,
            'exp': expiration_time.timestamp(),  # Convert expiration time to Unix timestamp
            'iat': datetime.now(timezone.utc).timestamp(),  # Convert current time to Unix timestamp
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def validate_tokens(access_token, refresh_token):
        # Validate the access token
        access_token_payload = TokenUtil.decode_token(access_token)
        if not access_token_payload:
            # Access token is invalid or expired, try to generate a new access token using the refresh token
            refresh_token_payload = TokenUtil.decode_token(refresh_token)
            if not refresh_token_payload:
                return False  # Both access and refresh tokens are invalid or expired

            # Check if the refresh token is associated with a user (add your logic here)
            user_id = refresh_token_payload.get('id')
            if not user_id:
                return False  # The refresh token is not associated with a user

            # Generate a new access token
            user = Student.objects.get(pk=user_id)  # Replace with your user retrieval logic
            new_access_token = TokenUtil.generate_access_token(user)

            return new_access_token  # Return the new access token

        # Validate the refresh token
        refresh_token_payload = TokenUtil.decode_token(refresh_token)
        if not refresh_token_payload:
            return False  # Refresh token is invalid or expired

        return True  # Both tokens are valid
    
    
    @staticmethod
    def generate_refresh_token(user):
        expiration_time = datetime.now(timezone.utc) + timedelta(weeks=settings.REFRESH_TOKEN_EXPIRATION)
        payload = {
            'id': user.id,
            'exp': expiration_time.timestamp(),  # Convert expiration time to Unix timestamp
            'iat': datetime.now(timezone.utc).timestamp(),  # Convert current time to Unix timestamp
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def is_token_valid(token):
        try:
            token_value = Token.objects.filter(access_token=token)
            if token_value:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                exp = payload.get('exp')
                if exp and datetime.now() < datetime.fromtimestamp(exp):
                    return True  # Token is valid
            return False  # Token not found in the database or expired
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return False  # Token decoding error or expired signature
        
    @staticmethod
    def is_token_expired(token):
        try:
            token_value = Token.objects.filter(access_token=token)
            if not token_value:
                return True  # Token not found, consider it expired
            
            print("token found")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            exp = payload.get('exp')
            if datetime.now() > datetime.fromtimestamp(exp):
                return True  # Token has expired
            else:
                return False  # Token is still valid
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return True  # Token decoding error or expired signature, consider it expired

    @staticmethod
    def is_refresh_token_expired(token):
        try:
            token_value = Token.objects.filter(refresh_token=token)
            if not token_value:
                return True  # Token not found, consider it expired
            
            print("token found")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            exp = payload.get('exp')
            print(exp)
            if datetime.now() > datetime.fromtimestamp(exp):
                return True  # Token has expired
            else:
                return False  # Token is still valid
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return True  # Token decoding error or expired signature, consider it expired
            
    @staticmethod
    def decode_token(token):
        try:
            print("decode", settings.SECRET_KEY)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError as e:
            # Token has expired, but we can still attempt to decode it for user information
            print(f"Token expired: {e}")
            return None
        except jwt.DecodeError as e:
            # Token decoding error
            print(f"Token decoding error: {e}")
            return None
        
        
    @staticmethod
    def blacklist_token(token):
        Token.objects.filter(access_token=token).delete()
