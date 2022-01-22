from enum import Enum
from kiteconnect.connect import KiteConnect
import sys


class Tag(Enum):
    ENTRY = 'ENTRY'
    EXIT = 'EXIT'


class Exchange(Enum):
    NSE = KiteConnect.EXCHANGE_NSE
    NFO = KiteConnect.EXCHANGE_NFO


class OrderType(Enum):
    MARKET_ORDER_BUY = 'MARKET_ORDER_BUY'
    MARKET_ORDER_SELL = 'MARKET_ORDER_SELL'
    LIMIT_ORDER_BUY = 'LIMIT_ORDER_BUY'
    LIMIT_ORDER_SELL = 'LIMIT_ORDER_SELL'


class Trade:
    endpoints = {
        '/place/market_order/buy': OrderType.MARKET_ORDER_BUY,
        '/place/market_order/sell': OrderType.MARKET_ORDER_SELL,
        '/place/limit_order/buy': OrderType.LIMIT_ORDER_BUY,
        '/place/limit_order/sell': OrderType.LIMIT_ORDER_SELL
    }

    def __init__(self, trade: dict):
        self.order_type = self.endpoints[trade["endpoint"]]
        self.trading_symbol = trade["trading_symbol"]
        self.exchange = Exchange[trade["exchange"]]
        self.quantity = trade["quantity"]
        self.tag = Tag[trade["tag"]]
        self.entry_price = trade["entry_price"]
        self.price = trade["price"]
        self.type = trade["type"]
        self.max_quantity = trade.get("max_quantity", 10**9)
