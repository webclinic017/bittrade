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

        self.profile = None
        self.token = ''
        self.streamer = None

    async def disconnect(self, code):
        db.delete(self.key)

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

    async def receive_json(self, content):
        # when auth token is received from the user end authenticate the user and save his token
        if self.profile == None:
            if "authtoken" in content:
                # try to authenticate the user
                profile = await self.get_user(content["authtoken"])

                if profile == None:
                    await self.send_json({"error": "failed to authenticate user"})
                    return
                else:
                    self.profile = profile
                    self.streamer = KiteStreamer(self.profile.kite)

                    # save the token
                    self.token = content["authtoken"]

                    # add the consumer to a group with "<token>-<USER_CHANNEL_KEY>"
                    await self.channel_layer.group_add(
                        str(self.profile.id) + USER_CHANNEL_KEY,
                        self.channel_name
                    )

                    return
            else:
                await self.send_json({"error":  "please provide a authtoken"})
                return

        try:
            margins = await self.streamer.get_margins_async()
            positions = await self.streamer.get_positions_async()
            pnl = await self.streamer.get_pnl_async()
        except kiteconnect.exceptions.TokenException as e:
            await self.send_json({
                "error": {
                    "status": True,
                    "message": str(e)
                }
            })

            return

        await self.send_json({
            "margins": margins.data,
            "positions": positions.data,
            "pnl": pnl,
        })

        return

    async def update_streamer(self, event):
        self.streamer = KiteStreamer(
            self.profile.kite
        )


class OrderConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.bot = None
        self.token = ''
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

        try:
            order = await self.bot.execTradeAsync(trade)
            print(order)
            await self.send_json(order.toJSON())
        except Exception as e:
            await self.on_error(e)
            return
