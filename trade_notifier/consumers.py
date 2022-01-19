from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from constants.channels import USER_CHANNEL_KEY
from entities.bot import TradeBot
from entities.streamer import KiteStreamer
from trade_notifier.utils import db
from entities.trade import Trade
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from users.models import UserProfile
import kiteconnect
import asyncio
import json
from asgiref.sync import async_to_sync
import threading


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

        self.profile = None
        self.token = ''

        self.streamer = None
        self.token_map = {}

        self.group_name = ''

        self.kite_ticker = None
        self.live_data = []

        self.margins = None
        self.positions = None
        self.pnl = 0

    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        if self.kite_ticker:
            self.kite_ticker.close()

    async def on_error(self, error):
        await self.send_json({"error": str(error)})
        return

    async def execute_safe(self, func, *args) -> bool:
        try:
            func(*args)
        except Exception as e:
            self.on_error(e)
            return False
        else:
            return True

    @database_sync_to_async
    def get_user(self, token):
        token = Token.objects.get(key=token)
        return UserProfile.objects.get(user=token.user)

    def on_connect(self, ws, response):
        print("[connecting to websocket]")

        self.kite_ticker.subscribe([256265, 260105])
        self.kite_ticker.set_mode(
            self.kite_ticker.MODE_QUOTE, [256265, 260105])

    def on_ticks(self, ws, ticks):
        if self.token_map != {}:
            for idx in range(len(ticks)):
                ticks[idx]['tradingsymbol'] = self.token_map[ticks[idx]
                                                             ['instrument_token']]['tradingsymbol']

            self.live_data = json.loads(json.dumps(ticks, default=str))

        if self.margins and self.positions:
            threading.Thread(target=async_to_sync(self.send_json), args=[{
                "margins": self.margins.data,
                "positions": self.positions.data,
                "pnl": self.pnl,
                "tickers": self.live_data
            }]).start()

        return True

    def on_error(self, code, reason):
        print(f"error - {code} <> {reason}")

    async def receive_json(self, content):
        # when auth token is received from the user end authenticate the user and save his token
        if self.profile == None:
            if "authtoken" in content:
                # try to authenticate the user
                profile = await self.get_user(content["authtoken"])
                self.token = content["authtoken"]

                if profile == None:
                    await self.send_json({"error": "failed to authenticate user"})
                    return
                else:
                    self.profile = profile
                    self.streamer = KiteStreamer(self.profile.kite)
                    self.group_name = str(self.profile.id) + USER_CHANNEL_KEY

                    if self.profile.is_accesstoken_valid:
                        # create a KiteTicker object
                        self.kite_ticker = kiteconnect.KiteTicker(
                            api_key=self.profile.api_key, access_token=self.profile.access_token)

                        self.kite_ticker.on_connect = self.on_connect
                        self.kite_ticker.on_ticks = self.on_ticks
                        self.kite_ticker.on_error = self.on_error
                        self.kite_ticker.connect(threaded=True)

                        self.token_map = {}

                        kite = self.profile.kite
                        for instrument in kite.instruments():
                            self.token_map[instrument['instrument_token']
                                           ] = instrument

                    # save the token
                    self.token = content["authtoken"]

                    # add the consumer to a group with "<token>-<USER_CHANNEL_KEY>"
                    await self.channel_layer.group_add(
                        self.group_name,
                        self.channel_name
                    )
            else:
                await self.send_json({"error":  "please provide a authtoken"})
                return

        if self.streamer is None:
            return

        if self.margins == None or self.positions == None:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "update.user.data",
                    "message": ""
                }
            )

        return

    async def update_streamer(self, event):
        print('updating the streamer....')
        self.profile = await self.get_user(self.token)
        self.streamer = KiteStreamer(self.profile.kite)

        if self.kite_ticker != None:
            self.kite_ticker.stop()
            self.kite_ticker = None

        self.kite_ticker = kiteconnect.KiteTicker(
            api_key=self.profile.api_key, access_token=self.profile.access_token)

        self.kite_ticker.on_connect = self.on_connect
        self.kite_ticker.on_ticks = self.on_ticks
        self.kite_ticker.on_error = self.on_error

        self.kite_ticker.connect(threaded=True)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "update.user.data",
                "message": ""
            }
        )

    async def update_user_data(self, event):
        print('updating the user data....')

        try:
            self.margins = await self.streamer.get_margins_async()
            self.positions = await self.streamer.get_positions_async()
            self.pnl = await self.streamer.get_pnl_async()
        except kiteconnect.exceptions.TokenException as e:
            await self.send_json({
                "error": {
                    "status": True,
                    "message": str(e)
                }
            })

            return


class OrderConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.bot = None
        self.token = ''
        self.profile = None
        self.user_data_group = ''

        await self.accept()

    # error handler for the websocket
    async def on_error(self, error):
        print(error)
        await self.send_json({"error": str(error)})

    @database_sync_to_async
    def get_user_profile(self, token):
        token = Token.objects.get(key=token)
        profile = UserProfile.objects.get(user=token.user)
        return profile

    async def receive_json(self, content):
        # authenticate the websocket first
        if self.bot == None and "authtoken" in content:
            self.profile = await self.get_user_profile(content["authtoken"])
            self.user_data_group = str(self.profile.id) + USER_CHANNEL_KEY
            # creating the trade bot instance when authentication is successful
            self.bot = TradeBot(self.profile)

            # save the token for sending messages to the user consumer
            # here the token is helpful as a group name
            self.token = content["authtoken"]

            return
        elif self.bot == None:
            await self.send_json({"error": "please provide authtoken"})
            return

        trade = Trade(content)

        try:
            order = await self.bot.execTradeAsync(trade)
            print(order)
            await self.send_json(order.toJSON())

            await self.channel_layer.group_send(
                self.user_data_group,
                {
                    "type": "update.user.data",
                    "message": ""
                }
            )
        except Exception as e:
            await self.on_error(e)
            return
