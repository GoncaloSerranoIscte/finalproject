from django.urls import include, path
from django.contrib import admin
urlpatterns = [
 path('bookshelf/', include('bookshelf.urls')),
 path('admin/', admin.site.urls),
]