from rest_framework import serializers
from .models import Student, className, division, subjects, batchYear, table_names, class_details

class StudentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Student
        fields = ['name', 'admission_no','phone_no', 'school_name','class_name', 'division','class_group','batch_year', 'subjects', 'email_id']      


class StudentDisplaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Student
        fields = ['name', 'admission_no','phone_no', 'school_name', 'subjects', 'email_id']      

class ClassDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = class_details
        fields = '__all__'
        
class table_namesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = table_names
        fields = '__all__'
class classNameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = className
        fields = '__all__'          
        
class divisionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = division
        fields = '__all__'
        
class subjectsSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = subjects
        fields = '__all__'
            
class batchYearSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = batchYear
        fields = '__all__'