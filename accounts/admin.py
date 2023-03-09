from django.contrib import admin
from accounts.models import User, ShoppingRecipeModel

# Register your models here.
admin.site.register(User)
admin.site.register(ShoppingRecipeModel)