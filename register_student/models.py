from django.db import models, migrations
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

class Student(models.Model):

    name = models.TextField()
    admission_no = models.CharField()
    phone_no = models.CharField(max_length=10,primary_key=False)
    batch_year = models.TextField(null=False, blank=False,default=0)
    class_name = models.CharField()
    division = models.CharField(max_length=1)
    subjects = models.TextField()
    school_name = models.TextField()

class ExamResults(models.Model):
    admission_no = models.CharField(max_length=20)  # Specify the max_length
    exam_name = models.CharField(max_length=100)     # Specify the max_length
    physics = models.IntegerField()
    chemistry = models.IntegerField()
    maths = models.IntegerField()
    
    
class LeaderBoard(models.Model):    
    admission_no = models.CharField()
    physics = models.IntegerField()
    chemistry = models.IntegerField()
    maths = models.IntegerField()
    
class Attendance(models.Model):
    admission_no = models.CharField()
    month_year_number = models.CharField() # 8/2021
    date = models.DateField()
    status = models.CharField()

class DailyUpdates(models.Model):
    admission_no = models.CharField()
    date = models.DateField()
    on_time = models.BooleanField()
    voice = models.BooleanField()
    nb_sub = models.BooleanField()
    mob_net = models.BooleanField()
    camera = models.BooleanField()
    full_class = models.BooleanField()
    activites = models.CharField()
    engagement = models.CharField()
    
    
def create_dynamic_model(model_name, base_model_class):
    # Check if the model already exists
    if model_name in apps.all_models['register_student']:
        return apps.get_model('register_student', model_name)

    # Get the fields from the base model (Student)
    base_model_fields = base_model_class._meta.fields

    # Define the new model class with the provided name
    class Meta:
        verbose_name = model_name  # Set a user-friendly name

    attrs = {
        '__module__': __name__,
        'Meta': Meta,
    }

    # Create a list of field instances for the new model
    dynamic_fields = []
    for field in base_model_fields:
        # Exclude BigAutoField from dynamic model
        if not isinstance(field, models.BigAutoField):
            # Clone the field and add it to the list of dynamic fields
            dynamic_field = field.clone()
            dynamic_fields.append(dynamic_field)

            # Add the dynamic field to the attrs dictionary
            attrs[field.name] = dynamic_field

    # Create the dynamic model class
    CustomModel = type(model_name, (models.Model,), attrs)

    # Register the dynamic model in Django's app registry
    apps.register_model('register_student', CustomModel)

    # Create a migration operation to create the dynamic model
    migration = migrations.CreateModel(
        name=model_name,
        fields=dynamic_fields,  # Use the list of field instances
        options={'verbose_name': model_name},
    )

    # Apply the migration
    migration.apply(
        database='default',
        project_state=migrations.state.ProjectState.from_apps(apps),
    )

    return CustomModel

def create_tables(unique_table_names):
    create_dynamic_model(unique_table_names+'_exam_results', ExamResults)
    create_dynamic_model(unique_table_names+'_leader_board', LeaderBoard)
    create_dynamic_model(unique_table_names+'_attendance', Attendance)
    create_dynamic_model(unique_table_names+'_daily_updates', DailyUpdates)
    
class className(models.Model):
    class_name = models.CharField(max_length=10)

class division(models.Model):
    division_name = models.CharField(max_length=1)
    
class subjects(models.Model):
    subjects_name = models.CharField(max_length=10)
    
class batchYear(models.Model):
    batch_year = models.TextField(null=False, blank=False,default=0)
    
class table_names(models.Model):
    table_name = models.TextField(null=False, blank=False,default=0)
