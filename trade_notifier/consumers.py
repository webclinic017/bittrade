from channels.generic.websocket import AsyncWebsocketConsumer


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


class TradeNotifierStocks(Notifier):
    group_name = 'stocks'


class TradeNotifierIndex(Notifier):
    group_name = 'index'


class TradeNotifierIndexOption(Notifier):
    group_name = 'index_option'


class TradeNotifierIndexFutures(Notifier):
    group_name = 'index_futures'

class TradeNotifierStockOptions(Notifier):
    group_name = 'stock_options'


class TradeNotifierStockFutures(Notifier):
    group_name = 'stock_futures'


class IBKRStocks(Notifier):
    group_name = 'ibkr_stocks'

class IBKRIndex(Notifier):
    group_name = 'ibkr_index'

class IBKRStockOptions(Notifier):
    group_name = 'ibkr_stock_options'