# from django.shortcuts import render
from django.http import HttpResponse
from kiteconnect import KiteConnect
from rest_framework.views import APIView
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
# Create your views here.


def zerodha_auth(request):
    return HttpResponse(request.GET['request_token'])


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


# reterive all orders
class ZerodhaOrders(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request : Request):
        kite = check_authorization(request.data)
        orders = []
        orders_ = kite.orders()
        
        for order in orders_:
            if order['status'] == 'COMPLETE':
                orders.append(order)
        
        return Response(orders, status=status.HTTP_200_OK)