from django.db import models

class class_updates_link(models.Model):
    class_name = models.CharField(max_length=100)
    batch_year = models.CharField(max_length=4)
    division = models.CharField(max_length=1)
    subject = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    topic = models.CharField(max_length=100)
    class_time = models.CharField(max_length=10, default="")
    date = models.CharField(max_length=10)
    upload_time = models.DateTimeField(auto_now_add=True)