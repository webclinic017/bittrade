from enum import Enum


class Tag(Enum):
    Entry = 'ENTRY'
    Exit = 'Exit'


class Exchange(Enum):
    NSE = 'NSE'
    NFO = 'NFO'


class Trade:
    endpoints = {
        '/place/market_order/buy': 'MARKET_ORDER_BUY',
        '/place/market_order/sell': 'MARKET_ORDER_SELL',
        '/place/limit_order/buy': 'LIMIT_ORDER_BUY',
        '/place/limit_order/sell': 'LIMIT_ORDER_SELL'
    }

    def __init__(self, trade: dict):
        self.endpoint = self.endpoints[trade["endpoint"]]
        self.trading_symbol = trade["trading_symbol"]
        self.exchange = Exchange[trade["exchange"]]
        self.quantity = trade["quantity"]
        self.tag = Tag[trade["tag"]]
        self.entry_price = trade["entry_price"]
        self.price = trade["price"]
        self.type = trade["type"]
        self.api_key = trade["api_key"]
        self.api_secret = trade["api_secret"]


class Order:
    def placeOrder(self, trade: Trade):
        raise NotImplementedError


class MarketOrder(Order):
    def placeOrder(self, trade: Trade):
        self.trade = trade
