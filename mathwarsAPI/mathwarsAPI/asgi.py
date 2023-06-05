"""
ASGI config for mathwarsAPI project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from game.consumers import RoomConsumer, MatchConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mathwarsAPI.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/room/<str:room_id>/', RoomConsumer.as_asgi()),
            path('ws/match/<str:room_id>/', MatchConsumer.as_asgi()),
        ])
    )
})
