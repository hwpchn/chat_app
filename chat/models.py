from django.db import models
from django.contrib.auth import get_user_model


class Message(models.Model):
    user = models.ForeignKey(get_user_model(), related_name='messages_sent', on_delete=models.CASCADE)
    recipient = models.ForeignKey(get_user_model(), related_name='messages_received', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
