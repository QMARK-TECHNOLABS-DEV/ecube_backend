from rest_framework.views import APIView
from register_student.models import Student
from register_student.serializers import StudentDisplaySerializer
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