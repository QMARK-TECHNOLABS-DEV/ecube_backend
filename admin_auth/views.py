from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import render
from .utils import TokenUtil
import jwt
from .models import Admin, Token, PasswordResetToken
from .serializers import UserSerializer
from django.core.mail import send_mail
from django.contrib import messages

class GetAllUsers(APIView):
    def get(self,request):
        users = Admin.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({'all_users': serializer.data})

#get user by id
class GetUserById(APIView):
    def get(self,request):
        
        user_id = request.GET.get('id')
        
        user = Admin.objects.get(id=user_id)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

# create user
class SignUpUser(APIView):
    def post(self,request):
        try:
            data = request.data.copy()
            
            email_db = Admin.objects.filter(email=data['email'], login_type='email').first()
            
            if email_db:
                return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'password' in data:
                data['password'] = make_password(data['password'])

            domain = data['email'].split('@')[1]

            if data['email'][0:3] != 'chn' and domain != 'ceconline.edu':
                data['role'] = 'guest'
            else:
                data['register_no'] = str(data['email'].split('@')[0]).upper()

            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                user = serializer.save()

                access_token, refresh_token = TokenUtil.generate_tokens(user)
                

    # Validate tokens
                if TokenUtil.validate_tokens(access_token, refresh_token):
                    return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid tokens.'}, status=status.HTTP_401_UNAUTHORIZED)
                
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except KeyError as e:
            return Response(f"Missing key: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
            return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# update user
class UpdateUser(APIView):
    def update(self,request):
        
        try: 
            user_id = request.GET.get('id')
        
            user = Admin.objects.get(id=user_id)
            serializer = UserSerializer(instance=user, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                
            return Response(serializer.data)
        
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)


# delete user
class DeleteUser(APIView):
    def delete(self,request):
        
        try:
            
            user_id = request.GET.get('id')
        
            user = Admin.objects.get(id=user_id)
            
            user.delete()
        
            return Response("User deleted successfully!", status=status.HTTP_204_NO_CONTENT)
        
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
        
class ValidateTokenView(APIView):
    def post(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            _, token = authorization_header.split()
            
            token_key = Token.objects.filter(access_token=token).first()
            
            if not token_key:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)
            

            payload = TokenUtil.decode_token(token_key.access_token)

            # Optionally, you can extract user information or other claims from the payload
            if not payload:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Implement additional authorization logic here if needed

        except (jwt.ExpiredSignatureError, jwt.DecodeError, ValueError, Admin.DoesNotExist):
            return Response({"error": "Invalid or expired access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Access token is valid; you can proceed with request processing
        return Response({"message": "Access token is valid."}, status=status.HTTP_200_OK)
    

class LoginUser(APIView):
    def post(self,request):
        try:
            user = Admin.objects.get(email=request.data['email'], login_type='email')
            
            if user is not None:
                
                if user.logged_in:
                    user_token = Token.objects.get(user_id=user.id)
                    
                    user_token.delete()
                    
                if check_password(request.data['password'], user.password):
                    # Generate refresh and access tokens
                    access_token, refresh_token = TokenUtil.generate_tokens(user)
                    
                    # Validate tokens
                    if TokenUtil.validate_tokens(access_token, refresh_token):
                        user.logged_in = True
                        user.save()

                        return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Invalid tokens.'}, status=status.HTTP_401_UNAUTHORIZED) 

                else:
                    return Response("Password is incorrect!", status=status.HTTP_400_BAD_REQUEST)
        
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)

class RequestAccessToken(APIView):
    def post(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
        
        _, refresh_token = authorization_header.split()
        
        token_key = Token.objects.filter(refresh_token=refresh_token).first()
        
        if not token_key:
            return Response({"error": "refresh token not found please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

        # Validate the refresh token
        refresh_token_payload = TokenUtil.decode_token(refresh_token)
        
        if not refresh_token_payload:
            return Response({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = refresh_token_payload.get('id')
        
        if not user_id:
            return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a new access token
        user = Admin.objects.get(id=user_id)
        
        access_token = TokenUtil.generate_access_token(user)
        
        if TokenUtil.validate_access_token(access_token):
            return Response({'error': 'Failed to generate access token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            
            user_token = Token.objects.get(refresh_token=refresh_token)
            user_token.access_token = access_token
            user_token.save()
            
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
 
class ForgotPassword(APIView):
    def post(self,request):
       
        email = request.data.get('email')
        try:
            user = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            user = None

        if user is not None:
            token = default_token_generator.make_token(user)
            token = urlsafe_base64_encode(force_bytes(token))
            PasswordResetToken.objects.create(user=user, token=token)
            reset_link = f"http://{request.get_host()}/reset/{token}/"

            send_mail(
                "Password Reset",
                f"Click the following link to reset your password: {reset_link}",
                "qmarktechnolabs@gmail.com",
                [user.email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
        else:
            messages.error(request, "No user with that email address found.")

        return render(request, "password_reset_request.html")
# logout user
class LogoutUser(APIView):
    def post(self,request):
        try:
            
            authorization_header = request.META.get("HTTP_AUTHORIZATION")
                
            if not authorization_header:
                return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)


            _, token = authorization_header.split()
            
            token_key = Token.objects.filter(access_token=token).first()
            
            if not token_key:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)
            

            payload = TokenUtil.decode_token(token_key.access_token)

            # Optionally, you can extract user information or other claims from the payload
            if not payload:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the refresh token is associated with a user (add your logic here)
            user_id = payload.get('id')
            
            if not user_id:
                return Response({'error': 'The access token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user = Admin.objects.get(id=user_id) 
                
            if user.logged_in:
                # Blacklist the user's refresh token to invalidate it
                        
                user.logged_in = False
                user.save()
                
                print("User logged out and starting to blacklist token")
                if TokenUtil.is_token_valid(token):
                    TokenUtil.blacklist_token(token)
                    
                    return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid access token or expired access token'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response("User is not logged in!", status=status.HTTP_400_BAD_REQUEST)
        
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)