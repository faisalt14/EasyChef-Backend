from django.urls import path

from recipes.views import AllRecipes, PopularRecipes, AddInteractionMedia, InteractionView, DeleteRecipe

urlpatterns = [
    path('all-recipes/', AllRecipes.as_view()),
    path('popular/<str:filter>/', PopularRecipes.as_view()),
    path('<recipe_id>/details/interaction/', InteractionView.as_view()),
    path('<interaction_id>/add-media/', AddInteractionMedia.as_view()),
    path('<recipe_id>/delete/', DeleteRecipe.as_view())
]
