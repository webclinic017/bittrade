from threading import Thread
import redis
import json
import time
from kiteconnect import KiteTicker
import datetime


class RedisKiteTicker:

    def __init__(self, api_key, access_token, host, tokens) -> None:
        self.kws = KiteTicker(api_key=api_key, access_token=access_token)
        self.db = redis.Redis(host=host)

        def on_connect(ws, response):
            ws.subscribe(tokens)
            ws.set_mode(ws.MODE_FULL, tokens)

        def on_close(ws, code, reason):
            print(reason)
            ws.stop()

        def on_ticks(ws, ticks):

            for tick in ticks:
                # print(tick)
                self.db.set(str(tick['instrument_token']),
                            json.dumps(tick, default=str))

        self.kws.on_connect = on_connect
        self.kws.on_ticks = on_ticks
        self.kws.on_close = on_close

    def exitService(self):
        while True:
            if datetime.datetime.now().time() >= datetime.time(9, 0):
                exit(0)
            time.sleep(5)

    def start(self):
        Thread(target=self.exitService).start()
        self.kws.connect()
