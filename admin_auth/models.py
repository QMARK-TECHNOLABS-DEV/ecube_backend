from django.db import models

class Admin(models.Model):
    email = models.TextField(max_length=100, unique=True)
    password = models.TextField(max_length=100)
    logged_in = models.BooleanField(default=False)
    login_type = models.CharField(max_length=20, default='email')
    
    def __str__(self):
        return self.id
    
    
class Token(models.Model):
    user = models.ForeignKey(Admin, on_delete=models.CASCADE)
    access_token = models.TextField(unique=True)
    refresh_token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.id}"
