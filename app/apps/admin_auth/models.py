from django.db import models
from django.utils import timezone


class Admin(models.Model):
    email = models.TextField(max_length=100, unique=True)
    password = models.TextField(max_length=100)
    login_type = models.CharField(max_length=20, default="email")

    def __str__(self):
        return self.id


class PasswordResetToken(models.Model):
    user = models.ForeignKey(Admin, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username
