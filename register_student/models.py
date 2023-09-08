from django.db import models


class Student(models.Model):

    name = models.TextField()
    admission_no = models.CharField()
    phone_no = models.CharField(max_length=10,primary_key=False)
    batch_year = models.TextField(null=False, blank=False,default=0)
    class_name = models.CharField()
    division = models.CharField(max_length=1)
    subjects = models.TextField()
    school_name = models.TextField()
    
class className(models.Model):
    class_name = models.CharField(max_length=10)

class division(models.Model):
    division_name = models.CharField(max_length=1)
    
class subjects(models.Model):
    subjects_name = models.CharField(max_length=10)
    
class batchYear(models.Model):
    batch_year = models.TextField(null=False, blank=False,default=0)
