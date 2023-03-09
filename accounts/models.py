from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser):
    phone_num = models.CharField(max_length=100, default="", null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)


class ShoppingRecipeModel(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=False, related_name="shoppingCartItems")
    recipe = models.ForeignKey("recipes.RecipeModel", on_delete=models.CASCADE)
    servings_num = models.PositiveIntegerField()

    def __str__(self):
        return f"User {self.user.name} has {self.recipe.name} in their shopping cart."
