import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from . import ws_urls
from account.authentication import WebSocketUserAuthenticationMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatdrop.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': WebSocketUserAuthenticationMiddleware(
        URLRouter(ws_urls.websocket_urlpatterns)
    )
})
