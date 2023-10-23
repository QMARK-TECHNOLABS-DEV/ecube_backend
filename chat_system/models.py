from django.db import models
from register_student.models import Student

class ChatRoom(models.Model):
    admission_no = models.CharField(max_length=100, unique=True)
    superuser = models.ForeignKey(Student, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name
    

class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    message = models.TextField()
    sender_id = models.CharField(max_length=100, null=True, blank=True,default='Student')
    superadmin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chat_room.admission_no}: {self.message}"
