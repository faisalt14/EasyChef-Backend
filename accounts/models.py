from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    
    phone_num = models.CharField(max_length = 100, default="", null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
