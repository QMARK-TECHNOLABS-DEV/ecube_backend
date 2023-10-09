from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from register_student.models import Student
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .utils import TokenUtil
from .models import Token
from register_student.models import Student
import boto3
import random
import jwt

class SendOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        # Ensure the phone_number is valid (you might want to add more validation)
        if not phone_number:
            return JsonResponse({'message': 'Invalid phone_number'}, status=400)
        
        db_phone_number = Student.objects.filter(phone_no=phone_number).first()
        
        if db_phone_number:
            # Generate a random OTP (6 digits)
            try:
                #otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                
                otp = '123456'
                # Store OTP in session
                expiry_time = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')

                request.session['otp'] = {
                    'phone_number': phone_number,
                    'code': otp,
                    'expiry': expiry_time
                }

                # Initialize the Amazon SNS client
                #client = boto3.client("sns")
                
                phone_number = '+91' + phone_number
                # Send the OTP via SMS
                # response = client.publish(
                #     PhoneNumber=phone_number,
                #     Message=f'Your OTP is: {otp}',
                # )

                # Check the response
                #if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                if otp:
                    print(f'OTP sent successfully to {phone_number}')
                    return JsonResponse({'message': 'OTP sent successfully'})
                else:
                    print('Failed to send OTP')
                    return JsonResponse({'message': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            except Exception as e:
                print(e)
                return JsonResponse({'message': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JsonResponse({'message': 'Invalid phone_number'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class VerifyOTP(APIView):
    def post(self, request):
        # Get the OTP entered by the user from the request data
        entered_otp = request.data.get('otp')
        
        # Get the OTP and its expiry timestamp from the session
        session_otp_data = request.session.get('otp')

        # Check if session_otp_data exists and if the OTP has not expired
        if session_otp_data:
            expiry_timestamp = session_otp_data.get('expiry')
            current_time = (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S')
            
            if current_time < expiry_timestamp:
                stored_otp = session_otp_data.get('code')
                
                if entered_otp == stored_otp:
                    
                    phone_number = session_otp_data.get('phone_number')
                    
                    user = Student.objects.filter(phone_no=phone_number).first()
    
                
                    access_token, refresh_token = TokenUtil.generate_tokens(user)
                    
                    request.session.pop('otp', None)

        # Validate tokens
                    if TokenUtil.validate_tokens(access_token, refresh_token):
                        return JsonResponse({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({'error': 'Invalid tokens.'}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    # Invalid OTP
                    return JsonResponse({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # OTP has expired
                request.session.pop('otp', None)
                return JsonResponse({'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Session data for OTP not found
            return JsonResponse({'message': 'Session data for OTP not found'}, status=status.HTTP_400_BAD_REQUEST)
        
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

        except (jwt.ExpiredSignatureError, jwt.DecodeError, ValueError, Student.DoesNotExist):
            return Response({"error": "Invalid or expired access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Access token is valid; you can proceed with request processing
        return Response({"message": "Access token is valid."}, status=status.HTTP_200_OK)
    
class RequestAccessToken(APIView):
    def post(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
        
        _, refresh_token = authorization_header.split()
        
        token_key = Token.objects.filter(refresh_token=refresh_token).first()
        
        if not token_key:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Validate the refresh token
        refresh_token_payload = TokenUtil.decode_token(refresh_token)
        
        if not refresh_token_payload:
            return JsonResponse({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = refresh_token_payload.get('id')
        
        if not user_id:
            return JsonResponse({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a new access token
        user = Student.objects.get(id=user_id)
        
        access_token = TokenUtil.generate_access_token(user)
        
        if TokenUtil.validate_access_token(access_token):
            return JsonResponse({'error': 'Failed to generate access token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            
            user_token = Token.objects.get(refresh_token=refresh_token)
            user_token.access_token = access_token
            user_token.save()
            
            return JsonResponse({'access_token': access_token}, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
       
        access_token = request.data.get('access_token')

        if not access_token:
            return JsonResponse({'error': 'Access token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if TokenUtil.is_token_valid(access_token):
            TokenUtil.blacklist_token(access_token)
            
            return JsonResponse({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Invalid access token or expired access token'}, status=status.HTTP_401_UNAUTHORIZED)

