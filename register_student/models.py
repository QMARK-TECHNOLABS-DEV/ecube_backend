from django.db import models, connection
from django.apps import apps
from django.contrib.contenttypes.models import ContentType


class class_details(models.Model):
    class_name = models.CharField(max_length=10)
    division = models.CharField(max_length=1)
    subjects = models.TextField(default='')
    batch_year = models.TextField(null=False, blank=False,default=0)
class Student(models.Model):

    name = models.TextField()
    admission_no = models.CharField()
    phone_no = models.CharField(max_length=10,primary_key=False)
    batch_year = models.TextField(null=False, blank=False,default=0)
    class_name = models.CharField(max_length=10)
    division = models.CharField(max_length=1)
    subjects = models.TextField()
    class_group = models.ForeignKey(class_details, on_delete=models.CASCADE, null=True, blank=True)
    school_name = models.TextField()
    email_id = models.TextField(default='')
    logged_in = models.BooleanField(default=False)

class ExamResults(models.Model):
    admission_no = models.CharField(max_length=20)  # Specify the max_length
    exam_name = models.CharField(max_length=100)     # Specify the max_length
    physics = models.IntegerField(null=True, blank=True)
    chemistry = models.IntegerField(null=True, blank=True)
    maths = models.IntegerField(null=True, blank=True)
    
    
class LeaderBoard(models.Model):    
    admission_no = models.CharField()
    physics = models.IntegerField(null=True, blank=True)
    chemistry = models.IntegerField(null=True, blank=True)
    maths = models.IntegerField(null=True, blank=True)
    
class Attendance(models.Model):
    admission_no = models.CharField()
    month_year_number = models.CharField() # 8/2021
    date = models.CharField()
    status = models.CharField()

class DailyUpdates(models.Model):
    admission_no = models.CharField()
    date = models.CharField()
    on_time = models.BooleanField(default=True)
    voice = models.BooleanField(default=True)
    nb_sub = models.BooleanField(default=True)
    mob_net = models.BooleanField(default=True)
    camera = models.BooleanField(default=True)
    full_class = models.BooleanField(default=True)
    activities = models.CharField(null=True, blank=True)
    engagement = models.BooleanField(default=True)
    overall_performance_percentage = models.FloatField(null=True, blank=True)
    overall_performance = models.CharField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    
    
def create_dynamic_models(model_names):
    base_models = [ExamResults, LeaderBoard, Attendance, DailyUpdates]

    for base_model, new_model_name in zip(base_models, model_names):
        # Check if the new model name is a valid identifier
        if not new_model_name.isidentifier():
            print(f"Invalid model name: {new_model_name}")
            continue

        app_label = base_model._meta.app_label

        # Create a dictionary of field names and their corresponding field objects
        fields = {
            field.name: field.clone() for field in base_model._meta.fields
        }

        fields['__module__'] = app_label

        # Create the dynamic model class
        dynamic_model = type(new_model_name, (models.Model,), fields)

        # Create the database table for the dynamic model
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(dynamic_model)


def create_tables(app_name,unique_table_names):
    model_names = [app_name + unique_table_names+'_examResults', app_name+unique_table_names+'_leaderBoard', app_name+unique_table_names+'_attendance',app_name + unique_table_names+'_dailyUpdates']
    create_dynamic_models(model_names)
    
