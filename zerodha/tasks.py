from celery import shared_task
import time
import datetime
import json
from zerodha.utils import post, get, make_order_request, get_position, BASE_URL
import redis
import redis_lock
from rest_framework import status

MARGINS_URL = BASE_URL + '/margins/'

redis_client = redis.StrictRedis(host='redis_channel')


@shared_task
def place_trade(user_id, trade):
    # print(trade)
    lock = redis_lock.Lock(redis_client, str(user_id))
    lock.acquire()
    token = trade['token']
    if trade['tag'] == 'ENTRY':

        margins = post(
            MARGINS_URL,
            {
                'Content-Type': 'application/json',
                'Authorization': f'Token {token}',
            },
            json.dumps({
                'api_key': trade['api_key'],
                'access_token': trade['access_token']
            }
            ))

        if status.is_client_error(margins.status_code) or status.is_server_error(margins.status_code):
            lock.release()
            return False

        margins = margins.json()

        price = trade['ltp'] * trade['quantity']
        # print(margins)
        if price <= margins['equity']['available']['cash'] / 2:
            # make the request

            res = make_order_request(trade)

            if status.is_server_error(res.status_code) or status.is_client_error(res.status_code):
                lock.release()
                return False

            # update the position
            position = post(
                get_position(trade['instrument_token']),
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Token {token}"
                },
                json.dumps(trade)
            )
            print(position)
        else:
            lock.release()
            return False

    elif trade['tag'] == 'EXIT':
        # check for the position
        position = get(
            get_position(trade['instrument_token']),
            {
                "Authorization": f'Token {token}'
            }
        )

        if status.is_client_error(position.status_code) or status.is_server_error(position.status_code):
            lock.release()
            return False

        position = position.json()
        trade["quantity"] = position["quantity"] if position["quantity"] <= 2000 else 2000
        res = make_order_request(trade)

        if status.is_server_error(res.status_code) or status.is_client_error(res.status_code):
            lock.release()
            return False

        position = post(
            get_position(trade['instrument_token']),
            {
                "Content-Type": "application/json",
                "Authorization": f"Token {token}"
            },
            json.dumps(trade)
        )

    lock.release()
    return True


@shared_task
def delay_return():
    t1 = datetime.datetime.now().time()
    print(t1)
    time.sleep(10)
    return 1
