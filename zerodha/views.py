from django.http import HttpResponseRedirect
from kiteconnect import KiteConnect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.utils.timezone import now
from entities.bot import TradeBot
from entities.trade import Trade
from rest_framework.exceptions import APIException
from rest_framework.throttling import UserRateThrottle
# return the request token to the user


def zerodha_auth(request):
    return HttpResponseRedirect(settings.FRONTEND_URL + "/request_token-zerodha/" + request.GET['request_token'])


# get the access token of zerodha api
class ZerodhaAccessToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        userprofile = request.user.userprofile

        kite = KiteConnect(api_key=userprofile.api_key)
        data_ = kite.generate_session(
            request.data['request_token'],
            userprofile.api_secret
        )

        request.user.userprofile.access_token = data_['access_token']
        request.user.userprofile.zerodha_last_login = now()
        request.user.userprofile.save()

        return Response({
            'access_token': data_['access_token']
        }, status=status.HTTP_200_OK)


class PnlAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        sum = 0
        kite = request.user.userprofile.kite
        positions = kite.positions()
        for pos in positions['net']:
            pnl = pos['pnl']
            sum += pnl

        return Response({
            'pnl': sum
        })


class MarginsAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        kite = request.user.userprofile.kite
        margins = kite.margins()

        return Response(margins, status=status.HTTP_200_OK)


class PositionsAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        kite = request.user.userprofile.kite
        positions = kite.positions()

        return Response(positions, status=status.HTTP_200_OK)


class ExecuteTradeThrottle(UserRateThrottle):
    scope = 'execute_trade'


class ExecuteTrade(APIView):
    permission_classes = [IsAuthenticated, ]
    throttle_classes = [ExecuteTradeThrottle, ]

    def post(self, request):
        profile = request.user.userprofile
        bot = TradeBot(profile)

        try:
            trade = Trade(request.data)
        except Exception as e:
            raise APIException(
                str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            order = bot.execTrade(trade)
        except Exception as e:
            raise APIException(
                str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(order.toJSON(), status=status.HTTP_200_OK)
