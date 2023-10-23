from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from chat_system import routing
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    ),
})
