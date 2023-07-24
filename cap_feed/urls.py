from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reset_cached_fragment', views.reset_cached_fragment, name='reset_cached_fragment'),
    path('dynamic_view', views.dynamic_view, name='dynamic_view'),
]
