"""
ASGI config for capaggregator project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from asgiref.wsgi import WsgiToAsgi
from django.core.asgi import get_asgi_application

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator
from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv
import django
import capaggregator.routing

if 'WEBSITE_HOSTNAME' not in os.environ:
    load_dotenv(".env")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capaggregator.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capaggregator.production')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": OriginValidator(
        AuthMiddlewareStack(URLRouter(capaggregator.routing.websocket_urlpatterns)),
        ["wss://localhost", "wss://https://backend-develop.scm.azurewebsites.net/"]
    ),
})

