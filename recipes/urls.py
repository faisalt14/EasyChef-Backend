from django.urls import path
from recipes.views import IngredientAutocompleteView, CreateRecipeView

urlpatterns = [
   path('ingredients/autocomplete/', IngredientAutocompleteView.as_view()),
   path('create-recipe/', CreateRecipeView.as_view()),
]