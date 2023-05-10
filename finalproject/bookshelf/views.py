from .models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import render


def index(request):
    return render(request, 'bookshelf/index.html')


def user_is_superuser(user):
    return user.is_superuser


def loginview(request):
    if request.method == 'POST':
        username = request.POST['name']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('bookshelf:index'))
        else:
            return render(request, 'bookshelf/loginview.html')
    else:
        return render(request, 'bookshelf/loginview.html')


def logoutview(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('bookshelf:index'))


def registautilizador(request):
    if request.method == 'POST':

        user = User.objects.create_user(username=request.POST['name'], email=request.POST['email'],
                                        password=request.POST['password'], )
        login(request, user)
        role = request.POST['role']
        if role == "User":
            reader = Reader(user=user,image="media/user.png")
            reader.save()
        if role == "Publisher":
            pub = Publisher(user=user)
            pub.save()
        return HttpResponseRedirect(reverse('bookshelf:index'))
    else:
        return render(request, 'bookshelf/registautilizador.html')
