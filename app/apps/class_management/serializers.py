from rest_framework import serializers
from ..register_student.models import class_details

class CombinedField(serializers.Field):
    def to_representation(self, obj):
        return f"{obj.class_name} {obj.division}"

class ClassDetailsSerializer(serializers.ModelSerializer):
    combined_field = CombinedField(source='*')

    class Meta:
        model = class_details
        fields = ('combined_field',)