from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Reader(models.Model):
    image = models.CharField(max_length=500, default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Publisher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.CharField(max_length=500, default="")


class Book(models.Model):
    pub_data = models.DateTimeField('data depublicacao')
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    autor = models.CharField(max_length=500)
    image = models.CharField(max_length=500, default="")
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)


class connect(models.Model):
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(default=-1)
    shelf = models.CharField(max_length=50)
