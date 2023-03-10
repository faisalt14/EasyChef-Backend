from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView, DestroyAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
import datetime

from recipes.models import RecipeModel, IngredientModel, StepModel, StepMediaModel
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from recipes.serializers import RecipeSerializer, IngredientSerializer, StepSerializer, RecipeMediaSerializer, StepMediaSerializer
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

    permission_classes = [IsAuthenticated]


    def get(self, request, *args, **kwargs):
        # get the id of the based_on recipe
        base_recipe = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])
        base_recipe_serialized = RecipeSerializer(base_recipe)
        step_data = StepSerializer(base_recipe.steps.all(), many=True)
        media_data = RecipeMediaSerializer(base_recipe.media.all(), many=True)
        ingredients_data = IngredientSerializer(base_recipe.ingredients.all(), many=True)


        base_recipe_data = {
        'user_id': base_recipe.user_id.id, 'name': base_recipe.name, 'based_on': base_recipe_serialized.data, 'total_reviews': 0, 'total_likes': 0, 'total_favs': 0, 'published_time': '', 'difficulty': base_recipe.difficulty, 'meal': base_recipe.meal,
        'diet': base_recipe.diet, 'cuisine': base_recipe.cuisine, 'cooking_time': base_recipe.cooking_time, 'prep_time': base_recipe.prep_time, 'servings_num': base_recipe.servings_num, 
        'media': media_data.data, 'steps': step_data.data, 'ingredients': ingredients_data.data
        }

        return Response(base_recipe_data)
        # send a response with the fields filled out except for reviews and the like

    def post(self, request, *args, **kwargs):
        # Get the base recipe object
        base_recipe = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])
        base_recipe_data = RecipeSerializer(base_recipe).data


        # Create a new dictionary with the POST data, pre-filling the 'based_on' field
        request_data = request.data.copy()
        base_recipe_data.update(request_data)

        base_recipe_data['based_on'] = base_recipe.id
        base_recipe_data['user_id'] = request.user.id
        base_recipe_data['published_time'] = datetime.datetime.now()

        # Create a new recipe object and validate the data
        serializer = RecipeSerializer(data=base_recipe_data)
        if serializer.is_valid():
            new_recipe = serializer.save()

            # Set the 'based_on' and 'user_id' fields and save the recipe
            new_recipe.based_on = base_recipe
            new_recipe.user_id = request.user
            new_recipe.save()

            # Serialize and return the new recipe object
            serialized_recipe = RecipeSerializer(new_recipe)
            return Response(serialized_recipe.data)
        else:
            return Response(serializer.errors, status=400)


        # post the recipe
        # base_recipe = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])
        # new_recipe = RecipeModel.objects.create(
        #     user_id=self.request.user,
        #     name=base_recipe.name,
        #     based_on=base_recipe,
        #     total_reviews=0,
        #     total_likes=0,
        #     total_favs=0,
        #     published_time=datetime.datetime.now,
        #     difficulty=base_recipe.difficulty,
        #     meal=base_recipe.meal,
        #     diet=base_recipe.diet,
        #     cuisine=base_recipe.cuisine,
        #     cooking_time=base_recipe.cooking_time,
        #     prep_time=base_recipe.prep_time,
        #     servings_num=base_recipe.servings_num,
        # )

        # # Add the steps
        # steps = StepModel.objects.get(recipe_id=base_recipe)
        # for step in steps:
        #     Step.objects.create(
        #         recipe_id=new_recipe,
        #         step_num=step.step_num,
        #         cooking_time=step.cooking_time,
        #         prep_time=step.prep_time,
        #         instructions=step.instructions
        #     )

        # # Add the media
        # media = RecipeMedia.objects.filter(recipe=base_recipe)
        # for media_item in media:
        #     RecipeMedia.objects.create(
        #         recipe=new_recipe,
        #         media_type=media_item.media_type,
        #         media_url=media_item.media_url
        #     )

        # # Add the ingredients
        # ingredients = Ingredient.objects.filter(recipe=base_recipe)
        # for ingredient in ingredients:
        #     Ingredient.objects.create(
        #         recipe=new_recipe,
        #         name=ingredient.name,
        #         amount=ingredient.amount
        #     )

        # # Serialize the new recipe
        # serializer = RecipeSerializer(new_recipe)
        # serializer = RecipeSerializer(new_recipe, data=request.data, partial=True)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateRecipeView(RetrieveUpdateAPIView, CreateAPIView):
    # To create a recipe, send a POST request to /recipes/create-recipe/.
    # To update a recipe with ID 123, send a PUT or PATCH request to /recipes/123/.

    permission_classes = [IsAuthenticated]
    queryset = RecipeModel.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        # Set the user to the currently logged in user
        serializer.save(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        step_ids = []
        ingredient_ids = []
        media_ids = []

        steps_list = request.data.get('steps', [])
        ingredients_list = request.data.get('ingredients', [])
        media_list = request.data.get('media', [])

        recipe_data = request.data.copy()
        recipe_data['published_time'] = datetime.datetime.now()
        recipe_serializer = RecipeSerializer(data=recipe_data)
        recipe_serializer.is_valid(raise_exception=True)
        recipe = recipe_serializer.save()
                
        # # Create Step instances
        for index, step_data in enumerate(steps_list):
            base_step = get_object_or_404(StepModel, id=step_data)
            base_step.recipe_id = recipe.id
            base_step.step_num = index + 1
            step_ids.append(base_step)
            # step_serializer = StepSerializer(data=step_data)
            # step_serializer.is_valid(raise_exception=True)
            # step = step_serializer.save()
            # step_ids.append(step.id)

            
        # # Create Ingredient instances
        for ingredient_data in ingredients_list:
            ingredient_base = get_object_or_404(IngredientModel, id=ingredient_data)
            ingredient_base.recipe_id = recipe.id
            ingredient_ids.append(ingredient_base)

            # ingredient_data['recipe_id'] = recipe.id
            # ingredient_serializer = IngredientSerializer(data=ingredient_data)
            # ingredient_serializer.is_valid(raise_exception=True)
            # ingredient = ingredient_serializer.save()
            # ingredient_ids.append(ingredient.id)

        # # Create Media instances
        for media_data in media_list:
            media_base = get_object_or_404(RecipeMediaModel, id=media_data)
            media_base.recipe_id = recipe.id
            media_ids.append(media_base)

            # media_data['recipe_id'] = recipe.id
            # media_serializer = RecipeMediaSerializer(data=media_data)
            # media_serializer.is_valid(raise_exception=True)
            # media = media_serializer.save()
            # media_ids.append(media.id)
        
        
        # Create Recipe instance
        # recipe_data = request.data.copy()
        recipe.steps.set(step_ids)
        recipe.ingredients.set(ingredient_ids)
        recipe.media.set(media_ids)
        recipe.save()

        # recipe_data['published_time'] = datetime.datetime.now()
        # recipe_serializer = RecipeSerializer(data=recipe_data)
        # recipe_serializer.is_valid(raise_exception=True)
        # recipe_serializer.save()
        
        return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)


    def update(self, request, *args, **kwargs):
        # get the instance of the model we are updating
        instance = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])

        # we update it from the serializer and save it to the database
        # partial = True allows us to retain data that was already there (hence the editing)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data)

    # def get(self, request):
    #     current_user_id = request.user.id
    #     recipe = RecipeModel(user_id=current_user_id)
    #     serializer = RecipeSerializer(recipe)
    #     return Response(serializer.data)
    #     # current_user_id = request.user.id
    #     # data = {'user_id': current_user_id, 'name': "", 'based_on': None, 'total_reviews': 0, 'total_likes': 0, 'total_favs': 0, 'published_time': '', 'difficulty': '', 'meal': '',
    #     # 'diet': '', 'cuisine': '', 'cooking_time': '', 'prep_time': '', 'servings_num': '', 'media': [], 'steps': [], 'ingredients': []}
    #     # serializer = RecipeSerializer(data=data)
    #     # serializer.is_valid()
    #     # return Response(serializer.data)

    # def perform_create(self, serializer):
    #     serializer.save(user_id=self.request.user.id)

    # def post(self, request):
    #     serializer = RecipeSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(user_id=self.request.user.id, published_time=datetime.datetime.now())
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IngredientAutocompleteView(ListAPIView):
    serializer_class = IngredientSerializer
    queryset = IngredientModel.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('query', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

# class CreateStepView(CreateAPIView):
#     queryset = StepModel.objects.all()
#     serializer_class = StepSerializer
    
#     def perform_create(self, serializer):
#         recipe_id = self.kwargs['recipe_id']
#         recipe = RecipeModel.objects.get(id=recipe_id)
#         serializer.save(recipe_id=recipe)

class CreateStepView(CreateAPIView):
    queryset = StepModel.objects.all()
    serializer_class = StepSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        return serializer.data

class AddRecipeMedia(CreateAPIView):
    queryset = StepMediaModel.objects.all()
    serializer_class = RecipeMediaSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        return serializer.data


class AddStepMedia(CreateAPIView):
    queryset = StepMediaModel.objects.all()
    serializer_class = StepMediaSerializer

class CreateIngredientView(CreateAPIView):
    serializer_class = IngredientSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        return serializer.data

class RecipeDetailView(RetrieveAPIView):
    serializer_class = RecipeSerializer
    queryset = RecipeModel.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['recipe_id'])
        return obj
