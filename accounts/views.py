from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login, update_session_auth_hash
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.generic.edit import CreateView
from accounts.models import User

# Create your views here.

def SignUpView(request):
    if request.method == 'GET':
        return HttpResponse('signupview get')

    elif request.method == 'POST':
        if User.objects.filter(username = request.POST['username']).exists():
            return HttpResponse('Username is already taken')
        if request.POST['password1'] != request.POST['password2']:
            return HttpResponse('Passwords do not match!')
        
        try:
            validate_email(request.POST['email'])
        except ValidationError:
            if (request.POST['email'] != ''):
                return HttpResponse('Enter a valid email address')
    
        user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'], email=request.POST['email'], first_name=request.POST['first_name'], last_name=request.POST['last_name'], phone_num=request.POST['phone_num'])
        user.save()
        return HttpResponseRedirect(f'/accounts/login')
    else:
        return HttpResponseNotAllowed(['GET, POST'])

def LoginView(request):
    if request.method == 'GET':
        return HttpResponse('get login', status=200)

    elif request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return HttpResponse('Username or Password is invalid.', status=300)
        
        auth_logout(request)
        auth_login(request, user)
        return HttpResponse('Login successful')
    else:
        return HttpResponseNotAllowed(['GET, POST'])

def LogoutView(request):
    if request.method == 'GET':
        auth_logout(request)
        return HttpResponseRedirect(f'/accounts/login')
    else:
        return HttpResponseNotAllowed(['GET'])

def EditProfileView(request):
    if request.user.is_authenticated == False:
            return HttpResponse('Not logged in', status=401)

    if request.method == 'GET':
        return HttpResponse('get edit', status=200)

    elif request.method == 'POST':
        if request.POST['password1'] != request.POST['password2']:
            return HttpResponse('Passwords do not match!')
        try:
            validate_email(request.POST['email'])
        except ValidationError:
            if (request.POST['email'] != ''):
                return HttpResponse('Enter a valid email address')
    
        request.user.first_name = request.POST['first_name']
        request.user.last_name = request.POST['last_name']
        request.user.email = request.POST['email']
        request.user.phone_num = request.POST['phone_num']
        
        if request.POST['password1']:
            request.user.set_password(request.POST['password1'])

        request.user.save()
        update_session_auth_hash(request, request.user)
        return HttpResponseRedirect(f'/accounts/login')
    else:
        return HttpResponseNotAllowed(['GET, POST'])