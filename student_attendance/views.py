from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from register_student.models import Student, class_details
from client_auth.utils import TokenUtil
from client_auth.models import Token
from django.http import JsonResponse
from collections import defaultdict
from datetime import datetime
import pandas as pd

class AddAttendance(APIView):
    def post(self, request):
        
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
        month_year_number = request.data['month_year_number']
        date = request.data['date']
        status_student = request.data['status']
        
        if admission_no is None or month_year_number is None or date is None or status is None:
            return Response({'status': 'failure', 'message': 'admission_no, month_year_number, date and status are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        app_name = 'register_student_'
        table_name = app_name + app_name+  batch_year + "_" + class_name + "_" + division + "_attendance"
        
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO public.{table_name} (admission_no, month_year_number, date, status) VALUES (%s, %s, %s, %s)", [admission_no, month_year_number, date, status_student])
        cursor.close()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class AddAttendanceBulk(APIView):
    def post(self, request):
        batch_year = request.GET.get('batch_year')
        class_name = request.GET.get('class_name')
        division = request.GET.get('division')
        date_attendance = request.GET.get('date')

        if batch_year is None or class_name is None or division is None or date_attendance is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name, date and division are required'}, status=status.HTTP_400_BAD_REQUEST)

        class_instance = class_details.objects.filter(batch_year=batch_year, class_name=class_name, division=division).first()
        
        if class_instance is None:
            return Response({'status': 'failure', 'message': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "")
        class_name = str(class_name).lower()
        division = str(division).replace(" ", "")
        division = str(division).lower()

        # Process uploaded CSV or XLSX file
        try:
            file = request.FILES['attendance_file']
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return Response({'status': 'failure', 'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Insert attendance data into the database
        date_attendance = str(date_attendance)

        # Insert attendance data into the database
        app_name = 'register_student'
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"
        
        student_list = Student.objects.all().values('name','id')
        
        try:
            for index, row in df.iterrows():
                first_name = row.get('First name', None)
                last_name = row.get('Last name', None)
                full_name = str(first_name) + str(last_name)

                full_name = full_name.replace(" ", "").lower()
                
                print(full_name)
                
                for student in student_list:
                    
                    name_db = student['name'].replace(" ", "").lower()
                    
                    print(name_db)
                    
                    if full_name == name_db:
                        student_instance = Student.objects.get(id=student['id'])
                    else:
                        student_instance = None
                
                
                


                    if student_instance is not None:
                        admission_no = student_instance.admission_no
                        
                        cursor = connection.cursor()
                        
                        print("Found student")
                        # Convert date to a string
                        date = date_attendance
                        
                        status_student = 'P'

                        month_year_number = date[3:]

                        if admission_no is not None and month_year_number is not None and date is not None and status_student is not None:
                            cursor.execute(f"INSERT INTO public.{table_name} (admission_no, month_year_number, date, status) VALUES (%s, %s, %s, %s)", [admission_no, month_year_number, date, status_student])
                            
                            print("Inserted")
                            cursor.close()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            cursor.close()
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class AdminGetAttendanceMonth(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        
        if user_id is None:
            return Response({'status': 'failure', 'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_instance = Student.objects.get(id=user_id)
        
        batch_year = user_instance.batch_year
        class_name = user_instance.class_name
        division = user_instance.division
        
        if batch_year is None or class_name is None or division is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        class_details_instance = class_details.objects.filter(batch_year=batch_year, class_name=class_name, division=division).first()
        
        if class_details_instance is None:
            return Response({'status': 'failure', 'message': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "")
        class_name = str(class_name).lower()
        division = str(division).replace(" ", "")
        division = str(division).lower()
        

        app_name = 'register_student'
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"

       
        cursor = connection.cursor()
        cursor.execute(f"SELECT DISTINCT month_year_number FROM public.{table_name} ORDER BY month_year_number DESC;")
        distinct_dates = [row[0] for row in cursor.fetchall()]
        cursor.close()
   
        response_data = {
            'status': 'success',
            'distinct_dates': distinct_dates,
        }

  
        return Response(response_data, status=status.HTTP_200_OK)
class AdminGetAttendance(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        
        if user_id is None:
            return Response({'status': 'failure', 'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_instance = Student.objects.get(id=user_id)
        
        batch_year = user_instance.batch_year
        class_name = user_instance.class_name
        division = user_instance.division
        
        if batch_year is None or class_name is None or division is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        class_details_instance = class_details.objects.filter(batch_year=batch_year, class_name=class_name, division=division).first()
        
        if class_details_instance is None:
            return Response({'status': 'failure', 'message': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "")
        class_name = str(class_name).lower()
        division = str(division).replace(" ", "")
        division = str(division).lower()
        

        app_name = 'register_student'
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"

        month_year_number = request.GET.get('month_year_number')
    
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM public.{table_name} WHERE admission_no = %s AND month_year_number = %s;", [user_instance.admission_no, month_year_number])
        query_result = cursor.fetchall()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(f"SELECT DISTINCT date FROM public.{table_name} WHERE month_year_number = %s;", [month_year_number])
        distinct_dates = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        # Create an empty dictionary to store attendance information
        attendance_data = {}

        # Function to convert date strings to objects with year, month, and day fields as integers
        def date_string_to_object(date_string):
            day, month, year = map(int, date_string.split('/'))
            return {"year": f"{year}", "month": f"{month:02d}", "day": f"{day:02d}"}

        # Iterate through the query result and build attendance_data
        for row in query_result:
            id, admission_no, month_year, date, status_att = row
            date_obj = date_string_to_object(date)
            attendance_data[date] = status_att

        # Iterate through distinct_dates and mark absent if date is missing in attendance_data
        for date in distinct_dates:
            if date not in attendance_data:
                attendance_data[date] = "A"

        # Create the final response dictionary
        present_days = [date_string_to_object(date) for date, status_att in attendance_data.items() if status_att == "P"]
        absent_days = [date_string_to_object(date) for date, status_att in attendance_data.items() if status_att == "A"]

        response_data = {"attendance_result": {"present_days": present_days, "absent_days": absent_days}}

        return Response(response_data, status=status.HTTP_200_OK)
    
        
class GetAttendance(APIView):
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
            return JsonResponse({'error': 'The refresh token is not associated with a user.'}, status=401)

        # Generate a new access token
        user = Student.objects.get(id=user_id)
        
        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division
        
        if batch_year is None or class_name is None or division is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "")
        class_name = str(class_name).lower()
        division = str(division).replace(" ", "")
        division = str(division).lower()
        

        app_name = 'register_student'
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"

        month_year_number = request.GET.get('month_year_number')

        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM public.{table_name} WHERE admission_no = %s AND month_year_number = %s;", [user.admission_no, month_year_number])
        query_result = cursor.fetchall()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(f"SELECT DISTINCT date FROM public.{table_name} WHERE month_year_number = %s;", [month_year_number])
        distinct_dates = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        # Create an empty dictionary to store attendance information
        attendance_data = {}

        # Function to convert date strings to objects with year, month, and day fields as integers
        def date_string_to_object(date_string):
            day, month, year = map(int, date_string.split('/'))
            return {"year": f"{year}", "month": f"{month:02d}", "day": f"{day:02d}"}

        # Iterate through the query result and build attendance_data
        for row in query_result:
            id, admission_no, month_year, date, status_att = row
            date_obj = date_string_to_object(date)
            attendance_data[date] = status_att

        # Iterate through distinct_dates and mark absent if date is missing in attendance_data
        for date in distinct_dates:
            if date not in attendance_data:
                attendance_data[date] = "A"

        # Create the final response dictionary
        present_days = [date_string_to_object(date) for date, status_att in attendance_data.items() if status_att == "P"]
        absent_days = [date_string_to_object(date) for date, status_att in attendance_data.items() if status_att == "A"]

        response_data = {"attendance_result": {"present_days": present_days, "absent_days": absent_days}}

        return Response(response_data, status=status.HTTP_200_OK)
    
    
class GetAttendanceYearStatus(APIView):
    def get(self, request):
        
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
                return JsonResponse({'error': 'The refresh token is not associated with a user.'}, status=401)

            # Generate a new access token
            user = Student.objects.get(id=user_id)
            
            batch_year = user.batch_year
            class_name = user.class_name
            division = user.division
            
            if batch_year is None or class_name is None or division is None:
                return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            class_details_instance = class_details.objects.filter(batch_year=batch_year, class_name=class_name, division=division).first()
            
            if class_details_instance is None:
                return Response({'status': 'failure', 'message': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
            batch_year = str(batch_year)
            class_name = str(class_name).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division).replace(" ", "")
            division = str(division).lower()
            

            app_name = 'register_student'
            table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"
            
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM public.{table_name} WHERE admission_no = %s;", [user.admission_no])
            year_query_result = cursor.fetchall()
            cursor.close()
            
            cursor = connection.cursor()
            cursor.execute(f"SELECT DISTINCT date FROM public.{table_name}")
            distinct_dates = [row[0] for row in cursor.fetchall()]
            cursor.close()
           
            
            attendance_data = {}

            # Function to convert date strings to objects with year, month, and day fields as integers
            def date_string_to_object(date_string):
                day, month, year = map(int, date_string.split('/'))
                return {"year": f"{year}", "month": f"{month:02d}", "day": f"{day:02d}"}

            # Iterate through the query result and build attendance_data
            for row in year_query_result:
                id, admission_no, month_year, date, status_att = row
                date_obj = date_string_to_object(date)
                attendance_data[date] = status_att

            # Iterate through distinct_dates and mark absent if date is missing in attendance_data
            for date in distinct_dates:
                if date not in attendance_data:
                    attendance_data[date] = "A"

            # Create the final response dictionary
            present_days = [date_string_to_object(date) for date, status_att in attendance_data.items() if status_att == "P"]
            absent_days = [date_string_to_object(date) for date, status_att in attendance_data.items() if status_att == "A"]
            
            total_working_days = len(present_days) + len(absent_days)

            response_data = {"total_working_days": total_working_days, "present_days": len(present_days), "absent_days": len(absent_days)}
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except:
            return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)