from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reset_cached_fragment', views.reset_template, name='reset_cached_fragment'),
    path('get_alerts', views.get_alerts, name='dynamic_view'),
]
