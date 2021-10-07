import requests
import json

BASE_URL = 'http://publisher'


def post(uri, headers, body):
    res = requests.post(uri, body, headers=headers)
    return res


def get(uri, headers):
    res = requests.get(uri, headers=headers)
    return res


def make_order_request(trade):
    token = trade["token"]
    endpoint = BASE_URL + trade['endpoint']
    return post(
        endpoint,
        {
            "Content-Type": "application/json",
            "Authorization": f"Token {token}"
        },
        json.dumps(trade)
    )


def get_position(instrument_token):
    return BASE_URL + '/position/' + str(instrument_token)
