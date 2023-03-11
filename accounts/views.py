from django.shortcuts import render
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login, update_session_auth_hash
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User, ShoppingRecipeModel
from accounts.serializers import UserDetailSerializer, UserLoginSerializer, UserEditSerializer, \
    AllShoppingListSerializer

# Create your views here.
from recipes.models import IngredientModel


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

    def post(self, request):
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


def updateQuantity(name: str, ingredients: list, quauntity: int):
    for each_dict in ingredients:
        if each_dict['name'] == name:
            each_dict['quantity'] += quauntity
    return ingredients


class CombinedListView(APIView):
    serializer_class = AllShoppingListSerializer

    # def get_queryset(self):
    #     return ShoppingRecipeModel.objects.filter(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        recipies_in_cart = ShoppingRecipeModel.objects.filter(user_id=self.request.user.id).values()
        # print(recipies_in_cart)
        # return Response(recipies_in_cart)

        # loop over each dictionary item in recipies_in_cart to get recipe_id
        ingredients = []
        for i in range(0, len(recipies_in_cart)):
            # get recipe_id_id
            recipeID = recipies_in_cart[i]['recipe_id_id']
            data = IngredientModel.objects.filter(recipe_id=recipeID).values()
            # print(data)
            for j in range(0, len(data)):
                ingredient_name = data[j]['name']
                ingredient_quantity = data[j]['quantity']

                if ingredientExists(ingredient_name, ingredients):
                    ingredients = updateQuantity(ingredient_name, ingredients, ingredient_quantity)
                else:
                    ingredients.append({
                        'name': ingredient_name,
                        'quantity': ingredient_quantity
                    })

        # print(ingredients)
        return Response(ingredients)


