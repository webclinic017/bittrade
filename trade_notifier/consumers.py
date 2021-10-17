from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
import json
from kiteconnect import KiteConnect
from trade_notifier.rdb import db

from trade_notifier.functions import (
    market_buy_order,
    market_sell_order,
    limit_buy_order,
    limit_sell_order,
    validate_limit_api,
    validate_market_api,
)


class Notifier(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": 'broadcast.message',
                "message": text_data
            }
        )

    async def broadcast_message(self, event):
        await self.send(
            text_data=event['message']
        )


class TradeNotifier(Notifier):
    group_name = 'indian'


class UserData(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.counter = 0
        self.key = ''

    async def disconnect(self, code):
        db.delete(self.key)

    async def getPositions(self, kite: KiteConnect):
        try:
            positions = kite.positions()
            return positions
        except Exception as e:
            return {'error': str(e)}

    async def getPnl(self, positions):
        sum = 0
        if "error" in positions:
            return positions
        for pos in positions['net']:
            pnl = pos['pnl']
            sum += pnl
        return {"pnl": sum}

    async def getMargins(self, kite: KiteConnect):
        try:
            return kite.margins()
        except Exception as e:
            return {"error": str(e)}

    async def receive(self, text_data):
        print(text_data)

        data = json.loads(text_data)
        if "api_key" in data and "access_token" in data and (data["api_key"] != None or data["access_token"] != None):
            self.key = data["api_key"]
            data_ = db.get(data['api_key'])

            if data_ == None or self.counter % 6 == 0:
                kite = KiteConnect(
                    api_key=data["api_key"], access_token=data["access_token"])
                positions = await self.getPositions(kite)
                pnl = await self.getPnl(positions)
                margins = await self.getMargins(kite)

                data_ = {
                    "positions": positions,
                    "pnl": pnl,
                    "margins": margins
                }

                db.set(data["api_key"], json.dumps(data_))
                await self.send(text_data=json.dumps(data_))
            else:
                await self.send(text_data=data_.decode())

            self.counter += 1


class OrderConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.positions = None
        self.margins = None
        self.key = ""

        self.endpoints = {
            '/place/market_order/buy': market_buy_order,
            '/place/market_order/sell': market_sell_order,
            '/place/limit_order/buy': limit_buy_order,
            '/place/limit_order/sell': limit_sell_order
        }

        self.validators = {
            '/place/market_order/buy': validate_market_api,
            '/place/market_order/sell': validate_market_api,
            '/place/limit_order/buy': validate_limit_api,
            '/place/limit_order/sell': validate_limit_api
        }

        await self.accept()

    async def getPnl(self, positions):
        sum = 0
        if "error" in positions:
            return positions
        for pos in positions['net']:
            pnl = pos['pnl']
            sum += pnl
        return {"pnl": sum}

    async def getPositions(self, kite: KiteConnect):
        try:
            return kite.positions()
        except Exception as e:
            return {"error": str(e)}

    async def getMargins(self, kite: KiteConnect):
        try:
            return kite.margins()
        except Exception as e:
            return {"error": str(e)}

    async def perform_action(self, endpoint, data):
        err = None
        orderid = None
        kite = self.validators[endpoint](data)
        if 'limit' in endpoint:
            try:
                orderid = self.endpoints[endpoint](
                    kite, data['trading_symbol'], data['exchange'], data['quantity'], data['price'])
            except Exception as e:
                err = e
        else:
            try:
                orderid = self.endpoints[endpoint](
                    kite, data['trading_symbol'], data['exchange'], data['quantity'])
            except Exception as e:
                err = e
        return orderid, err

    async def receive(self, text_data=None):

        # load the json data from the raw text data
        data = json.loads(text_data)

        if "api_key" not in data or "access_token" not in data or data["api_key"] == None or data["access_token"] == None:
            await self.send_json({
                "error": "invalid api_key or access_token"
            })
        else:
            self.key = data["api_key"]
            kite = KiteConnect(data["api_key"], data["access_token"])
            flag = True

            if self.positions == None or self.margins == None or "error" in self.positions or "error" in self.margins:
                self.positions = await self.getPositions(kite)
                self.margins = await self.getMargins(kite)

                if "error" in self.positions or "error" in self.positions:
                    flag = False
                    await self.send_json({"error": {"positions": self.positions, "margins": self.margins}})

            if data['tag'] == 'ENTRY' and flag:
                # check the margins and then enter
                price = data["price"] * data["quantity"]
                if price < self.margins["equity"]["available"]["live_balance"]:
                    # place the order
                    orderid, err = await self.perform_action(data['endpoint'], data)
                    if err != None:
                        await self.send_json({"error": str(err)})
                    else:
                        await self.send_json({"orderid": orderid, "type": "BUY"})
                        self.margins = await self.getMargins(kite)
                else:
                    await self.send_json({"error": "insufficent margins"})

            if data['tag'] == 'EXIT' and flag:
                # check the positions and then exit
                position = None

                # print(text_data)

                for i in range(len(self.positions["net"])):
                    if self.positions["net"][i]['tradingsymbol'] == data['trading_symbol'] and self.positions["net"][i]['quantity'] > 0:
                        position = self.positions["net"][i]

                if position == None:
                    await self.send_json({"error": "position not present"})
                else:
                    # place the exit order
                    data["quantity"] = position["quantity"]
                    orderid, err = await self.perform_action(data['endpoint'], data)
                    if err != None:
                        await self.send_json({"error": str(err)})
                    else:
                        await self.send_json({"orderid": orderid, "type": "SELL"})
                        self.positions = await self.getPositions(kite)

            pnl = await self.getPnl(self.positions)
            data_ = {
                "positions": self.positions,
                "margins": self.margins,
                "pnl": pnl
            }
            db.set(data["api_key"], json.dumps(data_))

    async def disconnect(self, code):
        db.delete(self.key)
