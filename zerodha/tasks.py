from celery import shared_task
import time
import datetime
import requests
import json


def post(uri, headers, body):
    res = requests.post(uri, body, headers=headers)
    return res


def get(uri, headers):
    res = requests.get(uri, headers=headers)
    return res


def make_order_request(trade):
    token = trade["token"]
    return post(
        trade["endpoint"],
        {
            "Content-Type": "application/json",
            "Authorization": f"Token {token}"
        },
        json.dumps(trade)
    )


@shared_task
def place_trade(trade):
    # print(trade)
    token = trade['token']
    if trade['tag'] == 'ENTRY':
        margins = post(
            trade['margins'],
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
            response = res.json()
            status = res.status_code
            # update the position
            position = post(
                trade["position"],
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
            trade['position'],
            {
                "Authorization": f'Token {token}'
            }
        )
        if position.status_code == 404:
            return "", 404

        res = make_order_request(trade)
        response = res.json()
        status = res.status_code
        position = post(
            trade["position"],
            {
                "Content-Type": "application/json",
                "Authorization": f"Token {token}"
            },
            json.dumps(trade)
        )

    return response, status


@shared_task
def delay_return():
    t1 = datetime.datetime.now().time()
    print(t1)
    time.sleep(10)
    return 1
