from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView

from recipes.models import RecipeModel
from recipes.serializers import RecipesSerializer


class AllRecipes(ListAPIView):
    serializer_class = RecipesSerializer

    def get_queryset(self):
        return RecipeModel.objects.all()
