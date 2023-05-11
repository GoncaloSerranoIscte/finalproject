from django.urls import include, path
from . import views

# (. significa que importa views da mesma directoria)
app_name = 'bookshelf'

urlpatterns = [
    path("", views.index, name="index"),

    path("loginview", views.loginview, name='loginview'),

    path("logoutview", views.logoutview, name='logoutview'),

    path("adicionarlivro", views.adicionarlivro, name='adicionarlivro'),

    path("verlivros", views.verlivros, name='verlivros'),

    path("<int:book_id>", views.detalhe, name='detalhe'),

    path("<int:book_id>/adicionarlista", views.adicionarlista, name='adicionarlista'),

    path("verlivrosReaded", views.verlivrosReaded, name='verlivrosReaded'),

    path("verlivrosToRead", views.verlivrosToRead, name='verlivrosToRead'),

    path("verlivrosReading", views.verlivrosReading, name='verlivrosReading'),

]
