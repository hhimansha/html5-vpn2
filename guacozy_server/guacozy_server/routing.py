from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from django.core.asgi import get_asgi_application

from .guacdproxy import GuacamoleConsumer

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # CHANGE FROM uuid TO int
            path('tunnelws/ticket/<uuid:ticket>/', GuacamoleConsumer.as_asgi()),
        ])
    ),
})