from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView, DestroyAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone


from recipes.models import RecipeModel, IngredientModel, StepModel, StepMediaModel, RecipeMediaModel
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from recipes.serializers import RecipesSerializer, RecipeSerializer, IngredientSerializer, StepSerializer, RecipeMediaSerializer, StepMediaSerializer, ReviewMediaSerializer, InteractionSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from accounts.serializers import UserDetailSerializer
import json

from rest_framework.exceptions import APIException



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


    def update(self, request, *args, **kwargs):
        # get the instance of the model we are updating
        instance = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])
        if self.request.user != instance.user_id:
            return Response('Forbidden', status=403)

        # calculate the ratio of new servings to old servings
        #old_servings = instance.servings_num
        #new_servings = request.data.get('servings_num', old_servings)
        #ratio = int(new_servings) / int(old_servings)

        # update the instance from the serializer and save it to the database
        # partial = True allows us to retain data that was already there (hence the editing)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(user=self.request.user)

        # adjust ingredient quantities based on the new ratio
        #for ingredient_instance in recipe.ingredients.all():
            # calculate the new quantity based on the new number of servings
        #    servings_num = int(request.data.get('servings_num', recipe.servings_num))
        #    new_quantity = int(round(ingredient_instance.quantity / recipe.servings_num * servings_num))

            # update the ingredient quantity
        #    ingredient_instance.quantity = new_quantity
        #    ingredient_instance.save()

        return Response(serializer.data)

class IngredientAutocompleteView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IngredientSerializer
    queryset = IngredientModel.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('query', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query, recipe_id=None)
        else:
            queryset = queryset.filter(recipe_id=None)
        return queryset


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


    def update(self, request, *args, **kwargs):
        # get the instance of the model we are updating
        instance = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])
        if self.request.user != instance.user_id:
            return Response('Forbidden', status=403)

        # calculate the ratio of new servings to old servings
        #old_servings = instance.servings_num
        #new_servings = request.data.get('servings_num', old_servings)
        #ratio = int(new_servings) / int(old_servings)

        # update the instance from the serializer and save it to the database
        # partial = True allows us to retain data that was already there (hence the editing)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(user=self.request.user)

        # adjust ingredient quantities based on the new ratio
        #for ingredient_instance in recipe.ingredients.all():
            # calculate the new quantity based on the new number of servings
        #    servings_num = int(request.data.get('servings_num', recipe.servings_num))
        #    new_quantity = int(round(ingredient_instance.quantity / recipe.servings_num * servings_num))

            # update the ingredient quantity
        #    ingredient_instance.quantity = new_quantity
        #    ingredient_instance.save()

        return Response(serializer.data)

class IngredientAutocompleteView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IngredientSerializer
    queryset = IngredientModel.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('query', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query, recipe_id=None)
        else:
            queryset = queryset.filter(recipe_id=None)
        return queryset


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


class InteractionView(RetrieveUpdateAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]

    
    
    # I can update my vote
    # mark/unmark a recipe as fav
    # post a comment
    # this should update the recipe fields
    # I can change the servings (this should create a ShoppingListModel)

    
