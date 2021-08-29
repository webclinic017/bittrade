# from django.shortcuts import render
from django.http import HttpResponse
from kiteconnect import KiteConnect
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .functions import (
    check_validity, 
    limit_buy_order, 
    limit_sell_order, 
    market_buy_order, 
    market_sell_order, 
    validate_limit_api, 
    validate_market_api, 
    check_authorization,
    validate_order
)
from .models import MarketOrder, LimitOrder
from .serializers import MarketOrderSerializer, LimitOrderSerializer
# Create your views here.


# return the request token to the user
def zerodha_auth(request):
    return HttpResponse(request.GET['request_token'])

# get the access token of zerodha api
class ZerodhaAccessToken(APIView):
    def post(self, request):
        data = request.data
        check_validity(data)

        kite = KiteConnect(api_key=data['api_key'])
        data_ = kite.generate_session(
            data['request_token'],
            data['api_secret']
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
            kite_ = validate_market_api(data)

            if data['exchange'] == 'NFO':
                exchange = kite_.EXCHANGE_NFO
            elif data['exchange'] == 'NSE':
                exchange = kite_.EXCHANGE_NSE
            else:
                raise Exception('enter a valid exchange, NSE or NFO')

            try:
                order_id = market_buy_order(
                    kite_, data['trading_symbol'], exchange, data['quantity'])
                validate_order(order_id, kite_)
                
                # create a market order row in the database
                MarketOrder.objects.create(
                    user=request.user,
                    trading_symbol=data['trading_symbol'],
                    exchange=data['exchange'],
                    quantity=data['quantity'],
                    action='BUY'
                )
                
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
            kite_ = validate_market_api(data)

            if data['exchange'] == 'NFO':
                exchange = kite_.EXCHANGE_NFO
            elif data['exchange'] == 'NSE':
                exchange = kite_.EXCHANGE_NSE
            else:
                raise Exception('enter a valid exchange, NSE or NFO')

            try:
                order_id = market_sell_order(
                    kite_, data['trading_symbol'], exchange, data['quantity'])
                validate_order(order_id, kite_)
                
                # create a market order row in the database
                MarketOrder.objects.create(
                    user=request.user,
                    trading_symbol=data['trading_symbol'],
                    exchange=data['exchange'],
                    quantity=data['quantity'],
                    action='SELL'
                )
                
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
            kite_ = validate_limit_api(data)

            if data['exchange'] == 'NFO':
                exchange = kite_.EXCHANGE_NFO
            elif data['exchange'] == 'NSE':
                exchange = kite_.EXCHANGE_NSE
            else:
                raise Exception('enter a valid exchange, NSE or NFO')

            try:
                order_id = limit_buy_order(
                    kite_, data['trading_symbol'], exchange, data['quantity'], data['price'])
                validate_order(order_id, kite_)
                
                # create limit order object
                LimitOrder.objects.create(
                    user=request.user,
                    trading_symbol=data['trading_symbol'],
                    exchange=data['exchange'],
                    quantity=data['quantity'],
                    price=data['price'],
                    action='BUY'
                )
                
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
            kite_ = validate_limit_api(data)

            if data['exchange'] == 'NFO':
                exchange = kite_.EXCHANGE_NFO
            elif data['exchange'] == 'NSE':
                exchange = kite_.EXCHANGE_NSE
            else:
                raise Exception('enter a valid exchange, NSE or NFO')

            try:
                order_id = limit_sell_order(
                    kite_, data['trading_symbol'], exchange, data['quantity'], data['price'])
                validate_order(order_id, kite_)
                
                # create limit order object
                LimitOrder.objects.create(
                    user=request.user,
                    trading_symbol=data['trading_symbol'],
                    exchange=data['exchange'],
                    quantity=data['quantity'],
                    price=data['price'],
                    action='SELL'
                )
                
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


# reterive all market orders
class MarketOrderList(ListAPIView):
    serializer_class = MarketOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.market_orders.all()

# reterive all limit orders
class LimitOrderList(ListAPIView):
    serializer_class = LimitOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.limit_orders.all()
    
# calculate the pnl
class PnlAPI(APIView):
    permission_classes = [IsAuthenticated,]
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