from trade_notifier.entities import SseConsumer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio
import json


class TradeNotifier(SseConsumer):
    group_name = 'indian_stocks'

    async def handle_stocks(self, event):
        payload = 'data: %s\n\n' % json.dumps(event["message"])

        await self.send_body(payload.encode('utf-8'), more_body=True)


class PublishTrade(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def post(self, request):
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            'indian_stocks',
            {
                "type": "handle.stocks",
                "message": request.data
            }
        )

        return Response(status=status.HTTP_200_OK)
