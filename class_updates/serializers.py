from rest_framework.serializers import ModelSerializer
from .models import class_updates_link, announcements, recordings

class class_updates_link_serializer(ModelSerializer):
    class Meta:
        model = class_updates_link
        fields = ('id','class_name', 'batch_year', 'division', 'subject', 'link', 'topic','class_time', 'date','upload_time')
        
class class_updates_link_get_serializer(ModelSerializer):
    class Meta:
        model = class_updates_link
        fields = ('subject', 'link', 'topic','class_time')
        
class announcement_serializer(ModelSerializer):
    class Meta:
        model = announcements
        fields = ('id','announcement', 'upload_date', 'upload_time')
        
class recordings_get_serializer(ModelSerializer):
    class Meta:
        model = recordings
        fields = ('subject','recording_link')
        
class recording_serializer(ModelSerializer):
    class Meta:
        model = recordings
        fields = ('id','class_name', 'batch_year', 'division', 'subject', 'date', 'recording_link')