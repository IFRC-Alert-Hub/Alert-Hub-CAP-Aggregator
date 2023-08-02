from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reset_template', views.reset_template, name='reset_template'),
    path('get_alerts', views.get_alerts, name='dynamic_view'),
    path('feeds', views.get_feeds, name='feeds'),
]