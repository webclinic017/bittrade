from celery import shared_task
import time
import datetime
import json
from zerodha.utils import post, get, make_order_request, get_position, BASE_URL

MARGINS_URL = BASE_URL + '/margins/'


@shared_task
def place_trade(trade):
    # print(trade)
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
            )).json()
        price = trade['ltp'] * trade['quantity']
        # print(margins)
        if price <= margins['equity']['available']['cash'] / 2:
            # make the request
            res = make_order_request(trade)
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
            raise Exception('insufficent margins')

    elif trade['tag'] == 'EXIT':
        # check for the position
        position = get(
            get_position(trade['instrument_token']),
            {
                "Authorization": f'Token {token}'
            }
        )
        if position.status_code == 404:
            return False

        position = position.json()
        trade["quantity"] = position["quantity"] if position["quantity"] <= 2000 else 2000
        res = make_order_request(trade)
        position = post(
            get_position(trade['instrument_token']),
            {
                "Content-Type": "application/json",
                "Authorization": f"Token {token}"
            },
            json.dumps(trade)
        )

    return True


@shared_task
def delay_return():
    t1 = datetime.datetime.now().time()
    print(t1)
    time.sleep(10)
    return 1
