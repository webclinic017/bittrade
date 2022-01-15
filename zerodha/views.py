from django.http import HttpResponseRedirect
from kiteconnect import KiteConnect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .functions import (
    check_validity,
    limit_buy_order,
    limit_sell_order,
    market_buy_order,
    market_sell_order,
    check_authorization,
    validate_order
)
from rest_framework import generics
from zerodha.pagenation import OrdersPagenation
from django.conf import settings
import datetime
from channels.layers import get_channel_layer
from constants.channels import USER_CHANNEL_KEY
from asgiref.sync import async_to_sync
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
        request.user.userprofile.zerodha_last_login = datetime.datetime.now()
        request.user.userprofile.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            str(request.user.userprofile.id) + USER_CHANNEL_KEY,
            {
                "type": "update.streamer",
                "message": ""
            }
        )
        return Response({
            'access_token': data_['access_token']
        }, status=status.HTTP_200_OK)


# get zerodha login url
class ZerodhaLoginUrl(APIView):
    def post(self, request):
        assert 'api_key' in request.data
        kite = KiteConnect(
            api_key=request.data['api_key']
        )

        return Response({
            'login_url': kite.login_url()
        })


# market orders

class MarketOrderBuy(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = request.data
        try:
            kite_ = request.user.userprofile.kite

            if data['exchange'] == 'NFO':
                exchange = kite_.EXCHANGE_NFO
            elif data['exchange'] == 'NSE':
                exchange = kite_.EXCHANGE_NSE
            else:
                raise Exception('enter a valid exchange, NSE or NFO')

            try:

                # check the margins and then enter
                margins = kite_.margins()

                if data["ltp"]*data["quantity"] > margins["equity"]["available"]["live_balance"]:
                    raise Exception("insufficent margins")

                order_id = market_buy_order(
                    kite_, data['trading_symbol'], exchange, data['quantity'])
                validate_order(order_id, kite_)

                return Response({
                    'message': f'order id is {order_id}'
                }, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({
                    'error': str(ex)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except AssertionError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MarketOrderSell(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = request.data
        try:
            kite_ = request.user.userprofile.kite

            if data['exchange'] == 'NFO':
                exchange = kite_.EXCHANGE_NFO
            elif data['exchange'] == 'NSE':
                exchange = kite_.EXCHANGE_NSE
            else:
                raise Exception('enter a valid exchange, NSE or NFO')

            try:

                # check for the positions and also holdings
                positions = kite_.positions()["net"]
                holdings = kite_.holdings()

                flag = False
                quantity = 0

                for holding in holdings:
                    if holding["tradingsymbol"] == data["trading_symbol"] and holding["quantity"] > 0:
                        flag = True
                        quantity = holding["quantity"]

                for position in positions:
                    if position["tradingsymbol"] == data["trading_symbol"] and position["quantity"] > 0:
                        flag = True
                        quantity = position["quantity"]

                if not(flag):
                    raise Exception("position not found for sell")

                order_id = market_sell_order(
                    kite_, data['trading_symbol'], exchange, quantity)
                validate_order(order_id, kite_)

                return Response({
                    'message': f'order id is {order_id}'
                }, status=status.HTTP_200_OK)
            except Exception as ex:
                print(ex)
                return Response({
                    'error': str(ex)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except AssertionError as e:
            print(e)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# limit orders

class LimitOrderBuy(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = request.data
        try:
            kite_ = request.user.userprofile.kite

            if data['exchange'] == 'NFO':
                exchange = kite_.EXCHANGE_NFO
            elif data['exchange'] == 'NSE':
                exchange = kite_.EXCHANGE_NSE
            else:
                raise Exception('enter a valid exchange, NSE or NFO')

            try:

                # check the margins and then enter
                margins = kite_.margins()
                if data["price"]*data["quantity"] > margins["equity"]["available"]["live_balance"]:
                    raise Exception("insufficent margins")

                order_id = limit_buy_order(
                    kite_, data['trading_symbol'], exchange, data['quantity'], data['price'])
                validate_order(order_id, kite_)

                return Response({
                    'message': f'order id is {order_id}'
                }, status=status.HTTP_200_OK)
            except Exception as ex:
                print(ex)
                return Response({
                    'error': str(ex)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except AssertionError as e:
            print(e)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LimitOrderSell(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = request.data
        try:
            kite_ = request.user.userprofile.kite

            if data['exchange'] == 'NFO':
                exchange = kite_.EXCHANGE_NFO
            elif data['exchange'] == 'NSE':
                exchange = kite_.EXCHANGE_NSE
            else:
                raise Exception('enter a valid exchange, NSE or NFO')

            try:
                # check for the positions and also holdings
                positions = kite_.positions()["net"]
                holdings = kite_.holdings()

                flag = False
                quantity = 0

                for holding in holdings:
                    if holding["tradingsymbol"] == data["trading_symbol"] and holding["quantity"] > 0:
                        flag = True
                        quantity = holding["quantity"]

                for position in positions:
                    if position["tradingsymbol"] == data["trading_symbol"] and position["quantity"] > 0:
                        flag = True
                        quantity = position["quantity"]

                if not(flag):
                    raise Exception("position not found for sell")

                order_id = limit_sell_order(
                    kite_, data['trading_symbol'], exchange, quantity, data['price'])
                validate_order(order_id, kite_)

                return Response({
                    'message': f'order id is {order_id}'
                }, status=status.HTTP_200_OK)
            except Exception as ex:
                print(ex)
                return Response({
                    'error': str(ex)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except AssertionError as e:
            print(e)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# calculate the pnl
class PnlAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        sum = 0
        kite = check_authorization(request.data)
        positions = kite.positions()
        for pos in positions['net']:
            pnl = pos['pnl']
            sum += pnl

        return Response({
            'pnl': sum
        })

# get the margins


class MarginsAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        kite = check_authorization(request.data)
        margins = kite.margins()
        return Response(margins, status=status.HTTP_200_OK)
