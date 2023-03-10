from django.urls import path

from recipes.views import AllRecipes, PopularRecipes

urlpatterns = [
    path('all-recipes/', AllRecipes.as_view()),
    path('popular/<str:filter>/', PopularRecipes.as_view()),
]
