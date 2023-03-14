import json
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import APIException
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, CreateAPIView, ListAPIView, DestroyAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from recipes.models import RecipeModel, IngredientModel, StepModel, StepMediaModel, RecipeMediaModel, InteractionModel, ReviewMediaModel
from recipes.serializers import RecipesSerializer, RecipeSerializer, IngredientSerializer, StepSerializer, RecipeMediaSerializer, StepMediaSerializer, ReviewMediaSerializer, InteractionSerializer
from accounts.models import User
from accounts.serializers import UserDetailSerializer

# Create your views here.


class AllRecipes(ListAPIView):
    serializer_class = RecipesSerializer

    def get_queryset(self):
        return RecipeModel.objects.all()


class PopularRecipes(ListAPIView):
    serializer_class = RecipesSerializer

    def get_queryset(self):
        options = ['total_reviews', 'total_likes', 'total_favs']
        if self.kwargs['filter'] not in options:
            # return Response(
            #     {
            #         'Error': 'Not a valid filter. Please select a filter from the following list',
            #         'Possible Values': options
            #     }
            # )
            raise APIException("Not a valid filter. Please select a filter from the following list: "
                               "['total_reviews', 'total_likes', 'total_favs']")
        else:
            return RecipeModel.objects.all().order_by('-' + self.kwargs['filter'])

class RemixRecipeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeSerializer

    def post(self, request, *args, **kwargs):

        # Get the original recipe
        original_recipe = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])

        # Create a new recipe instance
        new_recipe = RecipeModel()

        # Update the new recipe instance with values from the original recipe and user input
        for key, value in original_recipe.__dict__.items():
            if key not in ["_state", "id"]:
                setattr(new_recipe, key, value)

        new_recipe.id = None
        new_recipe.pk = None
        new_recipe.user_id = request.user
        new_recipe.based_on = original_recipe
        new_recipe.published_time = timezone.now()
        new_recipe.save()

        # Copy over foreign key relations for StepModel
        new_steps = []

        for step in original_recipe.steps.all():
            new_step = StepModel(recipe_id=new_recipe, step_num=step.step_num, cooking_time = step.cooking_time, prep_time= step.prep_time, instructions= step.instructions)
            new_step.save()
            new_steps.append(new_step)

        new_recipe.steps.set(new_steps)

        # Copy over foreign key relations for IngredientModel
        new_ingredients = []
        for ingredient in original_recipe.ingredients.all():
            new_ingredient = IngredientModel(recipe_id=new_recipe, name=ingredient.name, quantity=ingredient.quantity, unit=ingredient.unit)
            new_ingredient.save()
            new_ingredients.append(new_ingredient)
        new_recipe.ingredients.set(new_ingredients)

        # Copy over foreign key relations for RecipeMediaModel
        new_medias = []
        for item in original_recipe.media.all():
            new_media = RecipeMediaModel(recipe_id=new_recipe, media=item.media)
            new_media.save()
            new_medias.append(new_media)
        new_recipe.media.set(new_medias)

        # Update the new recipe instance with values from user input
        for key, value in request.data.items():
            if key == "steps":
                steps_list = [int(x.strip()) for x in value.split(",")]
                step_ids = []
                # Create Step instances
                total_cook = timedelta(hours=0, minutes=0)
                total_prep = timedelta(hours=0, minutes=0)

                for index, step_id in enumerate(steps_list):
                    base_step = get_object_or_404(StepModel, id=step_id)
                    total_cook += base_step.cooking_time
                    total_prep += base_step.prep_time
                    base_step.recipe_id = new_recipe
                    base_step.step_num = index + 1
                    base_step.save()
                    step_ids.append(base_step)
                recipe.calculated_prep_time = total_prep
                recipe.calculated_cooking_time = total_cook
                new_recipe.steps.set(step_ids)
                new_recipe.save()

            if key == "ingredients":     
                ingredients_list = json.loads(value)
                ingredient_ids = []
                # Create Ingredient instances
                for ingredient_id, data in ingredients_list.items():
                    quantity = data[0]
                    unit = data[1]
                    ingredient_base = get_object_or_404(IngredientModel, id=ingredient_id)
                    copied_ingredient = IngredientModel()
                    copied_ingredient.recipe_id = new_recipe
                    
                    copied_ingredient.quantity = quantity
                    #copied_ingredient.quantity = int(int(ingredient_base.quantity) / int(original_recipe.servings_num) * int(new_recipe.servings_num))

                    copied_ingredient.unit = unit
                    copied_ingredient.save()

                    ingredient_ids.append(copied_ingredient)

                new_recipe.ingredients.set(ingredient_ids)
                new_recipe.save()

            if key == "media":
                media_list = [int(x.strip()) for x in value.split(",")]
                media_ids = []
                # Create Media instances
                for media_data in media_list:
                    media_base = get_object_or_404(RecipeMediaModel, id=media_data)
                    media_base.recipe_id = new_recipe
                    media_base.save()
                    media_ids.append(media_base)
                new_recipe.media.set(media_ids)
                new_recipe.save()

            if key in ['cooking_time', 'prep_time']:
                if isinstance(value, str):
                    hours, minutes, seconds = map(int, value.split(":"))
                    delta = timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
                else:
                    delta = value

            if key not in ["steps", "ingredients", "media", 'cooking_time', 'prep_time']:
                setattr(new_recipe, key, value)

        # Save the new recipe instance
        setattr(new_recipe, 'total_favs', 0)
        setattr(new_recipe, 'total_likes', 0)
        setattr(new_recipe, 'total_reviews', 0)
        setattr(new_recipe, 'avg_rating', 0)

        new_recipe.save()

        # Return the new recipe data
        response_data = RecipeSerializer(new_recipe).data
        return Response(response_data)

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

        steps_list = request.data.get('steps', '')
        ingredients_list = request.data.get('ingredients', '')
        media_list = request.data.get('media', '')

        if steps_list:
            steps_list = [int(x.strip()) for x in steps_list.split(",")]
        if ingredients_list:
            ingredients_list = json.loads(ingredients_list)
            # ingredients_list = [int(x.strip()) for x in ingredients_list.split(",")]
        if media_list:
            media_list = [int(x.strip()) for x in media_list.split(",")]
        
        recipe_data = request.data.copy()
        recipe_data['published_time'] = timezone.now()

        # Set default values for the fields 
        required_fields = ['cooking_time', 'prep_time', 'name', 'difficulty', 'meal', 'diet', 'cuisine', 'servings_num', 'steps', 'media', 'ingredients']
        errors = []
        for field in required_fields:
            if request.data.get(field, '') == '':
                errors.append(f"{field} is required.")

        # Return errors if any required fields are empty
        if errors:
            error_message = " ".join(errors)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)


        recipe_serializer = RecipeSerializer(data=recipe_data, partial=True)
        recipe_serializer.is_valid(raise_exception=True)
        recipe = recipe_serializer.save()

        # # Create Step instances
        total_cook = timedelta(hours=0, minutes=0)
        total_prep = timedelta(hours=0, minutes=0)
        for index, step_id in enumerate(steps_list):
            base_step = get_object_or_404(StepModel, id=step_id)
            total_cook += base_step.cooking_time
            total_prep += base_step.prep_time
            base_step.recipe_id = recipe
            base_step.step_num = index + 1
            base_step.save()
            step_ids.append(base_step)
            
        # # Create Ingredient instances
        for ingredient_id, ingredient_data in ingredients_list.items():
            ingredient_base = get_object_or_404(IngredientModel, id=int(ingredient_id))

            # make a copy of the base ingredient - base ingredient has null
            copied_ingredient = IngredientModel()
            copied_ingredient.name = ingredient_base.name
            copied_ingredient.recipe_id = recipe
            copied_ingredient.quantity = ingredient_data[0]
            copied_ingredient.unit = ingredient_data[1]
            copied_ingredient.save()
            ingredient_ids.append(copied_ingredient)

        # # Create Media instances
        for media_data in media_list:
            media_base = get_object_or_404(RecipeMediaModel, id=media_data)
            media_base.recipe_id = recipe
            media_base.save()
            media_ids.append(media_base)
        
        # Create Recipe instance
        recipe.steps.set(step_ids)
        recipe.ingredients.set(ingredient_ids)
        recipe.media.set(media_ids)
        recipe.calculated_prep_time = total_prep
        recipe.calculated_cook_time = total_cook
        # we need to calculate the total cooking time, prep_time

        #servings_num = request.data.get('servings_num')
        #if servings_num:
        #    recipe_ingredient_instances = recipe.ingredients.all()
        #    for ingredient_instance in recipe_ingredient_instances:
        #        new_quantity = int(ingredient_instance.quantity) * int(servings_num)
        #        ingredient_instance.quantity = int(new_quantity)
        #        ingredient_instance.save(update_fields=['quantity'])

        recipe.save()


        
        return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)

class RecipeUpdateView(UpdateAPIView):
    queryset = RecipeModel.objects.all()
    serializer_class = RecipeSerializer

    def patch(self, request, *args, **kwargs):
        recipe = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])

        # Check if the authenticated user is the owner of the recipe
        if request.user != recipe.user_id:
            return Response({'message': 'You do not have permission to edit this recipe.'}, status=403)

        serializer = self.get_serializer(recipe, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateStepView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StepSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        return serializer.data

class AddRecipeMedia(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StepMediaModel.objects.all()
    serializer_class = RecipeMediaSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        return serializer.data


class AddStepMedia(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StepMediaSerializer

class CreateIngredientView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IngredientSerializer
    
    def perform_create(self, serializer):
        name = serializer.validated_data.get('name')
        if IngredientModel.objects.filter(name=name).exists():
            return Response({'message': 'Ingredient with this name already exists.'})
        serializer.save()
        return serializer.data

class RecipeDetailView(RetrieveAPIView):
    serializer_class = RecipeSerializer
    queryset = RecipeModel.objects.all()
    permission_classes = []

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['recipe_id'])
        return obj

class DeleteRecipe(DestroyAPIView):
    # handles DELETE requests
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])

        # Check if the authenticated user is the owner of the recipe
        if request.user != recipe.user_id:
            return Response({'message': 'You do not have permission to delete this recipe.'}, status=403)

        recipe.delete()
        return Response({'message': 'Recipe has been deleted.'}, status=204)

class AddInteractionMedia(CreateAPIView):
    serializer_class = ReviewMediaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the interaction, if it exists
        interaction = get_object_or_404(InteractionModel, id=self.kwargs['interaction_id'])
        try:
            # Attempt to create a new ReviewMediaModel
            review_media = ReviewMediaModel.objects.create(interaction_id=interaction, media=request.FILES['media'])
        except:
            # If the above attempt is unsuccessful, respond with error
            return Response({'message': 'invalid upload'}, status=400)
        # If a new ReviewMediaModel was created, save it in our database and return
        review_media.save()
        return Response({'message': 'media saved'}, status=200)


class InteractionView(RetrieveUpdateAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = InteractionSerializer(data=request.data)
        try:
            # Check if there already exists an InteractionModel between the user and the recipe
            interaction = InteractionModel.objects.get(user_id=request.user, recipe_id=self.kwargs['recipe_id'])
        except:
            # If no such InteractionModel exists, create a new one
            serializer.is_valid(raise_exception=True)
            if (not request.data.get('comment')) != (not request.data.get('rating')):
                return Response({'message': 'ratings and comments must be paired.'}, status=400)
            serializer.create(request.data, request.user, get_object_or_404(RecipeModel, id=self.kwargs['recipe_id']))
            return Response({'message': 'Created a new interaction'}, status=200)
        print(InteractionModel.objects.get(user_id=request.user, recipe_id=self.kwargs['recipe_id']))
        return Response({'message': 'There already exists an interaction between this user and the recipe. Use a PATCH request instead.'}, status=400)

    def patch(self, request, *args, **kwargs):
        serializer = InteractionSerializer(data=request.data)
        try:
            # Check if there already exists an InteractionModel between the user and the recipe
            interaction = InteractionModel.objects.get(user_id=request.user, recipe_id=self.kwargs['recipe_id'])
        except:
            # If no InteractionModel exists, return with information
            return Response({'message': 'There is no interaction between this user and the recipe. Use a POST request instead.'}, status=400)
        # If an InteractionModel does exist, update its data instead of making a new one
        if (not request.data.get('comment')) != (not request.data.get('rating')):
            return Response({'message': 'ratings and comments must be paired.'}, status=400)
        serializer.update(request.data, interaction)
        return Response({'message': 'Updated an existing interaction'}, status=200)
    
    # I can update my vote
    # mark/unmark a recipe as fav
    # post a comment
    # this should update the recipe fields
    # I can change the servings (this should create a ShoppingListModel)

    

class SearchView(ListAPIView):
    serializer_class = RecipesSerializer
    
    def get_queryset(self):

        # Create the base search results based on simple dropdown filters
        search_results = RecipeModel.objects.filter(cuisine=int(self.request.query_params.get('cuisine'))).distinct() if (int(self.request.query_params.get('cuisine', 14)) < 14) else RecipeModel.objects.all()
        search_results = search_results.filter(diet=int(self.request.query_params.get('diet', 5))).distinct() if (int(self.request.query_params.get('diet', 6)) < 6) else search_results
        search_results = search_results.filter(meal=int(self.request.query_params.get('meal', 5))).distinct() if (int(self.request.query_params.get('meal', 6)) < 6) else search_results
        

        # Check for the search query based on the search category
        category = self.request.query_params.get('category', '')
        query = self.request.query_params.get('query', '')
        if category == 'Recipe':
            search_results = search_results.filter(name__icontains=query).distinct()
        elif category == 'Ingredients':
            search_results = search_results.filter(ingredients__name__icontains=query).distinct()
        elif category == 'User':
            search_results = search_results.filter(user_id__username__icontains=query).distinct()
        else:
            raise APIException("Not a valid search category. Please select a category from the following list: "
                               "['Recipe', 'Ingredients', 'User']")

        try:
            cooking_time = int(self.request.query_params.get('cooking_time', 0))
        except:
            raise APIException("Not a valid cooking time filter. Please select a cooking from the following list by inputting its number: "
                               "[0: None, 1: Less than 10 minutes, 2: Between 10 and 30 minutes, 3: Between 30 and 60 minutes, 4: One hour or longer]")
        # Filter by cooking time filter
        # match case would probably work better here
        if cooking_time == 0:
            return search_results
        elif cooking_time == 1:
            return search_results.filter(cooking_time__lte=timedelta(minutes=10)).distinct()
        elif cooking_time == 2:
            return search_results.filter(cooking_time__lte=timedelta(minutes=30), cooking_time__gte=timedelta(minutes=10)).distinct()
        elif cooking_time == 3:
            return search_results.filter(cooking_time__lte=timedelta(minutes=60), cooking_time__gte=timedelta(minutes=30)).distinct()
        else:
            return search_results.filter(cooking_time__gte=timedelta(minutes=60)).distinct()

class HomeView(APIView):
    serializer_class = RecipesSerializer

    def get(self, request):
        PopularSet = RecipeModel.objects.all().order_by('-total_reviews')[:6]
        BreakfastSet = RecipeModel.objects.filter(meal=0).order_by('total_favs')[:6]
        LunchSet = RecipeModel.objects.filter(meal=1).order_by('total_favs')[:6]
        DinnerSet = RecipeModel.objects.filter(meal=2).order_by('total_favs')[:6]
        return Response({'Popular' : RecipesSerializer(PopularSet, many=True).data,
                         'Breakfasts' : RecipesSerializer(BreakfastSet, many=True).data,
                         'Lunches': RecipesSerializer(LunchSet, many=True).data,
                         'Dinners': RecipesSerializer(DinnerSet, many=True).data})

class AutocompleteView(ListAPIView):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        # Get values from params, default will be 0
        category = int(self.request.query_params.get('category', '0'))
        search_query = self.request.query_params.get('query', '')
        # Set up serializers and querysets based on category, default is the IngredientModel
        if category == 1:
            self.serializer_class = RecipesSerializer
            queryset = RecipeModel.objects.all()
        elif category == 2:
            self.serializer_class = UserDetailSerializer
            queryset = User.objects.all()
            queryset = queryset.filter(username__icontains=search_query)
        else:
            queryset = IngredientModel.objects.filter(recipe_id=None)

        if search_query and category != 2:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset
