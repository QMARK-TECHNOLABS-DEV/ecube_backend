from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Student, create_tables, class_details
from .serializers import ClassDetailsSerializer, StudentSerializer, ExamStudentDisplaySerializer, StudentDisplaySerializer
import pandas as pd
from django.db import connection, DatabaseError
from client_auth.utils import TokenUtil
from client_auth.models import Token
from class_updates.models import class_updates_link
class StudentMethods(APIView):
    def post(self, request):
        
        batch_year = request.query_params.get('batch_year')
        class_name = request.query_params.get('class_name')
        division = request.query_params.get('division')
        subjects = request.query_params.get('subjects')
        
        class_instance = class_details.objects.filter(batch_year=batch_year,class_name=class_name,division=division)
        
        print(class_instance)
        
        if not class_instance:
            return Response({'message': 'No such class group'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        
        data['batch_year'] = batch_year
        data['class_name'] = class_name
        data['division'] = division
        data['subjects'] = subjects
        data['class_group'] = class_instance[0].id
        
        
        serializer = StudentSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        students = Student.objects.filter(id=request.data['id'])
        serializer = StudentSerializer(students, many=True)
        
        if serializer.data == []:
            return Response({'Message': 'The record or student does not exist'} ,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data[0], status=status.HTTP_200_OK)
    
    def delete(self, request):
        student = Student.objects.filter(id=request.data['id'])
        
        if student.exists():
            student.delete()
            return Response({'Message': 'Record successfully deleted'} ,status=status.HTTP_200_OK)
        
        return Response({'Message': 'Record does not  exist'},status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        students = Student.objects.filter(id=request.GET.get('id'))
        
        if students.exists():
            students.update(**request.data)
            return Response({'Message': 'Record successfully updated'} ,status=status.HTTP_200_OK)
      
        return Response({'Message': 'Record does not  exist'},status=status.HTTP_400_BAD_REQUEST)
    

class ClassMethods(APIView):
    def post(self, request):
        try:
            data = request.data
            
            # Convert data values to uppercase
            for key in data:
                if isinstance(data[key], str):
                    data[key] = data[key].upper()
            
            serializer = ClassDetailsSerializer(data=data)
            
            if serializer.is_valid():
                if class_details.objects.filter(class_name=data['class_name'], division=data['division'], batch_year=data['batch_year']).exists():
                    return Response({'Message': 'Class already exists'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    
                    table_name = f"{data['batch_year']}_{data['class_name']}_{data['division']}".replace(" ","").lower()
             
                    if table_name:
                        
                        app_name = 'register_student_'
                        create_tables(app_name,table_name)
                        
                        serializer.save()
                        
                        for subject in ['PHYSICS', 'CHEMISTRY', 'MATHS']:
                            class_updates_link.objects.create(class_name=data['class_name'], batch_year=data['batch_year'], division=data['division'], subject=subject)
                            
        
                        return Response({"message": "Successfully created class group and associated feature group"}, status=status.HTTP_201_CREATED)
            
                 
                    return Response({"message": "Table names not valid"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Serializer not valid"},status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "Internal failure"},status=status.HTTP_400_BAD_REQUEST)
        
        
    def put(self, request):
        try:
            class_id = request.data.get('id')  # Use request.data instead of request.POST
            
            class_instance = class_details.objects.filter(id=class_id).first()
            
            if class_instance:
                
                app_name = 'register_student_'
                    
                table_name = f"{app_name}{app_name}{class_instance.batch_year}_{class_instance.class_name}_{class_instance.division}".replace(" ","").lower()
                    
                feature_group_id = ['_examresults', '_leaderboard', '_attendance', '_dailyupdates']
                
                data = request.data
                
                new_table_name = f"{app_name}{app_name}{data['batch_year']}_{data['class_name']}_{data['division']}".replace(" ","").lower()
            # Convert data values to uppercase
                for key in data:
                    if isinstance(data[key], str):
                        data[key] = data[key].upper()
                        
                if class_details.objects.filter(class_name=data['class_name'], division=data['division'], batch_year=data['batch_year']).exists():
                    return Response({'Message': 'Class already exists'}, status=status.HTTP_400_BAD_REQUEST)
                        
                serializer = ClassDetailsSerializer(class_instance, data=data)
                
                if serializer.is_valid():

                    
                    serializer.save()
                    
                    cursor = connection.cursor()
                    
                    for row in feature_group_id:
                        try:
                            cursor = connection.cursor()
                            cursor.execute(f"ALTER TABLE {table_name+row} RENAME TO {new_table_name+row}")
                            print(f'Table {table_name+row} deleted')
                            
                        except DatabaseError as e:
                            print(f'Error deleting table {table_name+row}: {str(e)}')  
                    
                
                                 
                    
                    return Response({"message": "Class updated successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Class does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:  # Catch specific exceptions for debugging
            return Response({"message": "Internal failure", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    def get(self, request):
        
        try: 
            class_id = request.data.get('id')
            
            if class_id:
                class_instance = class_details.objects.filter(id=class_id).first()
                
                if class_instance:
                    serializer = ClassDetailsSerializer(class_instance)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Class does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                classes = class_details.objects.all()
                serializer = ClassDetailsSerializer(classes, many=True)
                
                return Response({"class_details": serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Internal failure"}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
            class_id = request.query_params.get('id')
            if not class_id:
                return Response({"message": "Class ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

            class_instance = class_details.objects.filter(id=class_id).first()
            if not class_instance:
                return Response({"message": "Class group does not exist"}, status=status.HTTP_400_BAD_REQUEST)

            app_name = 'register_student_'
            table_name = f"{class_instance.batch_year}_{class_instance.class_name}_{class_instance.division}".replace(" ", "").lower()
            feature_group_id = ['_examresults', '_leaderboard', '_attendance', '_dailyupdates']

            try:
                with connection.cursor() as cursor:
                    for row in feature_group_id:
                        table_name_to_check = f"{app_name}{app_name}{table_name}{row}"

                        cursor.execute(f"DROP TABLE public.{table_name_to_check}")
                        print(f'Table {table_name_to_check} deleted')


                class_instance.delete()
                print(f'Class group {class_instance} deleted')

                return Response({"message": "Class group deleted successfully"}, status=status.HTTP_200_OK)

            except DatabaseError as e:
                return Response({"message": f"Error deleting tables: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DeviceIdMethods(APIView):
    def put(self, request):
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
                return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate a new access token
            
            device_id = request.data['device_id']
                
            student_instance = Student.objects.filter(id=user_id).first()
                
            if student_instance:
                student_instance.device_id = device_id
                student_instance.save()
                    
                return Response({"message": "Device ID updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Student does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:  # Catch specific exceptions for debugging
            return Response({"message": "Internal failure", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StudentBulkMethods(APIView):
    
    def post(self, request, format=None):
        
        try:
            file_obj = request.FILES['doc_file']

            if file_obj:
                # Process the uploaded file (CSV or XLSX)
                if file_obj.name.endswith('.csv'):
                    # Process CSV file
                    data = pd.read_csv(file_obj)
                elif file_obj.name.endswith('.xlsx'):
                    # Process XLSX file
                    data = pd.read_excel(file_obj)
                else:
                    return Response({'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
                
                batch_year = request.POST.get('batch_year')
                class_name = request.POST.get('class_name')
                division = request.POST.get('division')
                subjects = request.POST.get('subjects')
                
                class_instance = class_details.objects.filter(batch_year=batch_year,class_name=class_name,division=division)
                
                if not class_instance:
                    return Response({'message': 'No such class group'}, status=status.HTTP_400_BAD_REQUEST)
                
                data['batch_year'] = batch_year
                data['class_name'] = class_name
                data['division'] = division
                data['subjects'] = subjects
                data['class_group'] = class_instance[0].id

                serializer = StudentSerializer(data=data.to_dict(orient='records'), many=True)

                if serializer.is_valid():
                    # Save the data to the database
                    serializer.save()

                    file_obj.close()  
                
                    return Response({"message": "Successfully added users to class group"}, status=status.HTTP_201_CREATED)
                    
            return Response({'message': 'Invalid file format or data'}, status=status.HTTP_400_BAD_REQUEST)
        
        except:
            return Response({'message': 'Internal failure'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            batch_year = request.query_params.get('batch_year')
            class_name = request.query_params.get('class_name')
            division = request.query_params.get('division')
            
            students = Student.objects.filter(batch_year=batch_year,class_name=class_name,division=division)
            serializer = StudentDisplaySerializer(students, many=True)
            
            if serializer.data == []:
                return Response({'Message': 'No records found'} ,status=status.HTTP_400_BAD_REQUEST)
            
            
            return Response({'all_users':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Message': 'Internal failure', 'error': str(e)} ,status=status.HTTP_400_BAD_REQUEST)
 
class GetAllStudents(APIView):
     def get(self, request):
        try:
            students = Student.objects.all()
            serializer = StudentSerializer(students, many=True)
            
            if serializer.data == []:
                return Response({'Message': 'No records found'} ,status=status.HTTP_400_BAD_REQUEST)
            
            
            return Response({'all_users':serializer.data}, status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({'Message': 'Internal failure', 'error': str(e)} ,status=status.HTTP_400_BAD_REQUEST) 
    
class ExamStudentDisplay(APIView):
    def get(self, request):
        try:
            batch_year = request.query_params.get('batch_year')
            class_name = request.query_params.get('class_name')
            division = request.query_params.get('division')
            
            students = Student.objects.filter(batch_year=batch_year,class_name=class_name,division=division)
            serializer = ExamStudentDisplaySerializer(students, many=True)
            
            if serializer.data == []:
                return Response({'Message': 'No records found'} ,status=status.HTTP_400_BAD_REQUEST)
            
            
            return Response({'all_users':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Message': 'Internal failure', 'error': str(e)} ,status=status.HTTP_400_BAD_REQUEST)