from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..register_student.models import Student, class_details
from ..client_auth.utils import TokenUtil

from django.http import JsonResponse
import pandas as pd
import requests
import json
from datetime import datetime
from ecube_backend.pagination import CustomPageNumberPagination

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
    
class DeleteAttendance(APIView):
    def delete(self,request):
        try:
            batch_year = request.GET.get('batch_year')
            class_name = request.GET.get('class_name')
            division = request.GET.get('division')
            admission_no = request.GET.get('admission_no')
            
            if batch_year is None or class_name is None or division is None:
                return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            batch_year = str(batch_year)
            class_name = str(class_name).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division).replace(" ", "")
            division = str(division).lower()
            
            app_name = 'register_student'
            table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"
            
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM public.{table_name} WHERE admission_no = %s;", [admission_no])
            cursor.close()
            
            return Response({'status': 'successfully deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DeleteAttendanceBulk(APIView):
    def delete(self,request):
        try:
            batch_year = request.GET.get('batch_year')
            class_name = request.GET.get('class_name')
            division = request.GET.get('division')
            date = request.GET.get('date')
            
            if batch_year is None or class_name is None or division is None:
                return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            batch_year = str(batch_year)
            class_name = str(class_name).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division).replace(" ", "")
            division = str(division).lower()
            
            app_name = 'register_student'
            table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"
            
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM public.{table_name} WHERE date = %s;", [date])
            cursor.close()
            
            return Response({'status': 'successfully deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class AddAttendance(APIView):
    def post(self, request):
        
        batch_year = request.GET.get('batch_year')
        class_name = request.GET.get('class_name')
        division = request.GET.get('division')
        subject = request.GET.get('subject')
        
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
        cursor.execute(f"INSERT INTO public.{table_name} (admission_no, month_year_number, date, status,subject) VALUES (%s,%s, %s, %s, %s)", [admission_no, month_year_number, date, status_student,subject])
        cursor.close()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class AddAttendanceBulk(APIView):
    def post(self, request):
        batch_year = request.GET.get('batch_year')
        class_name = request.GET.get('class_name')
        division = request.GET.get('division')
        date_attendance = request.GET.get('date')
        subject = request.GET.get('subject')
        
        class_name_notif = class_name
        batch_year_notif = batch_year
        division_notif = division

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
            file  = request.data.get('attendance_file')

            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return Response({'status': 'failure', 'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        print(request.content_type)
        print(request.data)

        # Insert attendance data into the database
        date_attendance = str(date_attendance)

        # Insert attendance data into the database
        app_name = 'register_student'
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"
        
        student_list = Student.objects.filter(class_name=class_name_notif, batch_year=batch_year_notif, division=division_notif).values('id', 'name', 'device_id')
        
        try:
            for index, row in df.iterrows():
                first_name = row.get('First name', None)
                last_name = row.get('Last name', None)
                
                if str(last_name) == "nan":
                    last_name = ""
                full_name = str(first_name) + str(last_name)

                full_name = full_name.replace(" ", "").lower()
                
                print(full_name)
                
                for student in student_list:
                    
                    name_db = student['name'].replace(" ", "").lower()
                    
                    
                    if full_name == name_db:
                        student_instance = Student.objects.get(id=student['id'])
                    else:
                        student_instance = None
                

                    if student_instance is not None:
                        admission_no = student_instance.admission_no
                        
                        print(admission_no)
                        cursor = connection.cursor()
                        
                        print("Found student")
                        # Convert date to a string
                        date = date_attendance
                        
                        status_student = 'P'

                        month_year_number = date[3:]

                        if admission_no is not None and month_year_number is not None and date is not None and status_student is not None:
                            cursor.execute(f"INSERT INTO public.{table_name} (admission_no, month_year_number, date, status,subject) VALUES (%s,%s, %s, %s, %s)", [admission_no, month_year_number, date, status_student,subject])
                            
                            print("Inserted")
                            cursor.close()
                            
            if student_list:
                device_ids = [student['device_id'] for student in student_list]

                print(device_ids)
                
                message_title = "Attendance Added"
                message_desc = "Attendance has been added for " + date_attendance
                message_type = "attendence"
                send_notification_main(device_ids,message_title, message_desc, message_type)
            
            class_group_instance = class_details.objects.get(batch_year=batch_year_notif, class_name=class_name_notif, division=division_notif)
            
            class_group_instance.attendance = datetime.now()
            
            class_group_instance.attendance_date = date_attendance
            
            class_group_instance.save()
            return Response({'status': 'success',"message": "Attendance added and notification send"}, status=status.HTTP_200_OK)
        except Exception as e:
            cursor.close()
            print(e)
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class AdminGetAttendanceMonth(APIView):
    def get(self, request):
        
        batch_year_cap = request.query_params.get('batch_year')
        class_name_cap = request.query_params.get('class_name')
        division_cap = request.query_params.get('division')
        subject = request.query_params.get('subject')
        
        if batch_year_cap is None or class_name_cap is None or division_cap is None:
            return Response({'status': 'failure', 'message': 'batch_year, class_name and division are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        class_details_instance = class_details.objects.filter(batch_year=batch_year_cap, class_name=class_name_cap, division=division_cap).first()
        
        if class_details_instance is None:
            return Response({'status': 'failure', 'message': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        batch_year = str(batch_year_cap)
        class_name = str(class_name_cap).replace(" ", "")
        class_name = str(class_name).lower()
        division = str(division_cap).replace(" ", "")
        division = str(division).lower()
        

        app_name = 'register_student'
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"

        distinct_dates = []
        cursor = connection.cursor()
        cursor.execute(f"SELECT DISTINCT TO_DATE(date, 'DD/MM/YYYY') FROM public.{table_name} WHERE subject = %s ORDER BY TO_DATE(date, 'DD/MM/YYYY') DESC;", [subject])
        for row in cursor.fetchall():
            date_components = str(row[0]).split("-")
            formatted_date = "{}/{}/{}".format(date_components[2], date_components[1], date_components[0])
            distinct_dates.append(formatted_date)
        cursor.close()


        response_data = {
            'distinct_dates': distinct_dates
        }

        return Response(response_data, status=status.HTTP_200_OK)

class AdminGetAttendance(APIView,CustomPageNumberPagination):
    def get(self, request):
        
        try:
        
            batch_year_cap = request.query_params.get('batch_year')
            class_name_cap = request.query_params.get('class_name')
            division_cap = request.query_params.get('division')
            query_date = request.query_params.get('date')
            subject = request.query_params.get('subject')
            
            subject = str(subject).lower()
        
            if batch_year_cap is None or class_name_cap is None or division_cap is None:
                class_group_instance = class_details.objects.filter(
                        attendance__isnull=False,
                        attendance_date__isnull=False
                    ).order_by('-attendance').first()
                
                if class_group_instance is None:
                    return Response({"message": "Nothing to show here"}, status=status.HTTP_200_OK)
                else:
                    batch_year_cap = class_group_instance.batch_year
                    class_name_cap = class_group_instance.class_name
                    division_cap = class_group_instance.division
                    attendance_date = class_group_instance.attendance_date

            batch_year = str(batch_year_cap)
            class_name = str(class_name_cap).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division_cap).replace(" ", "")
            division = str(division).lower()
            

            app_name = 'register_student_'
            table_name = app_name + app_name + batch_year + "_" + class_name + "_" + division + "_attendance"

            if not query_date:
                query_date = attendance_date
                
            cursor = connection.cursor()
            cursor.execute(f"SELECT DISTINCT ON (admission_no) * FROM public.{table_name} WHERE date = %s AND subject = %s;", [query_date, subject])
            query_result = cursor.fetchall()
            cursor.close()
            
            if query_result == []:
                response_data = {
                    "class_name": class_name_cap,
                    "batch_year": batch_year_cap,
                    "division": division_cap, 
                    "current_date" : query_date,
                    "attendance_result": query_result,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                    "next_page_number": None,
                    "previous_page_number": None,
                }

                return Response(response_data, status=status.HTTP_200_OK)
            
            students_instance = Student.objects.filter(batch_year=batch_year_cap,class_name=class_name_cap,division=division_cap,subjects__contains=subject)
            
            attendance_data = []

            for row in query_result:
                id, admission_no, month_year, att_date, status_att, subject_query = row
                student = students_instance.filter(admission_no=admission_no,subjects__contains=subject).first()
                if student:
                    attendance_entry = {
                        "admission_no": admission_no,
                        "name": student.name,
                        "status": status_att
                    }
                    attendance_data.append(attendance_entry)
                # else:
                #     attendance_entry = {
                #         "admission_no": admission_no,
                #         "name": "",
                #         "status": "A"
                #     }
                #     attendance_data.append(attendance_entry)

            for student in students_instance:
                if not any(entry["admission_no"] == student.admission_no for entry in attendance_data):
                    attendance_entry = {
                        "admission_no": student.admission_no,
                        "name": student.name,
                        "status": "A"
                    }
                    attendance_data.append(attendance_entry)
            
            try:       
                attendance_data = self.paginate_queryset(attendance_data,request)
                
            except Exception as e:
                return Response({'status': 'failure', 'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            response_data = {
                "class_name": class_name_cap,
                "batch_year": batch_year_cap,
                "division": division_cap, 
                "current_date" : query_date,
                "attendance_result": attendance_data,
                "total_pages": self.page.paginator.num_pages,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
                "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,
                }

            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'status': 'failure', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AdminGetIndReportAttendanceMonth(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        subject = request.GET.get('subject')
        

        if user_id is None:
            return Response({'status': 'failure', 'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_instance = Student.objects.get(id=user_id)

        subjects = str(user_instance.subjects).split(",")
        
        if subject is None:
            return Response({'status': 'failure', 'message': 'subject is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif subject not in subjects:
            return Response({'status': 'failure', 'message': 'subject does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
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
        cursor.execute(f"SELECT DISTINCT month_year_number FROM public.{table_name} WHERE subject = %s ORDER BY month_year_number DESC;",[subject])
        distinct_dates = [row[0] for row in cursor.fetchall()]
        cursor.close()
   
        response_data = {
            'status': 'success',
            'distinct_dates': distinct_dates,
        }

  
        return Response(response_data, status=status.HTTP_200_OK)
class AdminGetIndReportAttendance(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        
        subject = request.GET.get('subject')
        
        if user_id is None:
            return Response({'status': 'failure', 'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_instance = Student.objects.get(id=user_id)
        
        batch_year = user_instance.batch_year
        class_name = user_instance.class_name
        division = user_instance.division
        
        subjects = str(user_instance.subjects).split(",")
        
        if subject is None:
            return Response({'status': 'failure', 'message': 'subject is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif subject not in subjects:
            return Response({'status': 'failure', 'message': 'subject does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        print(user_instance.admission_no)
        print(month_year_number)
        
        cursor.execute(f"SELECT * FROM public.{table_name} WHERE admission_no = %s AND month_year_number = %s AND subject = %s;", [user_instance.admission_no, month_year_number,subject])
        query_result = cursor.fetchall()
        
        print(query_result)
        cursor.close()

        cursor = connection.cursor()
        
        distinct_dates = [] 

        cursor.execute(f"SELECT DISTINCT date FROM public.{table_name} WHERE month_year_number = %s AND subject = %s;", [month_year_number,subject])
        rows = cursor.fetchall()  # Fetch all rows for the current subject
        
        for row in rows:
            date = row[0]  # Extract the date from the row tuple
            if date not in distinct_dates:  # Check if the date is not already in the list
                distinct_dates.append(date)  # Add the date to the list if it's not already present
                
        print(distinct_dates)
        # Create an empty dictionary to store attendance information
        attendance_data = {}

        # Function to convert date strings to objects with year, month, and day fields as integers
        def date_string_to_object(date_string):
            day, month, year = map(int, date_string.split('/'))
            return {"year": f"{year}", "month": f"{month:02d}", "day": f"{day:02d}"}

        # Iterate through the query result and build attendance_data
        for row in query_result:
            id, admission_no, month_year, date, status_att, subject_query = row
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

        payload = TokenUtil.decode_token(token)

        # Optionally, you can extract user information or other claims from the payload
        if not payload:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = payload.get('id')

        if not user_id:
            return JsonResponse({'error': 'The refresh token is not associated with a user.'}, status=401)

        # Generate a new access token
        user = Student.objects.get(id=user_id)
        
        subjects = str(user.subjects).split(",")
        
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
        
        print(user.admission_no)
        month_year_number = request.GET.get('month_year_number')
        cursor = connection.cursor()
        
        final_query_result = []
        for subject in subjects:
            cursor.execute(f"SELECT * FROM public.{table_name} WHERE admission_no = %s AND month_year_number = %s AND subject = %s;", [user.admission_no, month_year_number,subject])
            query_result = cursor.fetchall()
            
            final_query_result.append(query_result)
           
        cursor.close()
       
        cursor = connection.cursor()
        
        distinct_dates = []  # Initialize an empty list to store distinct dates

        for subject in subjects:
            cursor.execute(f"SELECT DISTINCT date FROM public.{table_name} WHERE subject = %s AND month_year_number = %s;", [subject,month_year_number])
            rows = cursor.fetchall()  # Fetch all rows for the current subject
            
            for row in rows:
                date = row[0]  # Extract the date from the row tuple
                if date not in distinct_dates:  # Check if the date is not already in the list
                    distinct_dates.append(date)  # Add the date to the list if it's not already present

        print(distinct_dates)        
        cursor.close()
        
        # Create an empty dictionary to store attendance information
        attendance_data = {}

        # Function to convert date strings to objects with year, month, and day fields as integers
        def date_string_to_object(date_string):
            day, month, year = map(int, date_string.split('/'))
            return {"year": f"{year}", "month": f"{month:02d}", "day": f"{day:02d}"}
        
        filtered_data = [item for item in final_query_result if item]
        
        print(filtered_data)
        

        for sublist in filtered_data:
            for row in sublist:
                id, admission_no, month_year, date, status_att, subject_query = row
                date_obj = date_string_to_object(date)
                attendance_data[date] = status_att

            
        print(attendance_data)
        # Iterate through distinct_dates and mark absent if date is missing in attendance_data
        for date in distinct_dates:
            
            if date not in attendance_data:
                attendance_data[date] = "A"
                
        print(attendance_data)
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

            payload = TokenUtil.decode_token(token)

            # Optionally, you can extract user information or other claims from the payload
            if not payload:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the refresh token is associated with a user (add your logic here)
            user_id = payload.get('id')

            if not user_id:
                return JsonResponse({'error': 'The refresh token is not associated with a user.'}, status=401)

            # Generate a new access token
            user = Student.objects.get(id=user_id)
            
            print(user)
            batch_year = user.batch_year
            class_name = user.class_name
            division = user.division
            
            print(batch_year, class_name, division)
            
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
            
            subjects = user.subjects.split(",")
            
            final_query_result = []

            app_name = 'register_student'
            table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_attendance"
            
            cursor = connection.cursor()
            for subject in subjects:
                print(subject)
                cursor.execute(f"SELECT * FROM public.{table_name} WHERE admission_no = %s AND subject = %s;", [user.admission_no, subject])
                year_query_result = cursor.fetchall()
                
                if year_query_result != []:
                    final_query_result.append(year_query_result)
            cursor.close()
            
            print(final_query_result)
            
            cursor = connection.cursor()
            
            distinct_dates = []  # Initialize an empty list to store distinct dates

            for subject in subjects:
                cursor.execute(f"SELECT DISTINCT date FROM public.{table_name} WHERE subject = %s;", [subject])
                rows = cursor.fetchall()  # Fetch all rows for the current subject
                
                for row in rows:
                    date = row[0]  # Extract the date from the row tuple
                    if date not in distinct_dates:  # Check if the date is not already in the list
                        distinct_dates.append(date)  # Add the date to the list if it's not already present

            print(distinct_dates)        
            cursor.close()
           
            
            attendance_data = {}

            # Function to convert date strings to objects with year, month, and day fields as integers
            def date_string_to_object(date_string):
                day, month, year = map(int, date_string.split('/'))
                return {"year": f"{year}", "month": f"{month:02d}", "day": f"{day:02d}"}

            filtered_data = [item for item in final_query_result if item]
            
            print(filtered_data)
            

            for sublist in filtered_data:
                for row in sublist:
                    id, admission_no, month_year, date, status_att, subject_query = row
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
            
        except Exception as e:
            print(e)
            return Response({'error':f'error occured {e}'}, status=status.HTTP_400_BAD_REQUEST)