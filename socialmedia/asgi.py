"""
ASGI config for socialmedia project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialmedia.settings')
django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from chattingapp import routing  
# application = get_asgi_application()

application = ProtocolTypeRouter({
    
    "http": get_asgi_application(),
    "websocket": (
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
