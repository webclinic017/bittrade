from trade_notifier.entities import SseConsumer
import asyncio
import json


class TradeNotifier(SseConsumer):
    group_name = 'indian_stocks'

    async def handle_stocks(self, event):
        payload = 'data: %s\n\n' % json.dumps(event["message"])

        await self.send_body(payload.encode('utf-8'), more_body=True)
