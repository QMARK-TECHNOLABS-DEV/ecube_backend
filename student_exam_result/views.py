from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from register_student.models import Student
from client_auth.utils import TokenUtil
from client_auth.models import Token
from django.http import JsonResponse
from django.db import connection
import pandas as pd

class AddExamResult(APIView):
    def post(self,request):
        try:
            batch_year = request.GET.get('batch_year')
            class_name = request.GET.get('class_name')
            division = request.GET.get('division')
            
            if batch_year is None or class_name is None or division is None:
                return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            batch_year = str(batch_year)
            class_name = str(class_name).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division).replace(" ", "")
            division = str(division).lower()
            
            admission_no = request.data['admission_no']
            exam_name = request.data['exam_name']
            physics = request.data['physics']
            chemistry = request.data['chemistry']
            maths = request.data['maths']
            
            physics = None if physics is None else physics
            chemistry = None if chemistry is None else chemistry
            maths = None if maths is None else maths
            
            if (admission_no is None or admission_no == "") or (exam_name is None or exam_name == ""):
                return Response({'status': 'failure', 'message': 'admission_no and exam_name are required'}, status=status.HTTP_400_BAD_REQUEST)


            app_name = 'register_student_'
            table_name_examresults = app_name + app_name +  batch_year + "_" + class_name + "_" + division + "_examresults"
            table_name_leaderboard = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_leaderboard"
            
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM public.{table_name_examresults} WHERE admission_no = %s AND exam_name = %s", [admission_no, exam_name])
            query_results = cursor.fetchone()
            
            if query_results is None:
            
                cursor = connection.cursor()
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
                    
                    return Response({'status': 'success'}, status=status.HTTP_200_OK)
                
                except:
                    return Response({'status': 'failure', 'message': 'admission_no, physics, chemistry and maths are required'}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                return Response({'status': 'failure', 'message': 'Exam already marked for student'}, status=status.HTTP_400_BAD_REQUEST)
        
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

                exams_data.append({
                    'subject': subject,
                    'data': [{'exam_name': exam_name, 'marks': marks} for exam_name, marks in subject_data]
                })

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
