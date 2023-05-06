from django.urls import path,include
from django.contrib import admin


urlpatterns = [
    path('', admin.site.urls, name='admin'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]