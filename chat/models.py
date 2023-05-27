from django.db import models
from django.contrib.auth import get_user_model

class Message(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
