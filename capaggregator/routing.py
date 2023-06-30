# chat/routing.py
from django.urls import re_path

from alert_subscription import consumers

websocket_urlpatterns = [
    re_path(r"ws/fetch_new_alert/(?P<alert_information>\w+)/$", consumers.ChatConsumer.as_asgi()),
]