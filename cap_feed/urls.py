from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pollingalerts/', views.polling_alerts, name = 'polling_alerts')
]
