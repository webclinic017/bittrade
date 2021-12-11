from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
import json
from kiteconnect import KiteConnect
from entities.bot import TradeBot
from entities.order import OrderResult
from trade_notifier.utils import db
from entities.trade import Trade
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async

from trade_notifier.functions import (
    getMargins,
    getPnl,
    getPositions,
)
from users.models import UserProfile


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
        self.bot = None
        await self.accept()

    # error handler for the websocket
    async def on_error(self, error):
        await self.send_json({"error": str(error)})

    async def execute_safe(self, func, *args) -> OrderResult:
        try:
            order = func(*args)
        except Exception as e:
            await self.on_error(e)
            return
        else:
            return order

    @database_sync_to_async
    def get_user_profile(self, token):
        token = Token.objects.get(key=token)
        profile = UserProfile.objects.get(user=token.user)
        return profile

    async def receive_json(self, content):
        # authenticate the websocket first
        if self.bot == None and "authtoken" in content:
            profile = await self.get_user_profile(content["authtoken"])
            # creating the trade bot instance when authentication is successful
            self.bot = TradeBot(profile)
            return
        elif self.bot == None:
            await self.send_json({"error": "please provide authtoken"})
            return

        trade = Trade(content)
        order = await self.execute_safe(self.bot.execTrade, trade)

        if order:
            await self.send_json(order.toDict())
