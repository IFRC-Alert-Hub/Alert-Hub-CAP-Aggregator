from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cache_all_data', views.cache_all_alert, name='cache_all_data'),
    path('get_all_data', views.get_cached_data, name='get_all_cached_data'),
]
