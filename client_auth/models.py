from django.db import models
from register_student.models import Student

# Create your models here.
class Token(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    access_token = models.TextField(unique=True)
    refresh_token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.id}"