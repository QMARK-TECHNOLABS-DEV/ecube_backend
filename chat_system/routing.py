from django.urls import path , include
from chat_system.consumers import ChatConsumer, ChatListConsumer
 
# Here, "" is routing to the URL ChatConsumer which 
# will handle the chat functionality.
websocket_urlpatterns = [
    path("chat/" , ChatConsumer.as_asgi()), 
    path("chat_list/" , ChatListConsumer.as_asgi()),
]
