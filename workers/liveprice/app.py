from redislive import RedisKiteTicker
from pymongo import MongoClient
from utils import get_key_token
import os
import time

os.environ['TZ'] = 'Asia/Kolkata'
time.tzset()

mongo_clients = MongoClient(
    "mongodb+srv://jag:rtut12#$@cluster0.alwvk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
)

zerodha_id = 'AL0644'

api_key, access_token = get_key_token(
    zerodha_id, mongo_clients["client_details"]["clients"]
)

print("Starting the live data worker")

host = "redis_channel"
tokens = [738561, 5633]

kws = RedisKiteTicker(
    api_key,
    access_token,
    host,
    tokens
)

kws.start()
