from rest_framework import serializers
from .models import Student, class_details

class StudentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Student
        fields = ['id','name', 'admission_no','phone_no', 'school_name','class_name', 'division','class_group','batch_year', 'subjects', 'email_id']      


class StudentDisplaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Student
        fields = ['name', 'admission_no','phone_no', 'school_name', 'subjects', 'email_id']      

class ClassDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = class_details
        fields = '__all__'
        
