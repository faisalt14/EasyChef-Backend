from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView
from rest_framework.views import APIView

from recipes.models import RecipeModel, IngredientModel,StepModel
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from recipes.serializers import RecipeSerializer, IngredientSerializer, StepSerializer, RecipeMediaSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from accounts.serializers import UserDetailSerializer

# Create your views here.

class RemixRecipeView(APIView):
    """
    This view is for remix recipe view
    """
    # TODO authenticate with token

    def get(self, request, *args, **kwargs):
        # get the id of the based_on recipe
        base_recipe = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])
        base_recipe_serialized = RecipeSerializer(base_recipe)
        user_serializer = UserDetailSerializer(base_recipe.user_id)
        step_data = StepSerializer(base_recipe.steps.all(), many=True)
        media_data = RecipeMediaSerializer(base_recipe.media.all(), many=True)
        ingredients_data = IngredientSerializer(base_recipe.ingredients.all(), many=True)


        base_recipe_data = {
        'user_id': user_serializer.data, 'name': base_recipe.name, 'based_on': base_recipe_serialized.data, 'total_reviews': 0, 'total_likes': 0, 'total_favs': 0, 'published_time': '', 'difficulty': base_recipe.difficulty, 'meal': base_recipe.meal,
        'diet': base_recipe.diet, 'cuisine': base_recipe.cuisine, 'cooking_time': base_recipe.cooking_time, 'prep_time': base_recipe.prep_time, 'servings_num': base_recipe.servings_num, 
        'media': media_data.data, 'steps': step_data.data, 'ingredients': ingredients_data.data
        }

        return Response(base_recipe_data)
        # send a response with the fields filled out except for reviews and the like

    def post(self, request, *args, **kwargs):
        # post the recipe
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)


class CreateRecipeView(CreateAPIView):

    # TODO authenticate with token

    serializer_class = RecipeSerializer
    # permission_class = [IsAuthenticated]
    def get(self, request):
        current_user_id = request.user.id
        data = {'user_id': current_user_id, 'name': "", 'based_on': None, 'total_reviews': 0, 'total_likes': 0, 'total_favs': 0, 'published_time': '', 'difficulty': '', 'meal': '',
        'diet': '', 'cuisine': '', 'cooking_time': '', 'prep_time': '', 'servings_num': '', 'media': "", 'steps': "", 'ingredients': ""}
        serializer = RecipeSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def post(self, request):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            recipe = serializer.save()
            recipe.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IngredientAutocompleteView(ListAPIView):
    serializer_class = IngredientSerializer
    queryset = IngredientModel.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('query', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

class CreateStepView(CreateAPIView):
    queryset = StepModel.objects.all()
    serializer_class = StepSerializer
    
    def perform_create(self, serializer):
        recipe_id = self.kwargs['recipe_id']
        recipe = RecipeModel.objects.get(id=recipe_id)
        serializer.save(recipe_id=recipe)

class AddStepMedia(APIView):
    pass

class AddRecipeMedia(APIView):
    pass
                        

class RecipeDetailView(RetrieveAPIView):
    serializer_class = RecipeSerializer
    queryset = RecipeModel.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['recipe_id'])
        return obj