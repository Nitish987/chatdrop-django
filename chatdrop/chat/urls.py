from django.urls import path
from . import views

urlpatterns = [
    path('v1/secret/canchat/', views.CanChat.as_view(), name='can-chat'),
    path('v1/secret/chat/message/', views.SecretChatMessage.as_view(), name='secret-chat-message-sender'),
    path('v1/normal/chat/message/', views.NormalChatMessage.as_view(), name='normal-chat-message-sender'),
    path('v1/chatgpt/chat/message/', views.ChatGptMessage.as_view(), name='chatgpt-ai'),
]