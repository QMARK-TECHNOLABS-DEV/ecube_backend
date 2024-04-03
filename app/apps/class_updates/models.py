from django.db import models

class class_updates_link(models.Model):
    class_name = models.CharField(max_length=100)
    batch_year = models.CharField(max_length=4)
    division = models.CharField(max_length=1)
    link = models.CharField(max_length=100,null=True, blank=True)
    topic = models.CharField(max_length=100,null=True, blank=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    
class announcements(models.Model):
    announcement = models.CharField(max_length=100)
    upload_date = models.CharField(max_length=10)
    upload_time = models.DateTimeField(auto_now_add=True)
    
class recordings(models.Model):
    class_name = models.CharField(max_length=100)
    batch_year = models.CharField(max_length=4)
    division = models.CharField(max_length=1)
    subject = models.CharField(max_length=100)
    date = models.CharField(max_length=10, default="", null=True, blank=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    recording_link = models.TextField(null=True, blank=True)
    video_id = models.CharField(max_length=100, null=True, blank=True)
    

