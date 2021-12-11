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
from zerodha.models import APICredentials, Position
from zerodha.serializers import APICredentialSerializer, MarketOrderSerializer, LimitOrderSerializer, PositionSerializer
from rest_framework import generics
from zerodha.pagenation import OrdersPagenation
from django.conf import settings
# return the request token to the user


def zerodha_auth(request):
    return HttpResponseRedirect(settings.FRONTEND_URL + "/request_token-zerodha/" + request.GET['request_token'])

# get the access token of zerodha api


class ZerodhaAccessToken(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        check_validity(data)

        kite = KiteConnect(api_key=data['api_key'])
        data_ = kite.generate_session(
            data['request_token'],
            data['api_secret']
        )

        request.user.userprofile.access_token = data_['access_token']
        request.user.userprofile.save()

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
            kite_ = request.user.userprofile.getKiteInstance()

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
            kite_ = request.user.userprofile.getKiteInstance()

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
            kite_ = request.user.userprofile.getKiteInstance()

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
            kite_ = request.user.userprofile.getKiteInstance()

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


# reterive all market orders
class UsersMarketOrderListAPI(generics.ListAPIView):
    serializer_class = MarketOrderSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = OrdersPagenation

    def get_queryset(self):
        return self.request.user.market_orders.all().order_by('-id')

# reterive all limit orders


class UsersLimitOrderListAPI(generics.ListAPIView):
    serializer_class = LimitOrderSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = OrdersPagenation

    def get_queryset(self):
        return self.request.user.limit_orders.all().order_by('-id')

# reterive all the positions


class PositionsListAPI(APIView):

    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        # get the user
        positions = request.user.positions.all()
        serializer = self.serializer_class(positions, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# reterive a particular position and also try to update it
class PositionDetailAPI(APIView):

    serializer = PositionSerializer
    permission_classes = [IsAuthenticated, ]

    # reterive a particular api
    def get(self, request, token):
        if request.user.positions.filter(instrument_token=token).exists():
            serializer = self.serializer(
                request.user.positions.get(instrument_token=token))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # create or update the position of the user

    def post(self, request, token):
        # check if the position with the given token exist
        if request.user.positions.filter(instrument_token=token).exists():
            # the position exist
            position = request.user.positions.get(instrument_token=token)
            # check if the request is about entry or exit
            if request.data['tag'] == 'ENTRY':
                position.quantity += request.data['quantity']
            else:
                position.quantity -= request.data['quantity']
            # price field is only updated for the limit orders
            position.price = request.data.get('price', None)
            # average entry price
            position.entry_price += request.data['entry_price']
            position.entry_price /= 2
            if position.quantity <= 0:
                position.delete()
            else:
                position.save()
        else:
            # the position dosent exist create the position
            if request.data['tag'] == 'ENTRY':
                position = Position(
                    user=request.user,
                    entry_price=request.data['entry_price'],
                    instrument_token=request.data['instrument_token'],
                    ltp=request.data['ltp'],
                    price=request.data.get('price', None),
                    quantity=request.data['quantity'],
                    tag=request.data['tag'],
                    trading_symbol=request.data['trading_symbol'],
                    uri=request.data['uri']
                )
                position.save()

        return Response(status=status.HTTP_200_OK)


class APICredentialDetailView(APIView):

    def get(self, request, userid):
        try:
            api = APICredentials.objects.get(userid=userid)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = APICredentialSerializer(api)
            return Response(serializer.data)
