from django.urls import path
from . import consumers

websocket_urls = [
    path('ws/stocks_notifications/', consumers.TradeNotifierStocks.as_asgi()),
    path('ws/index_notifications/', consumers.TradeNotifierIndex.as_asgi()),
    path('ws/stock_opt_notifications/',
         consumers.TradeNotifierStockOptions.as_asgi()),
    path('ws/stock_fut_notifications/',
         consumers.TradeNotifierStockFutures.as_asgi()),
    path('ws/ibkr_stocks/', consumers.IBKRStocks.as_asgi()),
    path('ws/ibkr_index/', consumers.IBKRIndex.as_asgi()),
]
