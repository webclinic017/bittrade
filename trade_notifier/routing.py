from django.urls import path
from . import consumers
from . import views

websocket_urls = [
    path('ws/indian/trade', consumers.TradeNotifier.as_asgi()),
    path('ws/international/trade', consumers.InternationNotifier.as_asgi()),
    path('ws/users', consumers.UserData.as_asgi()),
    path('ws/orders', consumers.OrderConsumer.as_asgi()),
]

event_urls = [
    path('notifier/trade', views.TradeNotifier.as_asgi())
]
