from django.urls import path
from recipes.views import IngredientAutocompleteView, CreateRecipeView, RemixRecipeView, CreateStepView, RecipeDetailView

urlpatterns = [
   path('ingredients/autocomplete/', IngredientAutocompleteView.as_view()),
   path('create-recipe/', CreateRecipeView.as_view()),
   path('<int:recipe_id>/remix-recipe/', RemixRecipeView.as_view()),
   path('create-recipe/<int:recipe_id>/create-step/', CreateStepView.as_view()),
   path('<recipe_id>/details/', RecipeDetailView.as_view()),
]
