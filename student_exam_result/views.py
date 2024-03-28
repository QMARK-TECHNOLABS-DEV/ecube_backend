from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from register_student.models import Student, class_details
from client_auth.utils import TokenUtil
from client_auth.models import Token
from ecube_backend.pagination import CustomPageNumberPagination
from django.db import connection
import pandas as pd
import requests
import json
from datetime import datetime

def send_notification(registration_ids, message_title, message_desc, message_type):
    fcm_api = "AAAAqbxPQ_Q:APA91bGWil8YXU8Zr1CLa-tqObZ-DVJUqq0CrN0O76bltTApN51we3kOqrA4rRFZUXauBDtkcR3nWCQ60UPWuroRZpJxuCBhgD6CdHAnjqh8V2zPIzLvuvERmbipMHIoJJxuBegJW3a3"
    url = "https://fcm.googleapis.com/fcm/send"

    headers = {
        "Content-Type": "application/json",
        "Authorization": 'key=' + fcm_api
    }

    payload = {
        "registration_ids": registration_ids,
        "priority": "high",
        "notification": {
            "body": message_desc,
            "title": message_title,
        },
        "data": {
            "type": message_type,
        }
    }

    result = requests.post(url, data=json.dumps(payload), headers=headers)
    print(result.json())

def send_notification_main(registration,message_title, message_desc, message_type):
    # registration = ['dREWgJKnS5yw3KJ_0w0OaS:APA91bGFBliKfQI4itzjmdhDRCqkBDywYeSQjJvIB1f3bHYEF9QLuD70lHyi3AI9QXDofqxzbjaXXEKdeolg8bGboQQPQXeJuLluw0K3Y-h_GEhHg47Ln_OiioGMiWKpqYX-xnXSUk7b']
    result = send_notification(registration, message_title, message_desc, message_type)
    print(result)
    
class ExamResult(APIView, CustomPageNumberPagination):
    def post(self,request):
        try:
           
            batch_year = request.query_params.get('batch_year')
            class_name = request.query_params.get('class_name')
            division = request.query_params.get('division')


            if batch_year is None or class_name is None or division is None:
                return Response({"message": "batch_year, class_name and division is required"},status=status.HTTP_400_BAD_REQUEST)
         
            batch_year_notif = batch_year
            class_name_notif = class_name
            division_notif = division
                       
            
            batch_year = str(batch_year)
            class_name = str(class_name).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division).replace(" ", "")
            division = str(division).lower()
            
            data = request.data  # Get the JSON array from the request body

            if not isinstance(data, list):
                return Response({'status': 'failure', 'message': 'Request body should be a JSON array'}, status=status.HTTP_400_BAD_REQUEST)

            app_name = 'register_student_'
            table_name_examresults = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_examresults"
            table_name_leaderboard = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_leaderboard"

            for item in data:
                admission_no = item.get('admission_no')
                exam_name = item.get('exam_name')
                physics = item.get('physics')
                chemistry = item.get('chemistry')
                maths = item.get('maths')

                if admission_no is None or exam_name is None:
                    return Response({'status': 'failure', 'message': 'admission_no and exam_name are required for each item'}, status=status.HTTP_400_BAD_REQUEST)
                    
                # Insert data into the database for each item in the JSON array
                cursor = connection.cursor()
                cursor.execute(f"SELECT * FROM public.{table_name_examresults} WHERE admission_no = %s AND exam_name = %s", [admission_no, exam_name])
                query_results = cursor.fetchone()

                if query_results is None:
                    cursor.execute(f"INSERT INTO public.{table_name_examresults} (admission_no, exam_name, physics, chemistry, maths) VALUES (%s, %s, %s, %s, %s)", [admission_no, exam_name, physics, chemistry, maths])
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.execute(f"SELECT * FROM public.{table_name_leaderboard} WHERE admission_no = %s", [admission_no])
                    query_results = cursor.fetchone()
                    cursor.close()

                    print("Query Results:", query_results)

                    try:
                        if query_results is None:
                            print("Inserting into the table")
                            cursor = connection.cursor()
                            cursor.execute(f"INSERT INTO public.{table_name_leaderboard} (admission_no, physics, chemistry, maths) VALUES (%s, %s, %s, %s)", [admission_no, physics, chemistry, maths])
                        else:
                            cursor = connection.cursor()
                            cursor.execute(f"UPDATE public.{table_name_leaderboard} SET physics = physics + %s, chemistry = chemistry + %s, maths = maths + %s WHERE admission_no = %s", [physics, chemistry, maths, admission_no])

                        cursor.close()

                    except Exception as e:
                        return Response({'status': 'failure', 'message': 'admission_no, physics, chemistry, and maths are required'}, status=status.HTTP_400_BAD_REQUEST)
                    
            student_list = Student.objects.filter(batch_year=batch_year_notif, class_name=class_name_notif, division=division_notif).values('device_id')
            
            if student_list:
                device_ids = [student['device_id'] for student in student_list]

                print(device_ids)
                
                message_title_exam = "Exam Results have been published"
                message_desc_exam = "Check your exam results now for " + exam_name
                message_type_exam = "performance"
                
                message_title_leaderboard = "Leaderboard has been updated"
                message_desc_leaderboard = "Check the leaderboard now for current standings"
                message_type_leaderboard = "leaderboard"
                
                send_notification_main(device_ids,message_title_exam, message_desc_exam, message_type_exam)
                
                send_notification_main(device_ids,message_title_leaderboard, message_desc_leaderboard, message_type_leaderboard)
            
            class_group_instance = class_details.objects.get(batch_year=batch_year_notif, class_name=class_name_notif, division=division_notif)
            
            class_group_instance.exam_result = datetime.now()
            
            class_group_instance.exam_name = exam_name
            
            class_group_instance.save()
            
            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def put(self, request):
        try:
            batch_year_cap = request.query_params.get('batch_year')
            class_name_cap = request.query_params.get('class_name')
            division_cap = request.query_params.get('division')
            
            if batch_year is None or class_name is None or division is None:
                return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            batch_year = str(batch_year_cap)
            class_name = str(class_name_cap).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division_cap).replace(" ", "")
            division = str(division).lower()
            
            data = request.data  # Get the JSON array from the request body
            
            if not isinstance(data, list):
                return Response({'status': 'failure', 'message': 'Request body should be a JSON array'}, status=status.HTTP_400_BAD_REQUEST)
            
            app_name = 'register_student_'
            
            table_name_examresults = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_examresults"
            table_name_leaderboard = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_leaderboard"
            
            for item in data:
                admission_no = item.get('admission_no')
                exam_name = item.get('exam_name')
                physics = item.get('physics')
                chemistry = item.get('chemistry')
                maths = item.get('maths')

                if admission_no is None or exam_name is None:
                    return Response({'status': 'failure', 'message': 'admission_no and exam_name are required for each item'}, status=status.HTTP_400_BAD_REQUEST)

                # Insert data into the database for each item in the JSON array
                cursor = connection.cursor()
                cursor.execute(f"SELECT * FROM public.{table_name_examresults} WHERE admission_no = %s AND exam_name = %s", [admission_no, exam_name])
                query_results = cursor.fetchone()
                
                if query_results:
                    cursor.execute(f"UPDATE public.{table_name_examresults} SET physics = %s, chemistry = %s, maths = %s WHERE admission_no = %s AND exam_name = %s", [physics, chemistry, maths, admission_no, exam_name])
                    cursor.close() 
                    
                    cursor = connection.cursor()
                    cursor.execute(f"SELECT * FROM public.{table_name_leaderboard} WHERE admission_no = %s", [admission_no])
                    query_results = cursor.fetchone()
                    cursor.close()

                    print("Query Results:", query_results)

                    try:
                        if query_results:
                            print("Updating the table")
                            cursor = connection.cursor()
                            cursor.execute(f"SELECT physics, chemistry, maths FROM public.{table_name_examresults} WHERE admission_no = %s", [admission_no])
                            query_results = cursor.fetchall()
                            cursor.close()

                            # Calculate the sum of marks for each subject
                            total_physics = sum([result[0] for result in query_results])
                            total_chemistry = sum([result[1] for result in query_results])
                            total_maths = sum([result[2] for result in query_results])

                            # Update the leaderboard
                            cursor = connection.cursor()
                            cursor.execute(f"UPDATE public.{table_name_leaderboard} SET physics = %s, chemistry = %s, maths = %s WHERE admission_no = %s", [total_physics, total_chemistry, total_maths, admission_no])
                            cursor.close()

                    except Exception as e:
                        return Response({'status': 'failure', 'message': 'admission_no, physics, chemistry, and maths are required'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'status': 'failure', 'message': 'admission_no and exam_name are required for each item'}, status=status.HTTP_400_BAD_REQUEST)
                
            class_group_instance = class_details.objects.get(batch_year=batch_year_cap, class_name=class_name_cap, division=division_cap)
            
            class_group_instance.exam_result = datetime.now()
            
            class_group_instance.exam_name = exam_name
            
            class_group_instance.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    def delete(self, request):
        try:
            batch_year_cap = request.query_params.get('batch_year')
            class_name_cap = request.query_params.get('class_name')
            division_cap = request.query_params.get('division')
            
            
            if batch_year is None or class_name is None or division is None:
                return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            batch_year = str(batch_year_cap)
            class_name = str(class_name_cap).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division_cap).replace(" ", "")
            division = str(division).lower()
            
            data = request.data  # Get the JSON array from the request body
            
            if not isinstance(data, list):
                return Response({'status': 'failure', 'message': 'Request body should be a JSON array'}, status=status.HTTP_400_BAD_REQUEST)
            
            app_name = 'register_student_'
            
            table_name_examresults = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_examresults"
            table_name_leaderboard = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_leaderboard"
            
            for item in data:
                admission_no = item.get('admission_no')
                exam_name = item.get('exam_name')
                physics = item.get('physics')
                chemistry = item.get('chemistry')
                maths = item.get('maths')

                if admission_no is None or exam_name is None:
                    return Response({'status': 'failure', 'message': 'admission_no and exam_name are required for each item'}, status=status.HTTP_400_BAD_REQUEST)

                # Insert data into the database for each item in the JSON array
                cursor = connection.cursor()
                cursor.execute(f"SELECT * FROM public.{table_name_examresults} WHERE admission_no = %s AND exam_name = %s", [admission_no, exam_name])
                query_results = cursor.fetchone()
                
                if query_results:
                    cursor.execute(f"DELETE FROM public.{table_name_examresults} WHERE admission_no = %s AND exam_name = %s", [admission_no, exam_name])
                    cursor.close() 
                    
                    cursor = connection.cursor()
                    cursor.execute(f"SELECT * FROM public.{table_name_leaderboard} WHERE admission_no = %s", [admission_no])
                    query_results = cursor.fetchone()
                    cursor.close()

                    print("Query Results:", query_results)

                    try:
                        if query_results:
                            print("Updating the table")
                            cursor = connection.cursor()
                            cursor.execute(f"SELECT physics, chemistry, maths FROM public.{table_name_examresults} WHERE admission_no = %s", [admission_no])
                            query_results = cursor.fetchall()
                            cursor.close()

                            # Calculate the sum of marks for each subject
                            total_physics = sum([result[0] for result in query_results])
                            total_chemistry = sum([result[1] for result in query_results])
                            total_maths = sum([result[2] for result in query_results])

                            # Update the leaderboard
                            cursor = connection.cursor()
                            cursor.execute(f"UPDATE public.{table_name_leaderboard} SET physics = %s, chemistry = %s, maths = %s WHERE admission_no = %s", [total_physics, total_chemistry, total_maths, admission_no])
                            cursor.close()

                    except Exception as e:
                        return Response({'status': 'failure', 'message': 'admission_no, physics, chemistry, and maths are required'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'status': 'failure', 'message': 'admission_no and exam_name are required for each item'}, status=status.HTTP_400_BAD_REQUEST)
                
            class_group_instance = class_details.objects.get(batch_year=batch_year_cap, class_name=class_name_cap, division=division_cap)
            
            class_group_instance.exam_result = None
            
            class_group_instance.exam_name = None
            
            class_group_instance.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
    def get(self, request):
        try:
            batch_year_cap = request.query_params.get('batch_year')
            class_name_cap = request.query_params.get('class_name')
            division_cap = request.query_params.get('division')
            exam_type = request.query_params.get('exam_type')
            
            if batch_year_cap is None or class_name_cap is None or division_cap is None:
                class_group_instance = class_details.objects.filter(
                        exam_result__isnull=False,
                        exam_name__isnull=False
                    ).order_by('-exam_result').first()
                
                if class_group_instance is None:
                    return Response({"message": "Nothing to show here"}, status=status.HTTP_200_OK)
                else:
                    batch_year_cap = class_group_instance.batch_year
                    class_name_cap = class_group_instance.class_name
                    division_cap = class_group_instance.division
                    exam_name = class_group_instance.exam_name
                    
            batch_year = str(batch_year_cap)
            class_name = str(class_name_cap).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division_cap).replace(" ", "")
            division = str(division).lower()
            
            
            app_name = 'register_student_'
            
            table_name_examresults = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_examresults"
            
            
            if not exam_type:
                
                exam_type = exam_name
                
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM public.{table_name_examresults} WHERE exam_name = %s", [exam_type])
            query_results = cursor.fetchall()
        
            cursor.close()
            
            exam_results = []
            if query_results:
                for result in query_results:
                    
                    try:
                        student_instance = Student.objects.get(admission_no=result[1])
                        
                        exam_results.append({
                            'user_id': student_instance.id,
                            'name': student_instance.name,
                            'admission_no': result[1],
                            'exam_name': result[2],
                            'physics': result[3],
                            'chemistry': result[4],
                            'maths': result[5]
                        })
                    except Exception as e:
                        print(e)
                        pass
                    
            exam_results = self.paginate_queryset(exam_results, request)
            
            response = {
                'class_name': class_name_cap,
                'batch_year': batch_year_cap,
                'division': division_cap, 
                'exam_name' : exam_type,
                'result_data': exam_results,
                "total_pages": self.page.paginator.num_pages,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
                "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,
            }
            return Response(response, status=status.HTTP_200_OK)
    
        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class GetExamType(APIView):
    def get(self,request):
        try:
            batch_year = request.query_params.get('batch_year')
            class_name = request.query_params.get('class_name')
            division = request.query_params.get('division')
            
            
            if batch_year is None or class_name is None or division is None:
                return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            batch_year = str(batch_year)
            class_name = str(class_name).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division).replace(" ", "")
            division = str(division).lower()
            
            
            app_name = 'register_student_'
            
            table_name_examresults = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_examresults"
            
            cursor = connection.cursor()
            cursor.execute(f"SELECT DISTINCT exam_name FROM public.{table_name_examresults}")
            query_results = cursor.fetchall()
            
            if query_results:
                exam_types = [result[0] for result in query_results]
                return Response({'exam_types': exam_types}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AddExamResultBulk(APIView):
    def post(self, request):
        batch_year = request.GET.get('batch_year')
        class_name = request.GET.get('class_name')
        division = request.GET.get('division')
        
        if batch_year is None or class_name is None or division is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name, and division are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "").lower()
        division = str(division).replace(" ", "").lower()
        
        app_name = 'register_student'
        table_name_examresults = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_examresults"
        table_name_leaderboard = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_leaderboard"
        
        try:
            # Process uploaded CSV or XLSX file
            file = request.FILES['exam_results_file']
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return Response({'status': 'failure', 'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cursor = connection.cursor()
            
            for index, row in df.iterrows():
                admission_no = str(row.get('admission_no'))
                exam_name = str(row.get('exam_name'))
                physics = row.get('physics')
                chemistry = row.get('chemistry')
                maths = row.get('maths')
                
                physics = None if pd.isna(physics) else physics
                chemistry = None if pd.isna(chemistry) else chemistry
                maths = None if pd.isna(maths) else maths
                
                # Check if the entry already exists in exam results table
                cursor.execute(f"SELECT * FROM public.{table_name_examresults} WHERE admission_no = %s AND exam_name = %s", [admission_no, exam_name])
                query_results = cursor.fetchone()
                
                print("Query Results:", query_results)
                if query_results is None:
                    # Insert into exam results table with NULL values for empty fields
                    print(physics, chemistry, maths)
                    cursor.execute(f"INSERT INTO public.{table_name_examresults} (admission_no, exam_name, physics, chemistry, maths) VALUES (%s, %s, %s, %s, %s)", [admission_no, exam_name, physics, chemistry, maths])
                    
                    # Check if the entry already exists in leaderboard table
                    cursor.execute(f"SELECT * FROM public.{table_name_leaderboard} WHERE admission_no = %s", [admission_no])
                    query_results_leaderboard = cursor.fetchone()
                    
                    if query_results_leaderboard is None:
                        # Insert into leaderboard table with NULL values for empty fields
                        cursor.execute(f"INSERT INTO public.{table_name_leaderboard} (admission_no, physics, chemistry, maths) VALUES (%s, %s, %s, %s)", [admission_no, physics, chemistry, maths])
                    else:
                        # Update leaderboard table
                        cursor.execute(f"UPDATE public.{table_name_leaderboard} SET physics = physics + %s, chemistry = chemistry + %s, maths = maths + %s WHERE admission_no = %s", [physics, chemistry, maths, admission_no])
            
            cursor.close()
            
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ExamResultsView(APIView):
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
            return Response({'error': 'The access token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)
        # Generate a new access token
        user = Student.objects.get(id=user_id) 
        
        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division
        admission_no = user.admission_no
        
        if batch_year is None or class_name is None or division is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name, and division are required'}, status=status.HTTP_400_BAD_REQUEST)

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "").lower()
        division = str(division).replace(" ", "").lower()

        app_name = 'register_student'
        table_name_examresults = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_examresults"

        try:
            cursor = connection.cursor()

            # Modify the SQL query to retrieve marks for each subject in every exam for the specific admission number
            cursor.execute(f"""
                SELECT DISTINCT subject
                FROM (
                    SELECT 'physics' AS subject
                    UNION ALL
                    SELECT 'chemistry' AS subject
                    UNION ALL
                    SELECT 'maths' AS subject
                ) AS subjects
            """)
            subject_results = cursor.fetchall()
            
            exams_data = []

            # Assuming subject_results is a list of subjects
            for subject in subject_results:
                subject = subject[0]  # Extract the subject name
                
                cursor.execute(f"""
                    SELECT exam_name, marks
                    FROM (
                        SELECT admission_no,
                            exam_name,
                            'physics' AS subject,
                            physics AS marks
                        FROM public.{table_name_examresults}
                        UNION ALL
                        SELECT admission_no,
                            exam_name,
                            'chemistry' AS subject,
                            chemistry AS marks
                        FROM public.{table_name_examresults}
                        UNION ALL
                        SELECT admission_no,
                            exam_name,
                            'maths' AS subject,
                            maths AS marks
                        FROM public.{table_name_examresults}
                    ) AS subquery
                    WHERE admission_no = '{admission_no}' AND subject = '{subject}'  -- Filter by admission_no and subject
                """)
                subject_data = cursor.fetchall()
                
                data_for_subject = [{'exam_name': exam_name, 'marks': marks} for exam_name, marks in subject_data if marks is not None]
                if data_for_subject:  # Check if data is not empty
                    exams_data.append({'subject': subject, 'data': data_for_subject})


            cursor.close()

            if not exams_data:
                return Response({'status': 'failure', 'message': 'No exam results found for the specified admission_no'}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate the total number of exams
            total_exams = sum(len(subject['data']) for subject in exams_data)

            # Create the final response structure
            response_data = {
                'no_of_exams': str(total_exams),  # Number of exams is the sum of all subject exams
                'results': exams_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'status': 'failure', 'message': 'Internal error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class AdminExamResultsView(APIView):
    def get(self, request):
        
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return Response({'error': 'The user id is not provided in the params.'}, status=status.HTTP_401_UNAUTHORIZED)
        # Generate a new access token
        user = Student.objects.get(id=user_id) 
        
        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division
        admission_no = user.admission_no
        
        if batch_year is None or class_name is None or division is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name, and division are required'}, status=status.HTTP_400_BAD_REQUEST)

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "").lower()
        division = str(division).replace(" ", "").lower()

        app_name = 'register_student'
        table_name_examresults = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_examresults"

        try:
            cursor = connection.cursor()

            # Modify the SQL query to retrieve marks for each subject in every exam for the specific admission number
            cursor.execute(f"""
                SELECT DISTINCT subject
                FROM (
                    SELECT 'physics' AS subject
                    UNION ALL
                    SELECT 'chemistry' AS subject
                    UNION ALL
                    SELECT 'maths' AS subject
                ) AS subjects
            """)
            subject_results = cursor.fetchall()

            exams_data = []

            # Assuming subject_results is a list of subjects
            for subject in subject_results:
                subject = subject[0]  # Extract the subject name
                
                cursor.execute(f"""
                    SELECT exam_name, marks
                    FROM (
                        SELECT admission_no,
                            exam_name,
                            'physics' AS subject,
                            physics AS marks
                        FROM public.{table_name_examresults}
                        UNION ALL
                        SELECT admission_no,
                            exam_name,
                            'chemistry' AS subject,
                            chemistry AS marks
                        FROM public.{table_name_examresults}
                        UNION ALL
                        SELECT admission_no,
                            exam_name,
                            'maths' AS subject,
                            maths AS marks
                        FROM public.{table_name_examresults}
                    ) AS subquery
                    WHERE admission_no = '{admission_no}' AND subject = '{subject}'  -- Filter by admission_no and subject
                """)
                subject_data = cursor.fetchall()
                
                data_for_subject = [{'exam_name': exam_name, 'marks': marks} for exam_name, marks in subject_data if marks is not None]
                if data_for_subject:  # Check if data is not empty
                    exams_data.append({'subject': subject, 'data': data_for_subject})


            cursor.close()

            if not exams_data:
                return Response({'status': 'failure', 'message': 'No exam results found for the specified admission_no'}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate the total number of exams
            total_exams = sum(len(subject['data']) for subject in exams_data)

            # Create the final response structure
            response_data = {
                'no_of_exams': str(total_exams),  # Number of exams is the sum of all subject exams
                'results': exams_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'status': 'failure', 'message': 'Internal error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
