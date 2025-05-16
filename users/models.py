from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Add additional profile fields here if needed
    bio = models.TextField(blank=True, null=True)
    badge = models.CharField(max_length=100, blank=True, null=True)
    # You can add more fields like profile_picture, phone, etc.

    def __str__(self):
        return self.username
