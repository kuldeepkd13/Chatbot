from django.db import models
from django.utils import timezone

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  
    confirm_password = models.CharField(max_length=128)
    last_login = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username
