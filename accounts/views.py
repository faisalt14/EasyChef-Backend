import math

from django.http import Http404
from django.shortcuts import render
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login, update_session_auth_hash
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from rest_framework.exceptions import APIException
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, get_object_or_404, \
    DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User, ShoppingRecipeModel

from accounts.serializers import UserDetailSerializer, UserLoginSerializer, UserEditSerializer, ShoppingRecipeModelSerializer
from recipes.serializers import RecipeSerializer, RecipesSerializer
from recipes.models import RecipeModel, InteractionModel, IngredientModel
from django.db.models import Q


# Create your views here.

class SignUpView(CreateAPIView):
    def post(self, request):
        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            if request.data.get('email'):
                try:
                    validate_email(request.data.get('email'))
                except ValidationError:
                    return Response({'message': 'enter a valid email'}, status=400)
            if request.data.get('password') != request.data.get('password2'):
                return Response({'message': 'passwords do not match'}, status=400)
            serializer.create(request.data)
            return Response({'message': 'signup success'}, status=200)

        if User.objects.filter(username=request.data.get('username')).exists():
            return Response({'message': 'username is already taken'}, status=400)
        errors = ""

        if not request.data.get('password2'):
            errors = errors + ' [password2 - This Field Is Required.]'
        for error in serializer.errors:
            errors = errors + ' [' + error + ' - ' + serializer.errors[error][0].title() + ']'
        return Response({'message': 'Errors in request:' + errors}, status=400)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
            if user is None:
                return Response({'message': 'Username or password is invalid'}, status=400)
            auth_logout(request)
            auth_login(request, user)
            return Response({'message': 'logged in as ' + user.username}, status=200)
        print(serializer.errors)
        return Response({'message': 'serializer is invalid!'}, status=400)


class LogoutView(APIView):
    def get(self, request):
        auth_logout(request)
        return Response({'message': 'logged out'}, status=200)


class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        if request.user.is_authenticated == False:
            return Response({'message': 'Not logged in'}, status=401)

        serializer = UserEditSerializer(data=request.data)
        if serializer.is_valid():

            if request.data.get('email'):
                try:
                    validate_email(request.data.get('email'))
                    request.user.email = request.data.get('email')
                except ValidationError:
                    return Response({'message': 'enter a valid email'}, status=400)
            if request.data.get('password') != request.data.get('password2'):
                return Response({'message': 'passwords do not match'}, status=400)
            elif request.data.get('password'):
                request.user.set_password(request.data.get('password'))

            if request.data.get('first_name'):
                request.user.first_name = request.data.get('first_name')
            if request.data.get('last_name'):
                request.user.last_name = request.data.get('last_name')
            if request.data.get('phone_num'):
                request.user.phone_num = request.data.get('phone_num')
            try:
                request.user.avatar = request.FILES['avatar']
            except:
                print('no avatar change')

            request.user.save()
            update_session_auth_hash(request, request.user)
            return Response({'message': 'edited user ' + request.user.username + "'s information"}, status=200)
        print(serializer.errors)
        Email_Error = ''
        try:
            if serializer.errors['email']:
                Email_Error = ' ' + serializer.errors['email'][0].title()
        except:
            pass
        return Response({'message': 'serializer is invalid!' + Email_Error}, status=400)


def ingredientExists(name: str, ingredients: list):
    for each_dict in ingredients:
        if each_dict['name'] == name:
            return True

    return False


def updateQuantity(name: str, ingredients: list, quantity: int):
    for each_dict in ingredients:
        if each_dict['name'] == name:
            each_dict['quantity'] += quantity
    return ingredients


class CombinedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated == False:
            return Response({'message': 'Not logged in'}, status=401)

        recipies_in_cart = ShoppingRecipeModel.objects.filter(user_id=self.request.user.id).values()

        # loop over each dictionary item in recipies_in_cart to get every ingredient for every recipe
        ingredients = []
        for i in range(0, len(recipies_in_cart)):

            recipeID = recipies_in_cart[i]['recipe_id_id']
            shoppingListServing = recipies_in_cart[i]['servings_num']
            original_recipe = RecipeModel.objects.get(id=recipeID)

            ingredients_data = IngredientModel.objects.filter(recipe_id=recipeID).values()

            for j in range(0, len(ingredients_data)):
                ingredient_name = ingredients_data[j]['name']
                ingredient_quantity = ingredients_data[j]['quantity']

                if ingredientExists(ingredient_name, ingredients):
                    if shoppingListServing == original_recipe.servings_num:
                        ingredients = updateQuantity(ingredient_name, ingredients, ingredient_quantity)

                    else:

                        """
                            Formula for calculating the quantity amount:

                            - divide the original recipe quantity by the original serving num to get a quantity value
                            equal to 1 serving.
                            - Then multiply this quantity for 1 serving amount by the number of servings the shopping
                            cart has.
                            *Note we always return an int and round up for decimals
                        """
                        original_quantity = IngredientModel.objects.get(recipe_id=original_recipe.id,
                                                                        name=ingredient_name).quantity / original_recipe.servings_num
                        updated_quantity = original_quantity * shoppingListServing
                        ingredients = updateQuantity(ingredient_name, ingredients, int(math.ceil(updated_quantity)))




                else:

                    if shoppingListServing == original_recipe.servings_num:
                        ingredients.append({
                            'name': ingredient_name,
                            'quantity': ingredient_quantity
                        })

                    else:

                        """
                            Formula for calculating the quantity amount:

                            - divide the original recipe quantity by the original serving num to get a quantity value
                            equal to 1 serving.
                            - Then multiply this quantity for 1 serving amount by the number of servings the shopping
                            cart has.
                        """
                        original_quantity = IngredientModel.objects.get(
                            recipe_id=original_recipe.id, name=ingredient_name).quantity / original_recipe.servings_num
                        updated_quantity = original_quantity * shoppingListServing

                        ingredients.append({
                            'name': ingredient_name,
                            'quantity': int(math.ceil(updated_quantity))
                        })

        return Response(ingredients)


class IndividualListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated == False:
            return Response({'message': 'Not logged in'}, status=401)

        result = []

        # All recipes this user has interacted with (created, liked, commented, favourited)
        recipies_in_cart = ShoppingRecipeModel.objects.filter(user_id=self.request.user.id).values()

        # Loop over each recipe and get all ingredients for it
        for i in range(0, len(recipies_in_cart)):

            recipeID = recipies_in_cart[i]['recipe_id_id']
            shoppingListServing = recipies_in_cart[i]['servings_num']
            original_recipe = RecipeModel.objects.get(id=recipeID)

            # List of ingredients for this specific recipe
            # Form: [
            #         {
            #         'Name':
            #          'Quantity':
            #           }, ... ,
            #         ]
            ingredients = []

            # All ingredients for this specific recipe
            ingredients_data = IngredientModel.objects.filter(recipe_id=recipeID).values()

            """
            Loop over all ingredients, if serving number for recipe in shopping cart is same as the recipe,
                just add the ingredient name and quantity.
                If not, re-calculate the quantity .
            """
            for j in range(0, len(ingredients_data)):
                ingredient_name = ingredients_data[j]['name']
                ingredient_quantity = ingredients_data[j]['quantity']

                if shoppingListServing == original_recipe.servings_num:

                    ingredients.append(
                        {
                            'name': ingredient_name,
                            'quantity': ingredient_quantity
                        }
                    )
                else:

                    """
                        Formula for calculating the quantity amount:

                        - divide the original recipe quantity by the original serving num to get a quantity value
                        equal to 1 serving.
                        - Then multiply this quantity for 1 serving amount by the number of servings the shopping
                        cart has.
                        *Note we always return an int and round up for decimals
                    """
                    original_quantity = IngredientModel.objects.get(recipe_id=original_recipe.id,
                                                                    name=ingredient_name).quantity / original_recipe.servings_num
                    updated_quantity = original_quantity * shoppingListServing
                    ingredients.append(
                        {
                            'name': ingredient_name,
                            'quantity': int(math.ceil(updated_quantity))
                        }
                    )

            result.append(
                {
                    'recipe_id': recipeID,
                    'name': original_recipe.name,
                    'servings_num': shoppingListServing,
                    'ingredients': ingredients
                }
            )

        return Response(result)


class UpdateServingSize(RetrieveAPIView, UpdateAPIView):
    serializer_class = ShoppingRecipeModelSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(ShoppingRecipeModel, recipe_id=self.kwargs['recipe_id'])


class RemoveFromCart(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        if request.user.is_authenticated == False:
            return Response({'message': 'Not logged in'}, status=401)

        recipe = get_object_or_404(ShoppingRecipeModel, recipe_id=kwargs['recipe_id'])

        recipe.delete()
        return Response({'message': 'Recipe has been deleted.'}, status=204)


class EmptyShoppingCart(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        if request.user.is_authenticated == False:
            return Response({'message': 'Not logged in'}, status=401)

        ShoppingRecipeModel.objects.filter(user_id=self.request.user.id).delete()

        return Response({"message": "Shopping Cart Cleared"})

class PublishedRecipesView(ListAPIView):
    serializer_class = RecipesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            RecipeModel.objects
            .filter(user_id=user)
            .order_by('-published_time')
        )

class FavouriteRecipesView(ListAPIView):
    serializer_class = RecipesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            RecipeModel.objects
            .filter(interactions__user_id=user, interactions__favourite=True)
            .prefetch_related('interactions__recipe_id')
            .order_by('-published_time')
        )

class RecentRecipesView(ListAPIView):
    serializer_class = RecipesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        interaction_recipe_ids = InteractionModel.objects.filter(user_id=user).values('recipe_id')
        my_recipes = RecipeModel.objects.filter(user_id=user)
        lst = RecipeModel.objects.filter(Q(id__in=interaction_recipe_ids) | Q(id__in=my_recipes)).distinct().order_by('-published_time')

        return lst

