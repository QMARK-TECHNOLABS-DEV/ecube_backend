from django.db import models
from ..register_student.models import Student


# Create your models here.
class Token(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "token"

    def __str__(self):
        return f"Token for {self.user.id}"


class OTP(models.Model):
    credientials = models.TextField(max_length=256)
    code = models.CharField(max_length=6)
    expiry_time = models.DateTimeField(auto_now_add=True)
