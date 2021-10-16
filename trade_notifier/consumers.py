from channels.generic.websocket import AsyncWebsocketConsumer
import json
from kiteconnect import KiteConnect


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

    async def receive(self, text_data):

        data = json.loads(text_data)

        if "api_key" in data and "access_token" in data:
            kite = KiteConnect(
                api_key=data["api_key"], access_token=data["access_token"])
            positions = await self.getPositions(kite)
            pnl = await self.getPnl(positions)

            data_ = {
                "positions": positions,
                "pnl": pnl
            }

            await self.send(text_data=json.dumps(data_))
