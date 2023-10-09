from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from register_student.models import Student
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
            return Response({'status': 'failure', 'message': 'batch_year, class_name, and division are required'}, status=status.HTTP_400_BAD_REQUEST)

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

        # Convert 'date' to the desired format 'dd/mm/yyyy'
        def format_date(date_str):
            if isinstance(date_str, datetime):
                return date_str.strftime('%d/%m/%Y')
            elif isinstance(date_str, str):
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    return date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    # Handle the case where the input is already in the desired format
                    return date_str
            return None

        df['date'] = df['date'].apply(format_date)

        # Convert 'month_year_number' to the desired format 'mm/yyyy'
        def format_month_year(month_year_str):
            if isinstance(month_year_str, datetime):
                return month_year_str.strftime('%m/%Y')
            elif isinstance(month_year_str, str):
                try:
                    date_obj = datetime.strptime(month_year_str, '%Y-%m-%d %H:%M:%S')
                    return date_obj.strftime('%m/%Y')
                except ValueError:
                    # Handle the case where the input is already in the desired format
                    return date_obj.strftime('%m/%Y')
            return None

       
        # Insert attendance data into the database
        app_name = 'register_student'
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"

        cursor = connection.cursor()

        try:
            for index, row in df.iterrows():
                first_name= row.get('First name', None)
                last_name = row.get('Last name', None)
                full_name = first_name + last_name
                
                full_name = full_name.replace(" ", "")
                full_name = full_name.lower()
                
                admission_no = Student.objects.filter(full_name=full_name).first().admission_no
                
                if admission_no is None:
                    continue
                
                date = date_attendance
                status_student = 'P'
                
                month_year_number = date[4:]

                if admission_no is not None and month_year_number is not None and date is not None and status_student is not None:
                    cursor.execute(f"INSERT INTO public.{table_name} (admission_no, month_year_number, date, status) VALUES (%s, %s, %s, %s)", [admission_no, month_year_number, date, status_student])

            cursor.close()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            cursor.close()
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        app_name = 'register_student'
        table_name = app_name + '_' + app_name + '_' + user.batch_year + "_" + user.class_name + "_" + user.division + "_attendance"

        month_year_number = request.GET.get('month_year_number')

        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM public.{table_name} WHERE admission_no = %s AND month_year_number = %s", [user.admission_no, month_year_number])
        query_result = cursor.fetchall()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute(f"SELECT DISTINCT date FROM public.{table_name}")
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