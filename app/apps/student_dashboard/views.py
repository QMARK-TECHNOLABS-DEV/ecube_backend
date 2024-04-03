from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..register_student.models import Student
from ..client_auth.utils import TokenUtil
from ..client_auth.models import Token

class StudentGetDashboard(APIView):
    def get(self, request):
        
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
            return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)
        # Generate a new access token
        user = Student.objects.get(id=user_id) 
        
        student_info = {
            "name": user.name,
            "profile_image": "",
            "admission_no": user.admission_no,
            "class_name": user.class_name,
            "division": user.division,
            "batch_year": user.batch_year,
            "subjects": user.subjects,
            "school_name": user.school_name,
            
        }
        
        return Response({"student_info": student_info}, status=status.HTTP_200_OK)