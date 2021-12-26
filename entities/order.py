from entities.trade import Trade
from entities.trade import OrderType
from users.models import UserProfile
from enum import Enum


class Action(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class OrderResult:
    def __init__(self, orderid: int, order_type: Action):
        self.order_id = orderid
        self.order_type = order_type

    def __dict__(self):
        return {"orderid": self.order_id, "type": self.order_type}

    def toDict(self):
        return self.__dict__


'''
    OrderExecutor is used to execute the Market and Limit Orders
'''


class OrderExecutor:
    def __init__(self, userprofile: UserProfile):
        self.kite = userprofile.getKiteInstance()
        self.order_func = {
            OrderType.MARKET_ORDER_BUY: self.__placeMarketBuyOrder,
            OrderType.MARKET_ORDER_SELL: self.__placeMarketSellOrder,
            OrderType.LIMIT_ORDER_BUY: self.__placeLimitBuyOrder,
            OrderType.MARKET_ORDER_SELL: self.__placeLimitSellOrder
        }

    def placeOrderSync(self, trade: Trade) -> OrderResult:
        return self.order_func[trade.order_type](trade)

    def __placeMarketBuyOrder(self, trade: Trade) -> OrderResult:
        kite = self.kite
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=trade.exchange.value,
            tradingsymbol=trade.trading_symbol,
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=trade.quantity,
            product=kite.PRODUCT_NRML,
            order_type=kite.ORDER_TYPE_MARKET,
            validity=kite.VALIDITY_DAY,
        )
        return OrderResult(order_id, Action.BUY)

    def __placeMarketSellOrder(self, trade: Trade) -> OrderResult:
        kite = self.kite
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=trade.exchange.value,
            tradingsymbol=trade.trading_symbol,
            transaction_type=kite.TRANSACTION_TYPE_SELL,
            quantity=trade.quantity,
            product=kite.PRODUCT_NRML,
            order_type=kite.ORDER_TYPE_MARKET,
            validity=kite.VALIDITY_DAY,
        )
        return OrderResult(order_id, Action.SELL)

    def __placeLimitBuyOrder(self, tradingsymbol, exchange, price, quantity) -> OrderResult:
        kite = self.kite
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=quantity,
            product=kite.PRODUCT_NRML,
            order_type=kite.ORDER_TYPE_LIMIT,
            price=price,
            validity=kite.VALIDITY_DAY,
        )
        return OrderResult(order_id, Action.BUY)

    def __placeLimitSellOrder(self, tradingsymbol, exchange, price, quantity) -> OrderResult:
        kite = self.kite
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            transaction_type=kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            product=kite.PRODUCT_NRML,
            order_type=kite.ORDER_TYPE_LIMIT,
            price=price,
            validity=kite.VALIDITY_DAY,
        )
        return OrderResult(order_id, Action.SELL)
