from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from register_student.models import Student
from client_auth.utils import TokenUtil
from client_auth.models import Token
import pandas as pd

def split_date(date_str):
    # Split the date string into parts
    parts = date_str.split(":")[1].split("/")

    # Ensure the year, month, and day are in the desired format
    year = f"20{parts[2]:02}"
    month = parts[1].zfill(2)
    day = parts[0].zfill(2)

    # return {
    #     "year": year,
    #     "month": month,
    #     "day": day
    # }
    return f"{day}/{month}/{year}"

    

class AddDailyUpdatesBulk(APIView):
    def post(self, request):
        
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

        file_obj = request.FILES['media_file']

        if file_obj:
            # Process the uploaded file (CSV or XLSX)
            if file_obj.name.endswith('.csv'):
                # Process CSV file
                df = pd.read_csv(file_obj)
            elif file_obj.name.endswith('.xlsx'):
                # Process XLSX file
                df = pd.read_excel(file_obj)
            else:
                return Response({'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
            
        data_dict = {
            "students": []
        }
        
        activity_code = {
            "O": "Contact Institution",
            "N": "Student have not answered in the QnA session"
        }
        # Extract the date from the first cell in the Excel sheet
        raw_date = df.columns[0]
        date_variable = split_date(raw_date)
        
        max_count_of_y = -1
        # Iterate through rows (excluding the header) and count "Y" values
        for index, row in df.iterrows():
            adm_no = row[0]  # Assuming the first column contains student names
            if pd.notna(adm_no) and adm_no != "AD NO":
                    
                student_data = {
                    "admission_no": adm_no,
                    "date": date_variable,
                    "on_time": True,
                    "voice": False if row[2] == "M" else True,
                    "nb_sub": False if row[2] == "B" else True,
                    "mob_net": False if row[2] == "R" else True,
                    "camera": False if row[2] == "V" else True,
                    "full_class": True,
                    "activities": sum(1 for val in row[3:] if val == "Y"),
                    "engagement": False if row[2] == "L" else True,
                    "remarks": activity_code[row[2]] if row[2] == "O" or row[2] == "N" else ""     
                }
                
                
                count_of_y = student_data["activities"]
                
                if count_of_y > max_count_of_y:
                    max_count_of_y = count_of_y
                    
                    
                data_dict["students"].append(student_data)
                
        app_name = 'register_student'
        
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_dailyupdates"
        
        cursor = connection.cursor()
        
        try: 
            
            for student in data_dict["students"]:
                student["overall_performance_percentage"] = int((int(student["activities"]) / int(max_count_of_y))* 50) + 25 if student['nb_sub'] else 0 + 25 if student['engagement'] else 0
                student["activities"] =  f"{student['activities']}/{max_count_of_y}"
                student["overall_performance"] = "EXCELLENT" if student["overall_performance_percentage"] >= 85 else "GOOD" if student["overall_performance_percentage"] >= 50 else "AVERAGE" if student["overall_performance_percentage"] > 25 else "POOR"
                
                print("Before insert")
                cursor.execute(f"INSERT INTO public.{table_name} (admission_no, date, on_time, voice, nb_sub, mob_net, camera, full_class, activities, engagement, overall_performance_percentage, overall_performance, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [str(student['admission_no']), student['date'], student['on_time'], student['voice'], student['nb_sub'], student['mob_net'], student['camera'], student['full_class'], student['activities'], student['engagement'], student['overall_performance_percentage'], student['overall_performance'], student['remarks']])
                print("After insert")
            return Response({'message': 'Data saved successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here
            print(f"Error: {str(e)}")
            return Response({'message': 'Failed to save data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class GetDates(APIView):
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
    
        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "").lower()
        division = str(division).replace(" ", "").lower()

        app_name = 'register_student'
        
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_dailyupdates"
        
        try:
            cursor = connection.cursor()
            
            cursor.execute(f"SELECT DISTINCT date, TO_DATE(date, 'DD/MM/YYYY') AS parsed_date FROM public.{table_name} ORDER BY parsed_date DESC")

            dates = cursor.fetchall()
            
        except Exception as e:
            # Handle exceptions here
            print(f"Error: {str(e)}")
            return Response({'message': 'Failed to save data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        dates_list = []
        
        for date in dates:
            dates_list.append(date[0])
            
        return Response({'dates': dates_list}, status=status.HTTP_200_OK)
    
    
class GetDailyUpdate(APIView):
    def get(self,request):
        date = request.GET.get('date')
        
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
    
        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "").lower()
        division = str(division).replace(" ", "").lower()

        app_name = 'register_student'
        
        table_name = app_name + '_' + app_name + '_' + batch_year + "_" + class_name + "_" + division + "_dailyupdates"
        
        cursor = connection.cursor()
        
        cursor.execute(f"SELECT * FROM public.{table_name} WHERE date = %s AND admission_no = %s", [date, user.admission_no])
        
        
        query_result = cursor.fetchall()
        
        
        cursor.close()
        
        daily_updates = []
        
        for row in query_result:
            daily_update = {
                "admission_no": row[1],
                "date": row[2],
                "on_time": row[3],
                "voice": row[4],
                "nb_sub": row[5],
                "mob_net": row[6],
                "camera": row[7],
                "full_class": row[8],
                "activities": row[9],
                "engagement": row[10],
                "overall_performance_percentage": row[11],
                "overall_performance": row[12],
                "remarks": row[13]
            }
            
            daily_updates.append(daily_update)
            
        return Response({'daily_updates': daily_updates}, status=status.HTTP_200_OK)
        