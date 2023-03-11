from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    '''
    Foreign Keys To Keep Track Of:
    - RecipeModel for recipes the user owns
    - InteractionModel for interactions that the user did
    - ShoppingRecipeModel for recipes in the shopping cart of the user
    '''
    phone_num = models.CharField(max_length = 100, default="", null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
