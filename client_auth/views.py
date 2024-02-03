from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from register_student.models import Student
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .utils import TokenUtil
from .models import Token, OTP
from register_student.models import Student
from .fast_sms import sendSMS
from django.utils import timezone 
import random
import jwt, json


class SendOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        # Ensure the phone_number is valid (you might want to add more validation)
        if not phone_number:
            return Response({'message': 'Invalid phone_number'}, status=400)
        
        phone_number = int(phone_number)
        print(phone_number, type(phone_number))
        db_phone_number = Student.objects.filter(phone_no=phone_number).first()
        
        if db_phone_number is not None:
            if db_phone_number.restricted == False:
                
                no_of_users_signed_in = Token.objects.filter(user_id=db_phone_number.id).count()
                
                print(no_of_users_signed_in)
                
                if no_of_users_signed_in < 2:
                
                    if str(db_phone_number.phone_no) != '1234567890':
                        # Generate a random OTP (6 digits)
                        try:
                            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                            
                            otp_instance = OTP.objects.filter(phone_number=phone_number).all()
                            
                            if otp_instance:
                                for otp in otp_instance:
                                    otp.delete()
                                
                            OTP.objects.create(phone_number=phone_number, code=otp)
                            
                            response = sendSMS(otp, phone_number)
                            print("sended")
                            response_data = json.loads(response)
                            
                            
                            # Access the 'return' key
                            return_value = response_data.get('return')
                            # Check the response
                            #if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                            if return_value == True:
                                print(f'OTP sent successfully to {phone_number}')
                                return Response({'message': 'OTP sent successfully'})
                            else:
                                print('Failed to send OTP')
                                return Response({'message': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                            
                        except Exception as e:
                            print(e)
                            return Response({'message': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:           
                        
                        otp = '123456'
                        
                        otp_instance = OTP.objects.filter(phone_number=phone_number).all()
                            
                        if otp_instance:
                            for otps in otp_instance:
                                otps.delete()
                        
                        print(otp)
                        OTP.objects.create(phone_number=phone_number, code=otp)
                        
                        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Maximum number of users signed in'}, status=status.HTTP_400_BAD_REQUEST)       
            else:
                return Response({'message': 'User is restricted'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class VerifyOTP(APIView):
    def post(self, request):
        # Get the OTP entered by the user from the request data
        entered_otp = request.data.get('otp')
        phone_number = request.data.get('phone_number')
        
        try:
            otp = OTP.objects.filter(phone_number=phone_number).first()
            
            # Ensure both times are in the same timezone-aware format
            current_time = timezone.now()  # Get the current time in the same timezone
            expiry_time = otp.expiry_time + timedelta(minutes=5)  # Add 5 minutes to expiry_time
            
            if expiry_time > current_time:
                if entered_otp == str(otp.code):
                
                    user = Student.objects.filter(phone_no=phone_number).first()
                    
                    if user is None:
                        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                    
                    access_token, refresh_token = TokenUtil.generate_tokens(user)
                    
                    otp.delete()  

                    return Response({'access_token': access_token, 'refresh_token': refresh_token, 'name': user.name, 'class_name': user.class_name, 'batch_year': user.batch_year, 'division': user.division}, status=status.HTTP_200_OK)

                    
                else:
                    return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                otp.delete()
                return Response({'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
            
        except OTP.DoesNotExist:
            # Session data for OTP not found
            return Response({'message': 'Session data for OTP not found'}, status=status.HTTP_400_BAD_REQUEST)
        
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
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

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
            return Response({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = refresh_token_payload.get('id')
        
        if not user_id:
            return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a new access token
        user = Student.objects.get(id=user_id)
        
        access_token = TokenUtil.generate_access_token(user)
        
        if TokenUtil.validate_access_token(access_token):
            return Response({'error': 'Failed to generate access token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            
            user_token = Token.objects.get(refresh_token=refresh_token)
            user_token.access_token = access_token
            user_token.save()
            
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
       
        access_token = request.data.get('access_token')

        if not access_token:
            return Response({'error': 'Access token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if TokenUtil.is_token_valid(access_token):
            TokenUtil.blacklist_token(access_token)
            
            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid access token or expired access token'}, status=status.HTTP_401_UNAUTHORIZED)

