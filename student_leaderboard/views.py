from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from register_student.models import Student
from client_auth.utils import TokenUtil
from client_auth.models import Token

class GetLeaderBoard(APIView):
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
        
        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division
        subject = request.GET.get('subject')

        if batch_year is None or class_name is None or division is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name, and division are required'}, status=status.HTTP_400_BAD_REQUEST)

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "")
        class_name = str(class_name).lower()
        division = str(division).replace(" ", "")
        division = str(division).lower()

        app_name = 'register_student'
        table_name = app_name + '_' + app_name+ '_'+ batch_year + "_" + class_name + "_" + division + "_leaderboard"

        cursor = connection.cursor()
        cursor.execute(f"SELECT admission_no, {subject} FROM public.{table_name} ORDER BY {subject} DESC NULLS LAST;")
        query_results = cursor.fetchall()
        cursor.close()
        
        # cursor = connection.cursor()
        # cursor.execute(f"SELECT DENSE_RANK() OVER (ORDER BY {subject} DESC NULLS LAST) FROM public.{table_name} WHERE admission_no = %s;", [user.admission_no])
        
        # rank_result = cursor.fetchone()
        # cursor.close()
        
        leaderboard = []

        for row in query_results:
            
            if row[0] == user.admission_no:
                user_rank = query_results.index(row) + 1
            leaderboard.append({
                "admission_no": row[0],
                "total": row[1],
            })

        return Response({'leaderboard': leaderboard,'user_rank': user_rank}, status=status.HTTP_200_OK)
    
    
class GetLeaderBoardByExams(APIView):
    def get(self,request):
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
        
        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division
        subject = request.GET.get('subject')
        exam_name = request.GET.get('exam_name')

        if batch_year is None or class_name is None or division is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name, and division are required'}, status=status.HTTP_400_BAD_REQUEST)

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "")
        class_name = str(class_name).lower()
        division = str(division).replace(" ", "")
        division = str(division).lower()

        app_name = 'register_student'
        table_name = app_name + '_' + app_name+ '_'+ batch_year + "_" + class_name + "_" + division + "_examresults"
        
        
        cursor = connection.cursor()
        cursor.execute(f"SELECT admission_no, {subject} FROM public.{table_name} WHERE exam_name = %s ORDER BY {subject} DESC NULLS LAST;", [exam_name])
        
        query_results = cursor.fetchall()
        
        cursor.close()
        
        leaderboard = []
        
        for row in query_results:
            
            if row[0] == user.admission_no:
                user_rank = query_results.index(row) + 1
            leaderboard.append({
                "admission_no": row[0],
                "total": row[1],
            })
            
        return Response({'leaderboard': leaderboard,'user_rank': user_rank}, status=status.HTTP_200_OK)
    
class GetExams(APIView):
    def get(self,request):
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
        
        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division
        subject = request.GET.get('subject')
        exam_name = request.GET.get('exam_name')

        if batch_year is None or class_name is None or division is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name, and division are required'}, status=status.HTTP_400_BAD_REQUEST)

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "")
        class_name = str(class_name).lower()
        division = str(division).replace(" ", "")
        division = str(division).lower()

        app_name = 'register_student'
        table_name = app_name + '_' + app_name+ '_'+ batch_year + "_" + class_name + "_" + division + "_examresults"
        
        cursor = connection.cursor()
        cursor.execute(f"SELECT DISTINCT exam_name FROM public.{table_name} ORDER BY exam_name ASC;")
        
        query_results = cursor.fetchall()
        
        cursor.close()
        
        exams = []
        
        for row in query_results:
            exams.append(row[0])
            
        return Response({'exams': exams}, status=status.HTTP_200_OK) 