from django.urls import path

from recipes.views import AllRecipes

urlpatterns = [
    path('all-recipes/', AllRecipes.as_view()),
]