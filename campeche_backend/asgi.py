"""
ASGI config for campeche_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from notifications.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campeche_backend.settings")

# Django ASGI application (para HTTP)
django_asgi_app = get_asgi_application()

from notifications.middleware import JWTAuthMiddleware
# ProtocolTypeRouter combina HTTP + WebSocket
application = ProtocolTypeRouter({
    # Envia a las peticiones HTTP de django con normalidad
    "http": get_asgi_application(),
    # Utiliza WEBSOcKET Envolviendo en midelwore para obtener al usuario logeado
    "websocket": JWTAuthMiddleware(
        JWTAuthMiddleware(
            # Utiliza las URLS WS
            URLRouter(websocket_urlpatterns)
        )
    ),
})