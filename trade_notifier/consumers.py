from channels.generic.websocket import AsyncJsonWebsocketConsumer
from trade_notifier.entities import Notifier
from constants.channels import USER_CHANNEL_KEY
from entities.bot import TradeBot
from entities.streamer import KiteStreamer
from entities.trade import Trade
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from users.models import UserProfile
import kiteconnect
import asyncio
import json
from asgiref.sync import async_to_sync
import threading


class TradeNotifier(Notifier):
    group_name = 'indian'


class InternationNotifier(Notifier):
    group_name = "international"


class UserData(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

        self.profile = None
        self.authtoken = ""
        self.streamer = None
        self.kite_ticker = None
        self.token_map = {}
        self.ticker_map = {}
        self.live_data = []

    async def disconnect(self, code):
        if self.kite_ticker:
            self.kite_ticker.close()

    @database_sync_to_async
    def get_user_profile(self, token):
        token = Token.objects.get(key=token)
        return UserProfile.objects.get(user=token.user)

    def on_connect(self, ws, response):
        print("[connected to websocket]")

        self.kite_ticker.subscribe([256265, 260105])
        self.kite_ticker.set_mode(
            self.kite_ticker.MODE_QUOTE, [256265, 260105])

    def on_ticks(self, ws, ticks):
        if self.token_map != {}:
            for idx in range(len(ticks)):
                ticks[idx]['tradingsymbol'] = self.token_map[ticks[idx]
                                                             ['instrument_token']]['tradingsymbol']

            self.live_data = json.loads(json.dumps(ticks, default=str))
            threading.Thread(target=async_to_sync(self.send_json), args=[{
                "type": "kite.tickers",
                "data": self.live_data
            }]).start()

        return True

    @database_sync_to_async
    def subscribe_tickers(self):
        tokens = set()
        strategies = self.profile.user.strategy_list.all()

        for strategy in strategies:
            # reterive all tickers here
            strategy_tickers = strategy.strategy_tickers.all()

            for strategy_ticker in strategy_tickers:
                tokens.add(
                    self.ticker_map[strategy_ticker.ticker]['instrument_token'])

        self.kite_ticker.subscribe(list(tokens))
        self.kite_ticker.set_mode(self.kite_ticker.MODE_QUOTE, list(tokens))

    def on_close(self, ws, code, reason):
        print(code, reason)

    async def stream_tickers(self, event):
        instruments = self.profile.kite.instruments()

        for instrument in instruments:
            self.token_map[instrument['instrument_token']
                           ] = instrument

            self.ticker_map[instrument['tradingsymbol']] = instrument

        # get all the tickers from the users strategies and subscribe to them
        self.kite_ticker = kiteconnect.KiteTicker(
            api_key=self.profile.api_key, access_token=self.profile.access_token)
        self.kite_ticker.on_close = self.on_close
        self.kite_ticker.on_connect = self.on_connect
        self.kite_ticker.on_ticks = self.on_ticks

        self.kite_ticker.connect(threaded=True)
        await asyncio.sleep(2)

        await self.subscribe_tickers()

    async def receive_json(self, content):
        # when auth token is received from the user end authenticate the user and save his token
        if "authtoken" in content:
            self.authtoken = content["authtoken"]

            self.profile = await self.get_user_profile(self.authtoken)
            await self.channel_layer.group_add(
                'USER_PROFILE_' + str(self.profile.id),
                self.channel_name
            )

            if self.profile.is_accesstoken_valid:
                await self.channel_layer.group_send(
                    'USER_PROFILE_' + str(self.profile.id),
                    {
                        "type": "stream.tickers"
                    }
                )

    async def update_user_profile(self, event):
        if not self.profile.is_accesstoken_valid:
            self.profile = await self.get_user_profile(self.authtoken)
            self.streamer = KiteStreamer(self.profile.kite)

            if self.kite_ticker == None:
                await self.channel_layer.group_send(
                    'USER_PROFILE_' + str(self.profile.id),
                    {
                        "type": "stream.tickers"
                    }
                )

    async def user_subscribe_tickers(self, event):
        if self.kite_ticker:
            tickers = event["message"]
            instrument_tokens = []

            for ticker in tickers:
                instrument_tokens.append(
                    self.ticker_map[ticker]['instrument_token']
                )

            self.kite_ticker.subscribe(instrument_tokens)
            self.kite_ticker.set_mode(
                self.kite_ticker.MODE_QUOTE, instrument_tokens)


class OrderConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.bot = None
        self.token = ''
        self.profile = None

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
            await self.send_json(order.toJSON())
        except Exception as e:
            await self.on_error(e)
            return
