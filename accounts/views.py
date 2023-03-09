from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login, update_session_auth_hash
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.generic.edit import CreateView
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import User
from accounts.serializers import UserDetailSerializer, UserLoginSerializer, UserEditSerializer

# Create your views here.
class SignUpView(CreateAPIView):
    def post(self, request):
        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                validate_email(request.data.get('email'))
            except ValidationError:
                return Response({'message': 'enter a valid email'}, status=400)
            if request.data.get('password') != request.data.get('password2'):
                return Response({'message': 'passwords do not match'}, status=400)
            serializer.create(request.data)
            return Response({'message': 'signup success'}, status=200)
        print(serializer.errors)

        if User.objects.filter(username = request.POST['username']).exists():
            return Response({'message': 'username is already taken'}, status=400)
        return Response({'message': 'serializer is invalid!'}, status=400)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is None:
                return Response({'message': 'Username or password is invalid'}, status=400)
            auth_logout(request)
            auth_login(request, user)
            return Response({'message': 'logged in as ' + user.username }, status=200)
        print(serializer.errors)
        return Response({'message': 'serializer is invalid!'}, status=400)

class LogoutView(APIView):
    def get(self, request):
        auth_logout(request)
        return Response({'message': 'logged out'}, status=200)

class EditProfileView(APIView):

    def post(self, request):
        if request.user.is_authenticated == False:
            return Response({'message': 'Not logged in'}, status=401)

        serializer = UserEditSerializer(data=request.data)
        if serializer.is_valid():
            
            if request.POST['password'] != request.POST['password2']:
                return Response({'message': 'Passwords do not match'}, status=400)
            try:
                validate_email(request.POST['email'])
            except ValidationError:
                if (request.POST['email'] != ''):
                    return Response({'message': 'Enter a valid email address'}, status=400)
        
            request.user.first_name = request.POST['first_name']
            request.user.last_name = request.POST['last_name']
            request.user.email = request.POST['email']
            request.user.phone_num = request.POST['phone_num']
            request.user.avatar = request.FILES['avatar']

            if request.POST['password']:
                request.user.set_password(request.POST['password'])

            request.user.save()
            update_session_auth_hash(request, request.user)
            return Response({'message': 'edited user '+ request.user.username + "'s information"}, status=200)
        print(serializer.errors)
        return Response({'message': 'serializer is invalid!'}, status=400)
