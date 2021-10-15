from django.urls import path
from . import consumers

websocket_urls = [
    path('ws/indian/trade', consumers.TradeNotifier.as_asgi()),
    path('ws/users', consumers.UserData.as_asgi()),
]
