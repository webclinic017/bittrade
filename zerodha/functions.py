from kiteconnect import KiteConnect # type: ignore
import time


def market_buy_order(kite: KiteConnect, tradingsymbol, exchange, quantity):
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=exchange,
                                tradingsymbol=tradingsymbol,
                                transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=quantity,
                                product=kite.PRODUCT_NRML, order_type=kite.ORDER_TYPE_MARKET,
                                price=None,
                                validity=kite.VALIDITY_DAY,
                                disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                                trailing_stoploss=None, tag=None)
    return order_id


def market_sell_order(kite: KiteConnect, tradingsymbol, exchange, quantity):
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=exchange,
                                tradingsymbol=tradingsymbol,
                                transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=quantity,
                                product=kite.PRODUCT_NRML, order_type=kite.ORDER_TYPE_MARKET,
                                price=None,
                                validity=kite.VALIDITY_DAY,
                                disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                                trailing_stoploss=None, tag=None)
    return order_id


def limit_sell_order(kite: KiteConnect, tradingsymbol, exchange, quantity, price):
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=exchange,
                                tradingsymbol=tradingsymbol,
                                transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=quantity,
                                product=kite.PRODUCT_NRML, order_type=kite.ORDER_TYPE_LIMIT,
                                price=price, validity=kite.VALIDITY_DAY,
                                disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                                trailing_stoploss=None, tag=None)
    return order_id


def limit_buy_order(kite: KiteConnect, tradingsymbol, exchange, quantity, price):
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=exchange,
                                tradingsymbol=tradingsymbol,
                                transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=quantity,
                                product=kite.PRODUCT_NRML, order_type=kite.ORDER_TYPE_LIMIT,
                                price=price, validity=kite.VALIDITY_DAY,
                                disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                                trailing_stoploss=None, tag=None)
    return order_id


def check_validity(data):
    assert 'api_key' in data, 'provide api key'
    assert 'request_token' in data, 'provide request token'
    assert 'api_secret' in data, 'provide api secret'

def check_authorization(data):
    assert 'api_key' in data, 'provide api key'
    assert 'access_token' in data, 'provide access token'

    kite = KiteConnect(api_key=data['api_key'], access_token=data['access_token'])
    return kite

def validate_market_api(data):
    assert 'api_key' in data, 'provide api key'
    assert 'access_token' in data, 'provide access token'
    assert 'trading_symbol' in data, 'provide trading_symbol'
    assert 'exchange' in data, 'provide exchange'
    assert 'quantity' in data, 'provide quantity'
    
    kite_ = KiteConnect(api_key=data['api_key'], access_token=data['access_token'])
    return kite_

def validate_limit_api(data):
    assert 'api_key' in data, 'provide api key'
    assert 'access_token' in data, 'provide access token'
    assert 'trading_symbol' in data, 'provide trading_symbol'
    assert 'exchange' in data, 'provide exchange'
    assert 'quantity' in data, 'provide quantity'
    assert 'price' in data, 'provide price'
    
    kite_ = KiteConnect(api_key=data['api_key'], access_token=data['access_token'])
    return kite_

def validate_order(order_id : int, kite : KiteConnect):
    time.sleep(1)
    order_history = kite.order_history(order_id=order_id)
    
    for order in order_history:
        if order['status'] == 'REJECTED':
            raise Exception('Order rejected')
