# guacozy_server/guacozy_server/asgi.py
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guacozy_server.settings')
django.setup()

# Import consumers from the correct path - guacdproxy directory
from guacozy_server.guacdproxy.consumers import GuacamoleConsumer

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('tunnelws/ticket/<uuid:ticket>/', GuacamoleConsumer.as_asgi()),
        ])
    ),
})