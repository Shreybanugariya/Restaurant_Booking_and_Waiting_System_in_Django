from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True) 
    address = models.TextField()
    contact= models.CharField(max_length=10)

    def __str__(self):
        return self.username
