from rest_framework.serializers import ModelSerializer
from .models import class_updates_link

class class_updates_link_serializer(ModelSerializer):
    class Meta:
        model = class_updates_link
        fields = ('id','class_name', 'batch_year', 'division', 'subject', 'link', 'topic')
        
class class_updates_link_get_serializer(ModelSerializer):
    class Meta:
        model = class_updates_link
        fields = ('id','class_name', 'batch_year', 'division', 'subject', 'link', 'topic', 'date')