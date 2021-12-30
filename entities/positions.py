from typing import List


class Position:
    def __init__(self, position):
        self.tradingsymbol = position["tradingsymbol"]
        self.exchange = position["exchange"]
        self.instrument_token = position["instrument_token"]
        self.product = position["product"]
        self.quantity = position["quantity"]
        self.overnigth_quantity = position["overnight_quantity"]
        self.multiplier = position["multiplier"]
        self.average_price = position["average_price"]
        self.close_price = position["close_price"]
        self.last_price = position["last_price"]
        self.value = position["value"]
        self.pnl = position["pnl"]
        self.m2m = position["m2m"]
        self.unrealised = position["unrealised"]
        self.realised = position["realised"]
        self.buy_quantity = position["buy_quantity"]
        self.buy_price = position["buy_price"]
        self.buy_value = position["buy_value"]
        self.buy_m2m = position["buy_m2m"]
        self.day_buy_quantity = position["day_buy_quantity"]
        self.day_buy_price = position["day_buy_price"]
        self.day_buy_value = position["day_buy_value"]
        self.sell_quantity = position["sell_quantity"]
        self.sell_price = position["sell_price"]
        self.sell_value = position["sell_value"]
        self.sell_m2m = position["sell_m2m"]
        self.day_sell_quantity = position["day_sell_quantity"]
        self.day_sell_price = position["day_sell_quantity"]
        self.day_sell_value = position["day_sell_value"]
        self.sell_m2m = position["sell_m2m"]
        self.day_sell_price = position["day_sell_price"]


class Positions:
    def __init__(self, positions: dict):
        self.day: List[Position] = []

        for position in positions["day"]:
            self.day.append(
                Position(position)
            )

        self.net: List[Position] = []
        for position in positions["net"]:
            self.net.append(
                Position(position)
            )
