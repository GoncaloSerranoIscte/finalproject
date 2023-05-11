from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from .models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string


def index(request):
    url = "index"
    context = {'url': url}
    return render(request, 'bookshelf/index.html', context)


def user_is_superuser(user):
    return user.is_superuser


def loginview(request):
    if request.method == 'POST':
        if 'Log in' in request.POST:
            username = request.POST['name']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('bookshelf:index'))
            else:
                return render(request, 'bookshelf/loginview.html')
        elif 'Register' in request.POST:
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
        url = "loginview"
        context = {'url': url}
        return render(request, 'bookshelf/loginview.html', context)


def logoutview(request):
    if request.user.is_authenticated:
        logout(request)
    url = "index"
    context = {'url': url}
    return HttpResponseRedirect(reverse('bookshelf:index'), context)


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
    livros = Book.objects.all()
    order_by = request.GET.get('order_by', '-pub_data')
    for l in livros:
        l.updateRating()

    if order_by == 'name':
        livros = livros.order_by('name')
    elif order_by == '-name':
        livros = livros.order_by('-name')
    elif order_by == 'autor':
        livros = livros.order_by('autor')
    elif order_by == '-autor':
        livros = livros.order_by('-autor')
    elif order_by == 'pub_data':
        livros = livros.order_by('pub_data')
    elif order_by == '-pub_data':
        livros = livros.order_by('-pub_data')
    elif order_by == 'rating':
        livros = livros.order_by('rating')
    elif order_by == '-rating':
        livros = livros.order_by('-rating')

    context = {'url': url, 'livros': livros, 'order_by': order_by}
    return render(request, 'bookshelf/verlivros.html', context)


def detalhe(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        raise Http404("The Book doesnt exist")
    a = None
    exists = 0
    for c in Connect.objects.all():
        if c.book.id == book_id and c.reader.user.username == request.user.username:
            a = c
            exists = 1
    return render(request, 'bookshelf/detalhe.html', {'book': book, 'connect': a})


def adicionarlista(request, book_id):
    c1 = None
    book = Book.objects.get(pk=book_id)
    if 'lista' in request.POST:
        print("changing list")
        opc = request.POST['opcao']
        book = Book.objects.get(pk=book_id)
        shelf = "nop"
        if opc == "1":
            shelf = "to read"
        elif opc == "2":
            shelf = "reading"
        elif opc == "3":
            shelf = "readed"
        print(shelf)
        c1 = None
        exists = 0
        for c in Connect.objects.all():
            if c.book.id == book_id and c.reader.user.username == request.user.username:
                c.shelf = shelf
                c.save()
                c1 = c
                print("changing to " + shelf)
                exists = 1
        if exists == 0:
            c1 = Connect(reader=request.user.reader, book=book, shelf=shelf)
            c1.save()
            print("creating " + shelf)
    if 'rate' in request.POST:
        print("changing rate")
        opc = request.POST.get('rate')
        rati = -1
        if int(opc) == 4:
            rati = 1
            print(1)
        elif int(opc) == 5:
            rati = 2
            print(2)
        elif int(opc) == 6:
            rati = 3
            print(3)
        elif int(opc) == 7:
            rati = 4
            print(4)
        elif int(opc) == 8:
            rati = 5
            print(5)
        for c in Connect.objects.all():
            if c.book.id == book_id and c.reader.user.username == request.user.username:
                c.rating = rati
                c.save()
                c1 = c
                book.updateRating()

    return render(request, 'bookshelf/detalhe.html', {'book': book, 'connect': c1})


def verlivrosToRead(request):
    livros = Book.objects.all()
    for c in Connect.objects.all():
        if c.shelf != "to read" or c.reader.user.username != request.user.username:
            livros.exclude(id=c.book.id)
    url = "verlivrosToRead"

    order_by = request.GET.get('order_by', '-pub_data')
    if len(livros) != 0:
        for l in livros:
            l.updateRating()

    if order_by == 'name':
        livros = livros.order_by('name')
    elif order_by == '-name':
        livros = livros.order_by('-name')
    elif order_by == 'autor':
        livros = livros.order_by('autor')
    elif order_by == '-autor':
        livros = livros.order_by('-autor')
    elif order_by == 'pub_data':
        livros = livros.order_by('pub_data')
    elif order_by == '-pub_data':
        livros = livros.order_by('-pub_data')
    elif order_by == 'rating':
        livros = livros.order_by('rating')
    elif order_by == '-rating':
        livros = livros.order_by('-rating')

    context = {'url': url, 'livros': livros, 'order_by': order_by}
    return render(request, 'bookshelf/verlivrosToRead.html', context)

def verlivrosReading(request):
    print("oioiioahahahaha")
    livros = []
    for c in Connect.objects.all():
        if c.shelf == "reading" or c.reader.user.username == request.user.username:
            livros.append(c.book)
    url = "verlivrosReading"

    order_by = request.GET.get('order_by', '-pub_data')
    if len(livros) != 0:
        for l in livros:
            print("oioi")
            l.updateRating()

    if order_by == 'name':
        livros = livros.order_by('name')
    elif order_by == '-name':
        livros = livros.order_by('-name')
    elif order_by == 'autor':
        livros = livros.order_by('autor')
    elif order_by == '-autor':
        livros = livros.order_by('-autor')
    elif order_by == 'pub_data':
        livros = livros.order_by('pub_data')
    elif order_by == '-pub_data':
        livros = livros.order_by('-pub_data')
    elif order_by == 'rating':
        livros = livros.order_by('rating')
    elif order_by == '-rating':
        livros = livros.order_by('-rating')

    context = {'url': url, 'livros': livros, 'order_by': order_by}
    return render(request, 'bookshelf/verlivrosReading.html', context)

def verlivrosReaded(request):
    livros = Book.objects.all()
    for c in Connect.objects.all():
        if c.shelf != "readed" or c.reader.user.username != request.user.username:
            livros.exclude(id=c.book.id)
    url = "verlivrosReaded"

    order_by = request.GET.get('order_by', '-pub_data')
    if len(livros) != 0:
        for l in livros:
            l.updateRating()

    if order_by == 'name':
        livros = livros.order_by('name')
    elif order_by == '-name':
        livros = livros.order_by('-name')
    elif order_by == 'autor':
        livros = livros.order_by('autor')
    elif order_by == '-autor':
        livros = livros.order_by('-autor')
    elif order_by == 'pub_data':
        livros = livros.order_by('pub_data')
    elif order_by == '-pub_data':
        livros = livros.order_by('-pub_data')
    elif order_by == 'rating':
        livros = livros.order_by('rating')
    elif order_by == '-rating':
        livros = livros.order_by('-rating')

    context = {'url': url, 'livros': livros, 'order_by': order_by}
    return render(request, 'bookshelf/verlivrosReaded.html', context)