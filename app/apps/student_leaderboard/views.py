from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from ..register_student.models import Student
from ..client_auth.utils import TokenUtil

from ..register_student.models import class_details
from ecube_backend.pagination import CustomPageNumberPagination
from ecube_backend.utils import role_checker


class AdminGetExams(APIView):
    @role_checker(allowed_roles=['admin'])
    def get(self,request):
        try:
            batch_year = request.GET.get('batch_year')
            class_name = request.GET.get('class_name')
            division = request.GET.get('division')

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
        except Exception as e:
            print(e)
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AdminGetLeaderBoard(APIView,CustomPageNumberPagination):
    @role_checker(allowed_roles=['admin'])
    def get(self, request):
        
        batch_year_cap = request.GET.get('batch_year')
        class_name_cap = request.GET.get('class_name')
        division_cap = request.GET.get('division')
        subject = request.GET.get('subject')
        exam_name = request.GET.get('exam_name')
        
        if not exam_name:
            if batch_year_cap is None or class_name_cap is None or division_cap is None:
                    class_group_instance = class_details.objects.filter(
                            exam_result__isnull=False 
                        ).order_by('-exam_result').first()
                    
                    if class_group_instance is None: 
                        return Response({"message": "Nothing to show here"}, status=status.HTTP_200_OK)
                    else:
                        batch_year_cap = class_group_instance.batch_year
                        class_name_cap = class_group_instance.class_name
                        division_cap = class_group_instance.division
                        subject = class_group_instance.exam_subject
            else:
                class_group = class_details.objects.filter(batch_year=batch_year_cap,class_name=class_name_cap,division=division_cap).first()
                
                if not class_group:
                    return Response({"message": "Class Group does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if not class_group.exam_result:
                        return Response({"message": "No exam results published for this class group"}, status=status.HTTP_400_BAD_REQUEST)
                    
            batch_year = str(batch_year_cap)
            class_name = str(class_name_cap).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division_cap).replace(" ", "")
            division = str(division).lower()
            
            if subject is None:
                subject = "PHYSICS" 
            else:
                subject = str(subject).upper()      
                    

            app_name = 'register_student_'
            table_name = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_leaderboard"

            cursor = connection.cursor()
            cursor.execute(f"SELECT admission_no, {subject} FROM public.{table_name} WHERE admission_no IS NOT NULL AND {subject} IS NOT NULL ORDER BY {subject} DESC NULLS LAST;")
            query_results = cursor.fetchall()
            cursor.close()
            
        else:
            batch_year = str(batch_year_cap)
            class_name = str(class_name_cap).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division_cap).replace(" ", "")
            division = str(division).lower()
            
            if subject is None:
                subject = "PHYSICS" 
            else:
                subject = str(subject).upper()
                
            app_name = 'register_student'
            table_name = app_name + '_' + app_name + '_'+ batch_year + "_" + class_name + "_" + division + "_examresults"
            
            cursor = connection.cursor()
            cursor.execute(f"SELECT admission_no, {subject} FROM public.{table_name} WHERE exam_name = %s AND {subject} IS NOT NULL ORDER BY {subject} DESC NULLS LAST;", [exam_name])
            
            query_results = cursor.fetchall()
            
            print(query_results)
            cursor.close()
        
        leaderboard = []
        
        
        for row in query_results:     
            
            try:
                other_student = Student.objects.get(admission_no=row[0])
                
                leaderboard.append({
                    "admission_no": other_student.admission_no,
                    "mark": row[1],
                    "name": other_student.name,
                    "profile_image": "",
                })
            except Exception as e:
                print(e)
                pass
            
        try:
            leaderboard = self.paginate_queryset(leaderboard, request)
        except Exception as e:
            return Response({'status': 'failure', 'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
        response = {
            'class_name': class_name_cap,
            'batch_year': batch_year_cap,
            'division': division_cap, 
            'subject': subject,
            'leaderboard': leaderboard,
            "total_pages": self.page.paginator.num_pages,
            "has_next": self.page.has_next(),
            "has_previous": self.page.has_previous(),
            "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
            "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,
        }
        return Response(response, status=status.HTTP_200_OK)
    
class GetLeaderBoard(APIView):
    def get(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)

      
        _, token = authorization_header.split()
        

        payload = TokenUtil.decode_token(token)

        # Optionally, you can extract user information or other claims from the payload
        if not payload:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = payload.get('id')
        
        if not user_id:
            return Response({'error': 'The access token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)
        # Generate a new access token
        user = Student.objects.get(id=user_id) 
        
        print(user.id)
        
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

        app_name = 'register_student_'
        table_name = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_leaderboard"

        cursor = connection.cursor()
        cursor.execute(f"SELECT admission_no, {subject} FROM public.{table_name} WHERE admission_no IS NOT NULL AND {subject} IS NOT NULL ORDER BY {subject} DESC NULLS LAST LIMIT 10;")
        query_results = cursor.fetchall()
        cursor.close()
        
        leaderboard = []
        
        user_rank = {}
   
        try:
            for row in query_results:
                
                if row[0] == user.admission_no:

                    user_rank = {
                        "name": user.name,
                        "profile_image": "",
                        "rank": query_results.index(row) + 1,
                        "mark": row[1],
                        }
                
                try:  
                    
                    other_student = Student.objects.get(admission_no=row[0])
                    
                    
                        
                    leaderboard.append({
                        "admission_no": row[0],
                        "mark": row[1],
                        "name": other_student.name,
                        "profile_image": "",
                    })
                except Exception as e:
                    print(e)
                    pass
                    

            return Response({'leaderboard': leaderboard,'user_rank': user_rank}, status=status.HTTP_200_OK)
    
        except Exception as e:
            print(e)
            return Response({"error": f"the error is {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

    
    
class GetLeaderBoardByExams(APIView):
    def get(self,request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)

      
        _, token = authorization_header.split()

        payload = TokenUtil.decode_token(token)

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
        
        payload = TokenUtil.decode_token(token)

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
    
    
class RecalculateLeaderBoardByClass(APIView):
    @role_checker(allowed_roles=['admin'])
    def post(self, request):
        try:
            batch_year_cap = request.GET.get('batch_year')
            class_name_cap = request.GET.get('class_name')
            division_cap = request.GET.get('division')
            
            if batch_year_cap is None or class_name_cap is None or division_cap is None:
                return Response({'status': 'failure', 'message': 'batch_year, class_name, and division are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            batch_year = str(batch_year_cap)
            class_name = str(class_name_cap).replace(" ", "").lower()
            division = str(division_cap).replace(" ", "").lower()
            
            app_name = 'register_student_'
            
            cursor = connection.cursor()
            
            try:
                cursor.execute(f"DELETE FROM public.{app_name}{app_name}{batch_year}_{class_name}_{division}_leaderboard;")
                
                # cursor.execute(f"SELECT DISTINCT exam_name FROM public.{app_name}{app_name}{batch_year}_{class_name}_{division}_examresults;")
                    
                # query_results = cursor.fetchall()

                # for exam in query_results:
                    
                cursor.execute(f'''
                    INSERT INTO public.{app_name}{app_name}{batch_year}_{class_name}_{division}_leaderboard (admission_no, physics, chemistry, maths)
                    SELECT 
                        admission_no,
                        CASE WHEN SUM(physics) IS NULL THEN NULL ELSE COALESCE(SUM(physics), 0) END AS total_physics,
                        CASE WHEN SUM(chemistry) IS NULL THEN NULL ELSE COALESCE(SUM(chemistry), 0) END AS total_chemistry,
                        CASE WHEN SUM(maths) IS NULL THEN NULL ELSE COALESCE(SUM(maths), 0) END AS total_maths
                    FROM (
                        SELECT 
                            admission_no, 
                            SUM(physics) AS physics,
                            SUM(chemistry) AS chemistry,
                            SUM(maths) AS maths
                        FROM 
                            (SELECT 
                                admission_no, 
                                exam_name, 
                                CASE WHEN physics IS NULL THEN NULL ELSE COALESCE(physics, 0) END AS physics, 
                                CASE WHEN chemistry IS NULL THEN NULL ELSE COALESCE(chemistry, 0) END AS chemistry, 
                                CASE WHEN maths IS NULL THEN NULL ELSE COALESCE(maths, 0) END AS maths
                            FROM 
                                public.{app_name}{app_name}{batch_year}_{class_name}_{division}_examresults) AS subquery
                        GROUP BY 
                            admission_no, exam_name
                    ) AS total_scores
                    GROUP BY 
                        admission_no;
                ''')
                
                cursor.close()
                
                return Response({'status': 'success', 'message': 'Leaderboard recalculated successfully'}, status=status.HTTP_200_OK)
                                        
            except Exception as e:
                return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            print(e)
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)