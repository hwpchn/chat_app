from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
