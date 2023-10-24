from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/v1/secret/chat/<str:uid>/', consumers.SecretChatConsumer.as_asgi()),
]