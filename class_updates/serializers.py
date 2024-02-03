from rest_framework.serializers import ModelSerializer
from .models import class_updates_link, announcements, recordings

class class_updates_link_serializer(ModelSerializer):
    class Meta:
        model = class_updates_link
        fields = ('id','class_name', 'batch_year', 'division', 'link', 'topic','upload_time')
        
class class_updates_link_get_serializer(ModelSerializer):
    class Meta:
        model = class_updates_link
        fields = ('link', 'topic')
        
class announcement_serializer(ModelSerializer):
    class Meta:
        model = announcements
        fields = ('id','announcement', 'upload_date', 'upload_time')
        
class recordings_get_serializer(ModelSerializer):
    class Meta:
        model = recordings
        fields = ['subject','recording_link','video_id']
        
class recording_serializer(ModelSerializer):
    class Meta:
        model = recordings
        fields = ('id','class_name', 'batch_year', 'division', 'subject', 'date', 'recording_link','video_id')