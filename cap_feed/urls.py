from django.urls import path

from . import views
from django.contrib import admin
urlpatterns = [
    path('', views.index, name='index'),
    path('pollingalerts/', views.polling_alerts, name = 'polling_alerts')
]
