from django.contrib import admin

from .models import RecipeModel, RecipeMediaModel, ReviewMediaModel, IngredientModel, InteractionModel, StepMediaModel, StepModel

# Register your models here.
admin.site.register(RecipeModel)
admin.site.register(RecipeMediaModel)
admin.site.register(ReviewMediaModel)
admin.site.register(IngredientModel)
admin.site.register(InteractionModel)
admin.site.register(StepMediaModel)
admin.site.register(StepModel)


