"""
ASGI config for network project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Ensure DJANGO_SETTINGS_MODULE is set properly based on your project name!
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "network.settings")

# Fetch ASGI application before importing dependencies that require ORM models.
django_asgi_app = get_asgi_application()


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from reactpy_django import REACTPY_WEBSOCKET_ROUTE
from planning import consumers  # Your consumers here

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    REACTPY_WEBSOCKET_ROUTE,  # ReactPy
                    re_path(r"ws/notifications/$", consumers.ChatConsumer.as_asgi()),  # Your consumers
                ]
            )
        ),
    }
)
