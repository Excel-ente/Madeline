from django.urls import include, path

from django.urls import path

urlpatterns = [
    path('', include('administracion.urls')),
]
