"""
ASGI config for bittrade project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bittrade.settings')
django_app = get_asgi_application()


from django.conf.urls import url
from trade_notifier.routing import websocket_urls, event_urls
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


application = ProtocolTypeRouter({
    'http': URLRouter([
        url(r'^events/', AuthMiddlewareStack(URLRouter(
            event_urls
        ))),
        url(r'', django_app),
    ]),
    'websocket': AuthMiddlewareStack(URLRouter(
        websocket_urls
    )),
})
