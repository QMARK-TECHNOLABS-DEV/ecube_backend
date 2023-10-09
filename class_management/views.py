from rest_framework.views import APIView
from register_student.models import Student, class_details
from register_student.serializers import StudentDisplaySerializer
from .serializers import ClassDetailsSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q


# Create your views here.
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

        serializer = StudentDisplaySerializer(students, many=True)
        
        if not serializer.data:
            return Response({'Message': 'No students found'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'all_students': serializer.data}, status=status.HTTP_200_OK)
    
    
class AllClassesView(APIView):
    def get(self, request):
        try:
            batch_year = request.data.get('batch_year')  # Use query_params for GET requests
            
            if not batch_year:
                unique_batch_years = class_details.objects.values_list('batch_year', flat=True).distinct().order_by('-batch_year')
                
                if not unique_batch_years:
                    return Response({'Message': 'No classes found'}, status=status.HTTP_400_BAD_REQUEST)
                
                batch_year = unique_batch_years[0]
            
            
            if batch_year:
                classes_instances = class_details.objects.filter(batch_year=batch_year)
                
                if not classes_instances:
                    return Response({'Message': 'No classes found'}, status=status.HTTP_400_BAD_REQUEST)
        
                serializer = ClassDetailsSerializer(classes_instances, many=True)
                
                return Response({'all_classes': serializer.data}, status=status.HTTP_200_OK)
            
            else:
                return Response({'Message': 'Batch year not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e)
            return Response({'Message': 'Error in fetching classes'}, status=status.HTTP_400_BAD_REQUEST)

class AllBatchYear(APIView):
    def get(self, request):
        try:
            batch_year = class_details.objects.values_list('batch_year', flat=True).distinct().order_by('-batch_year')
            
            if not batch_year:
                return Response({'Message': 'No classes found'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'batch_year': batch_year}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({'Message': 'Error in fetching classes'}, status=status.HTTP_400_BAD_REQUEST)

class AllClassName(APIView):
    def get(self, request):
        try:
            class_name = class_details.objects.values_list('class_name', flat=True).distinct().order_by('-class_name')
            
            if not class_name:
                return Response({'Message': 'No classes found'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'class_name': class_name}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({'Message': 'Error in fetching classes'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class AllDivision(APIView):
    def get(self, request):
        try:
            division = class_details.objects.values_list('division', flat=True).distinct().order_by('-division')
            
            if not division:
                return Response({'Message': 'No classes found'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'division': division}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({'Message': 'Error in fetching classes'}, status=status.HTTP_400_BAD_REQUEST)
