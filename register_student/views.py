from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Student, className, division, subjects, batchYear, table_names, create_tables
from .serializers import StudentSerializer, classNameSerializer, divisionSerializer, subjectsSerializer, batchYearSerializer, table_namesSerializer
import pandas as pd

class StudentMethods(APIView):
    def post(self, request):
        serializer = StudentSerializer(data=request.data)
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
    

class StudentBulkMethods(APIView):
    
    def post(self, request, format=None):
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
            
            data['class_name']= data['class_name'].str.replace(' ', '').str.lower()
            data['division']= data['division'].str.replace(' ', '').str.lower()
            
                    # Group the data by the specified columns and iterate through unique combinations
            unique_combinations = data.groupby(['batch_year', 'class_name', 'division']).size().reset_index()

            for _, row in unique_combinations.iterrows():
                batch_year = row['batch_year']
                class_name = row['class_name']
                division_name = row['division']
                
                table_name = f"{batch_year}_{class_name}_{division_name}"
                
                result_table_name = table_names.objects.filter(table_name=table_name)
                
                if not result_table_name:
                    table_serializer = table_namesSerializer(data={'table_name':table_name})
                    
                    class_serializer = classNameSerializer(data={'class_name':class_name})
                    
                    division_serializer = divisionSerializer(data={'division_name':division_name})
                    
                    batch_year_serializer = batchYearSerializer(data={'batch_year':batch_year})
                    
                    
        
                    if class_serializer.is_valid():
                        
                        if className.objects.filter(class_name=class_name).exists():
                            pass
                        else:
                            class_serializer.save()
                            
                        
                    if division_serializer.is_valid():
                            
                        if division.objects.filter(division_name=division_name).exists():
                            pass
                        else:
                            division_serializer.save()
                           
                        
                    if batch_year_serializer.is_valid():
                        
                        if batchYear.objects.filter(batch_year=batch_year).exists():
                            pass
                        else:
                            batch_year_serializer.save()
                            
                        
                    
                    if table_serializer.is_valid():
                        
                        table_serializer.save()
                        app_name = 'register_student_'
                        create_tables(app_name,table_name)
            
                    else:
                        return Response({'message': 'Table name not saved'}, status=status.HTTP_400_BAD_REQUEST)
                    
            serializer = StudentSerializer(data=data.to_dict(orient='records'), many=True)

            if serializer.is_valid():
                # Save the data to the database
                serializer.save()

                # Delete or remove the uploaded file
                file_obj.close()  # Close the file before deleting
                #file_obj.delete()  # Delete the file from the server

                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        return Response({'message': 'Invalid file format or data'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        
        if serializer.data == []:
            return Response({'Message': 'No records found'} ,status=status.HTTP_400_BAD_REQUEST)
        
        
        return Response({'all_users':serializer.data}, status=status.HTTP_200_OK)
    
class classMethods(APIView):
    
    def post(self,request):
        serializer = classNameSerializer(data=request.data)
        
        if serializer.is_valid():
            
            if className.objects.filter(class_name=request.data['class_name']).exists():
                return Response({'Message': 'Class already exists'} ,status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
    def get(self,request):
        classes = className.objects.all()
        
        serializer = classNameSerializer(classes,many=True)
        
        if serializer.data == []:
            return Response({'Message': 'No classes defined'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'all_classes':serializer.data}, status=status.HTTP_200_OK)
        
    def delete(self,request):
        
        classes = className.objects.filter(class_name=request.data['class_name'])
        
        if classes.exists():
            classes.delete()
            return Response({'Message': 'Classes successfully deleted'} ,status=status.HTTP_200_OK)
        
        return Response({'Message': 'Record does not  exist'},status=status.HTTP_400_BAD_REQUEST)
    
class divisionMethods(APIView):
    def post(self,request):
        serializer = divisionSerializer(data=request.data)
        
        if serializer.is_valid():
            
            if division.objects.filter(division_name=request.data['division_name']).exists():
                print('bad request detected')
                return Response({'Message': 'Division already exists'} ,status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
    def get(self,request):
        divisions = division.objects.all()
        
        serializer = divisionSerializer(divisions,many=True)
        
        if serializer.data == []:
            return Response({'Message': 'No divisions defined'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'all_divisions':serializer.data}, status=status.HTTP_200_OK)
    
    def delete(self,request):
            
            divisions = division.objects.filter(division_name=request.data['division_name'])
            
            if divisions.exists():
                divisions.delete()
                return Response({'Message': 'Division successfully deleted'} ,status=status.HTTP_200_OK)
            
            return Response({'Message': 'Record does not  exist'},status=status.HTTP_400_BAD_REQUEST)
        

class subjectMethods(APIView):
    def post(self,request):
        serializer = subjectsSerializer(data=request.data)
        
        if serializer.is_valid():
            
            if subjects.objects.filter(subjects_name=request.data['subjects_name']).exists():
                return Response({'Message': 'Subject already exists'} ,status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
    def get(self,request):
        subjects_ = subjects.objects.all()
        
        serializer = subjectsSerializer(subjects_,many=True)
        
        if serializer.data == []:
            return Response({'Message': 'No subjects defined'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'all_subjects':serializer.data}, status=status.HTTP_200_OK)
    
    def delete(self,request):
                
        subjects_ = subjects.objects.filter(subjects_name=request.data['subjects_name'])
        
        if subjects_.exists():
            subjects_.delete()
            return Response({'Message': 'Subject successfully deleted'} ,status=status.HTTP_200_OK)
        
        return Response({'Message': 'Record does not  exist'},status=status.HTTP_400_BAD_REQUEST)
    
    
class batchYearMethods(APIView):
    def post(self,request):
        serializer = batchYearSerializer(data=request.data)
        
        if serializer.is_valid():
            
            if batchYear.objects.filter(batch_year=request.data['batch_year']).exists():
                return Response({'Message': 'Batch year already exists'} ,status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        batch_years = batchYear.objects.all()
        
        serializer = batchYearSerializer(batch_years,many=True)
        
        if serializer.data == []:
            return Response({'Message': 'No batch years defined'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'all_batch_years':serializer.data}, status=status.HTTP_200_OK)
    
    
    def delete(self,request):
                        
        batch_years = batchYear.objects.filter(batch_year=request.data['batch_year'])
        
        if batch_years.exists():
            batch_years.delete()
            return Response({'Message': 'Batch year successfully deleted'} ,status=status.HTTP_200_OK)
        
        return Response({'Message': 'Record does not  exist'},status=status.HTTP_400_BAD_REQUEST)
    
    
class StudentFilterGetMethods(APIView):    
    def get(self, request):
        class_name = request.data.get('class_name')
        division = request.data.get('division')
        batch_year = request.data.get('batch_year')
        subject = request.data.get('subject')

        students = Student.objects.all()

        if class_name:
            students = students.filter(class_name=class_name)
        
        if division:
            students = students.filter(division=division)
        
        if batch_year:
            students = students.filter(batch_year=batch_year)
        
        if subject:
            # Use the Q object to filter for students with the desired subject
            students = students.filter(Q(subjects__contains=subject))

        serializer = StudentSerializer(students, many=True)
        
        if not serializer.data:
            return Response({'Message': 'No students found'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'all_students': serializer.data}, status=status.HTTP_200_OK)
