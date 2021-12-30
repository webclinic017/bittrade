from typing import Tuple
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
import json
from kiteconnect import KiteConnect
from constants.channels import USER_CHANNEL_KEY
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


class UserData(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.counter = 0
        self.key = ''

        self.user = None
        self.token = ''

    async def disconnect(self, code):
        db.delete(self.key)

    @database_sync_to_async
    def get_user(self, token):
        token = Token.objects.get(key=token)
        return token.user

    async def receive_json(self, content):
        # when auth token is received from the user end authenticate the user and save his token
        if self.user == None:
            if "authtoken" in content:
                # try to authenticate the user
                user = await self.get_user(content["authtoken"])

                if user == None:
                    await self.send_json({"error": "failed to authenticate user"})
                    return
                else:
                    self.user = user

                    # save the token
                    self.token = content["authtoken"]

                    # add the consumer to a group with "<token>-<USER_CHANNEL_KEY>"
                    await self.channel_layer.group_add(
                        self.token + USER_CHANNEL_KEY,
                        self.channel_name
                    )

                    return
            else:
                await self.send_json({"error":  "please provide a authtoken"})
                return

        data = content
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
        self.token = ''
        await self.accept()

    # error handler for the websocket
    async def on_error(self, error):
        await self.send_json({"error": str(error)})

    async def execute_safe(self, func, *args) -> Tuple[OrderResult, bool]:
        try:
            order = func(*args)
        except Exception as e:
            await self.on_error(e)
            return None, False
        else:
            return order, True

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

            # save the token for sending messages to the user consumer
            # here the token is helpful as a group name
            self.token = content["authtoken"]

            return
        elif self.bot == None:
            await self.send_json({"error": "please provide authtoken"})
            return

        trade = Trade(content)
        order, success = await self.execute_safe(self.bot.execTrade, trade)

        if success:
            await self.send_json(order.toDict())
