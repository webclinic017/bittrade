from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
import json
from kiteconnect import KiteConnect
from trade_notifier.utils import db

from trade_notifier.functions import (
    market_buy_order,
    market_sell_order,
    limit_buy_order,
    limit_sell_order,
    validate_limit_api,
    validate_market_api,
    getMargins,
    getPnl,
    getPositions,
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


class InternationNotifier(Notifier):
    group_name = "international"


class UserData(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.counter = 0
        self.key = ''

    async def disconnect(self, code):
        db.delete(self.key)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if "api_key" in data and "access_token" in data and (data["api_key"] != None or data["access_token"] != None):
            self.key = data["api_key"]

            kite = KiteConnect(
                api_key=data["api_key"], access_token=data["access_token"])

            # hit the cache first
            data_ = db.get(data['api_key'])

            # cache miss has occured or there is an error in cache
            if (data_ != None and 'error' in json.loads(data_)["positions"]) or data == None or self.counter % 10 == 0:
                # reterive the positions and margins

                positions = await getPositions(kite)
                pnl = await getPnl(positions)
                margins = await getMargins(kite)
                data_ = {
                    "positions": positions,
                    "pnl": pnl,
                    "margins": margins
                }

                # store the result in the cache
                db.set(self.key, json.dumps(data_))
                # send the data to the user
                await self.send(text_data=json.dumps(data_))
                # increment the counter
                self.counter += 1
                return
            else:
                # cache hit has occured so send it to the user
                await self.send(data_.decode())
                # increment the counter
                self.counter += 1
                return


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

    async def perform_action(self, endpoint, data):
        err = None
        orderid = None

        try:
            kite = self.validators[endpoint](data)
        except AssertionError as e:
            return orderid, e

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

    async def receive_json(self, content):
        data = content
        # the api key is been passed correctly
        if ("api_key" in data) and ("access_token" in data) and (data["api_key"] != None and data["access_token"] != None):
            kite = KiteConnect(data["api_key"], data["access_token"])

            self.positions = await getPositions(kite)
            self.margins = await getMargins(kite)

            # if there is an error in positions or margins then return the error
            if "error" in self.positions or "error" in self.margins:
                await self.send_json({"error": "invalid api_key or access_token"})
                return

            if data['tag'] == 'ENTRY':
                # get the price
                price = data["price"] * data["quantity"]

                # check for the margins
                if price < self.margins["equity"]["available"]["live_balance"]:
                    # place the trade as the margins are sufficent

                    # try placing the order
                    orderid, err = await self.perform_action(data['endpoint'], data)

                    if err:
                        await self.send_json({"error": str(err)})
                    else:
                        # send the success message
                        await self.send_json({"type": "BUY", "orderid": orderid})

                    return
                else:
                    # send margins not sufficent error to the frontend
                    await self.send_json({"error": "margins are not sufficent"})
                    return

            if data['tag'] == 'EXIT':
                # check if position is present or not
                is_present = False

                for position in self.positions["net"]:
                    if position['tradingsymbol'] == data['trading_symbol'] and position['quantity'] > 0:
                        data['quantity'] = position['quantity']

                        if 'INDEX' in data['type']:
                            if 'BANKNIFTY' in data['trading_symbol']:
                                if data['quantity'] > 1200:
                                    data['quantity'] = 1200
                            else:
                                if data['quantity'] > 1800:
                                    data['quantity'] = 1800

                        is_present = True
                        break

                if is_present:
                    # execute the exit order if the position is present
                    orderid, err = await self.perform_action(data['endpoint'], data)

                    if err:
                        await self.send_json({"error": str(err)})
                    else:
                        await self.send_json({"type": "SELL", "orderid": orderid})

                    return
                else:
                    await self.send_json({'error': 'position not present'})
