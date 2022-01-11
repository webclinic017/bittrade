'''
    TradeBot class is used for entering and exiting the Trades

    ENTRY : it checks for the margins and then enters
    EXIT  : it checks the positions and then exits
'''
from entities.order import OrderExecutor, OrderResult
from users.models import UserProfile
from entities.trade import Tag, Trade


class InsufficentMarginsException(Exception):
    def __init__(self):
        super().__init__("Insufficent Margins")


class NoPositionFoundException(Exception):
    def __init__(self):
        super().__init__("No Position Found")


class TradeBot(OrderExecutor):
    def __init__(self, userprofile: UserProfile):
        super().__init__(userprofile)
        self.exec_func = {
            Tag.ENTRY: self.__enterTrade,
            Tag.EXIT: self.__exitTrade
        }

    def __enterTrade(self, trade: Trade) -> OrderResult:
        # check for the margins and then execute the trade
        price = trade.price * trade.quantity

        if price < self.streamer.margins.equity.available.live_balance:
            order = self.placeOrderSync(trade)
        else:
            raise InsufficentMarginsException

        return order

    def __exitTrade(self, trade: Trade) -> OrderResult:
        # search for the trade in the positions and then exit
        is_present = False
        for position in self.streamer.positions.net:
            if position.tradingsymbol == trade.trading_symbol and position.quantity > 0:
                is_present = True
                trade.quantity = position.quantity
                break

        if is_present:
            order = self.placeOrderSync(trade)
        else:
            raise NoPositionFoundException

        return order

    def execTrade(self, trade: Trade) -> OrderResult:
        return self.exec_func[trade.tag](trade)

    async def execTradeAsync(self, trade: Trade) -> OrderResult:
        return self.execTrade(trade)
