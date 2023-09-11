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


        app_name = 'register_student'
        table_name_examresults = app_name + '_' + app_name+ '_'+ batch_year + "_" + class_name + "_" + division + "_examresults"
        table_name_leaderboard = app_name + '_' + app_name+ '_'+ batch_year + "_" + class_name + "_" + division + "_leaderboard"
        
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