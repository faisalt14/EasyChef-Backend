from django.urls import path

from recipes.views import AllRecipes, PopularRecipes, SearchView, HomeView

urlpatterns = [
    path('all-recipes/', AllRecipes.as_view()),
    path('popular/<str:filter>/', PopularRecipes.as_view()),
    path('search/', SearchView.as_view()),
    path('', HomeView.as_view()),
]
