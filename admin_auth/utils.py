# customjwtapp/utils.py
import jwt
from datetime import datetime, timedelta
from .models import Token, Admin
from django.conf import settings

class TokenUtil:
    @staticmethod
    def generate_tokens(user):
        # Check if tokens already exist for the user
        existing_tokens = Token.objects.filter(user=user).first()
        if existing_tokens:
            return existing_tokens.access_token, existing_tokens.refresh_token

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
        payload = {
            'id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION),
            'iat': datetime.utcnow(),
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
            user = Admin.objects.get(pk=user_id)  # Replace with your user retrieval logic
            new_access_token = TokenUtil.generate_access_token(user)

            return new_access_token  # Return the new access token

        # Validate the refresh token
        refresh_token_payload = TokenUtil.decode_token(refresh_token)
        if not refresh_token_payload:
            return False  # Refresh token is invalid or expired

        # You can also perform additional checks here if needed
        # For example, check if the tokens belong to the same user

        return True  # Both tokens are valid
    
    
    @staticmethod
    def generate_refresh_token(user):
        payload = {
            'id': user.id,
            'exp': datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRATION),
            'iat': datetime.utcnow(),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def is_token_valid(token):
        try:
            token_value = Token.objects.filter(access_token=token)
            if token_value:
                
                # jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                return True
            else:
                return False
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return False
        
    @staticmethod
    def is_token_expired(token):
        try:
            token_value = Token.objects.filter(access_token=token)
            if token_value:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                exp = payload.get('exp')
                if datetime.utcnow() > datetime.fromtimestamp(exp):
                    return True
                else:
                    return False
            else:
                return False
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return False
        
    @staticmethod
    def decode_token(token):
        try:
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
