from rest_framework import serializers
from .models import Student, className, division, subjects, batchYear

class StudentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Student
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