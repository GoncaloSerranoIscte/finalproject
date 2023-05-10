from django.utils import timezone

from .models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage


def index(request):
    url = "index"
    context = {'url': url}
    return render(request, 'bookshelf/index.html', context)


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
        url = "loginview"
        context = {'url': url}
        return render(request, 'bookshelf/loginview.html',context)


def logoutview(request):
    if request.user.is_authenticated:
        logout(request)
    url = "index"
    context = {'url': url}
    return HttpResponseRedirect(reverse('bookshelf:index'), context)


def registautilizador(request):
    if request.method == 'POST':

        user = User.objects.create_user(username=request.POST['name'], email=request.POST['email'],
                                        password=request.POST['password'], )
        login(request, user)
        role = request.POST['role']
        if role == "User":
            reader = Reader(user=user, image="media/user.png")
            if request.FILES['myfile']:
                myfile = request.FILES['myfile']
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
                reader.image = uploaded_file_url.split('/static/', 1)[1]
            reader.save()
        if role == "Publisher":
            pub = Publisher(user=user)
            if request.FILES['myfile']:
                myfile = request.FILES['myfile']
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
                pub.image = uploaded_file_url.split('/static/', 1)[1]
            pub.save()
        return HttpResponseRedirect(reverse('bookshelf:index'))
    else:
        url = "registautilizador"
        context = {'url': url}
        return render(request, 'bookshelf/registautilizador.html', context)


def adicionarlivro(request):
    if request.method == 'POST':
        try:
            description = request.POST.get("description")
            name = request.POST.get("name")
            pub_data = request.POST.get("pub_data")
            autor = request.POST.get("authors")
        except KeyError:
            return render(request, 'bookshelf/adicionarlivro.html')
        if description:
            book = Book(description=description, name=name, autor=autor,
                        publisher=request.user.publisher, image="media/user.png")
            if pub_data is not None:
                book.pub_data = pub_data
            else:
                book.pub_data = timezone.now()  # set the default value to the current time if no value is provided
            if request.FILES['myfile'] is not None:
                myfile = request.FILES['myfile']
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
                book.image = uploaded_file_url.split('/static/', 1)[1]
            book.save()
            return HttpResponseRedirect(reverse('bookshelf:index'))
        else:
            return HttpResponseRedirect(reverse('bookshelf:adicionarlivro'))
    else:
        url = "adicionarlivro"
        context = {'url': url}
        return render(request, 'bookshelf/adicionarlivro.html', context)


def verlivros(request):
    url = "verlivros"
    livros = Book.objects.order_by('-pub_data')
    context = {'url': url , 'livros' : livros}
    return render(request, 'bookshelf/verlivros.html', context)