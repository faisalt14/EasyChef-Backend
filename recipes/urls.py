from django.urls import path
from recipes.views import AllRecipes, PopularRecipes, IngredientAutocompleteView, CreateIngredientView, CreateRecipeView, RemixRecipeView, CreateStepView, RecipeDetailView, AddStepMedia, AddRecipeMedia, AddInteractionMedia, InteractionView, DeleteRecipe

urlpatterns = [
    path('all-recipes/', AllRecipes.as_view()),
    path('popular/<str:filter>/', PopularRecipes.as_view()),
    path('ingredients/autocomplete/', IngredientAutocompleteView.as_view()),
    path('create-recipe/', CreateRecipeView.as_view()),
    path('<int:recipe_id>/', CreateRecipeView.as_view()), 
    path('<int:recipe_id>/remix-recipe/', RemixRecipeView.as_view()),
    path('steps/create/', CreateStepView.as_view()),
    path('steps/create/media/', AddStepMedia.as_view()),
    path('create-recipes/add-media/', AddRecipeMedia.as_view()),
    path('ingredients/create/', CreateIngredientView.as_view()),
    path('<recipe_id>/details/', RecipeDetailView.as_view()),
    path('<recipe_id>/details/interaction/', InteractionView.as_view()),
    path('<interaction_id>/add-media/', AddInteractionMedia.as_view()),
    path('<recipe_id>/delete/', DeleteRecipe.as_view())
]
