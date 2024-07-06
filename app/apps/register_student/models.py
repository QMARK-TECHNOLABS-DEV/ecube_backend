from django.db import models, connection
from django.apps import apps
from django.contrib.contenttypes.models import ContentType


class class_details(models.Model):
    class_name = models.CharField(max_length=10)
    division = models.CharField(max_length=1)
    subjects = models.TextField(default='')
    batch_year = models.TextField(null=False, blank=False,default=0)
    exam_result = models.DateTimeField(null=True,blank=True)
    exam_name = models.TextField(blank=True,null=True)
    exam_subject = models.TextField(blank=True,null=True)
    attendance = models.DateTimeField(null=True,blank=True)
    attendance_date = models.TextField(blank=True,null=True)
    daily_class = models.DateTimeField(null=True,blank=True)
    daily_class_date = models.TextField(blank=True,null=True)

class Student(models.Model):
    name = models.TextField()
    admission_no = models.CharField(max_length=20, unique=True)
    phone_no = models.CharField(max_length=15, unique=True)
    batch_year = models.TextField(null=False, blank=False, default=0)
    class_name = models.CharField(max_length=10)
    division = models.CharField(max_length=1)
    subjects = models.TextField()
    class_group = models.TextField(null=False, blank=False, default='')
    school_name = models.TextField()
    device_id = models.TextField(default='')
    restricted = models.BooleanField(default=False)
    email_id = models.EmailField(max_length=254, unique=True, null=True, blank=True)


class ExamResults(models.Model):
    admission_no = models.CharField(max_length=20)  # Specify the max_length
    exam_name = models.CharField(max_length=100)     # Specify the max_length
    physics = models.DecimalField(null=True, blank=True,decimal_places=2,max_digits=5)
    chemistry = models.DecimalField(null=True, blank=True,decimal_places=2,max_digits=5)
    maths = models.DecimalField(null=True, blank=True,decimal_places=2,max_digits=5)
    physics_status = models.CharField(max_length=20,null=True, blank=True)
    chemistry_status = models.CharField(max_length=20,null=True, blank=True)
    maths_status = models.CharField(max_length=20,null=True, blank=True)
    
    
class LeaderBoard(models.Model):    
    admission_no = models.CharField(max_length=20)  
    physics = models.DecimalField(null=True, blank=True,decimal_places=2,max_digits=5)
    chemistry = models.DecimalField(null=True, blank=True,decimal_places=2,max_digits=5)
    maths = models.DecimalField(null=True, blank=True,decimal_places=2,max_digits=5)
    
class Attendance(models.Model):
    admission_no = models.CharField(max_length=20)
    month_year_number = models.CharField(max_length=20) 
    date = models.CharField(max_length=20) 
    status = models.CharField(max_length=20)
    subject = models.CharField(max_length=20,default='')

class DailyUpdates(models.Model):
    admission_no = models.CharField(max_length=20)
    date = models.CharField(max_length=20)
    on_time = models.BooleanField(default=True)
    voice = models.BooleanField(default=True)
    nb_sub = models.BooleanField(default=True)
    mob_net = models.BooleanField(default=True)
    camera = models.BooleanField(default=True)
    full_class = models.BooleanField(default=True)
    activities = models.CharField(null=True, blank=True, max_length=100)
    engagement = models.BooleanField(default=True)
    overall_performance_percentage = models.FloatField(null=True, blank=True)
    overall_performance = models.CharField(null=True, blank=True, max_length=100)
    remarks = models.TextField(null=True, blank=True)
    
    
    class Meta:

        unique_together = ['admission_no', 'date']
    
    
def create_dynamic_models(model_names):
    try:
        base_models = [ExamResults, LeaderBoard, Attendance, DailyUpdates]

        for base_model, new_model_name in zip(base_models, model_names):
            # Check if the new model name is a valid identifier
            if not new_model_name.isidentifier():
                print(f"Invalid model name: {new_model_name}")
                continue
            
            print(base_model)
            app_label = base_model._meta.app_label
            
            print(app_label)
            # Create a dictionary of field names and their corresponding field objects
            fields = {
                field.name: field.clone() for field in base_model._meta.fields
            }

            fields['__module__'] = 'apps.register_student.models'

            # Create the dynamic model class
            dynamic_model = type(new_model_name, (models.Model,), fields)

            # Create the database table for the dynamic model
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(dynamic_model)
    except Exception as e:
        print(e)
        


def create_tables(app_name,unique_table_names):
    print(app_name)
    model_names = [app_name + unique_table_names+'_examresults', app_name+unique_table_names+'_leaderboard', app_name+unique_table_names+'_attendance',app_name + unique_table_names+'_dailyupdates']
    create_dynamic_models(model_names)
    
