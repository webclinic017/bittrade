import redis
import os

db = redis.Redis(host=os.environ['REDIS_CHANNEL'])
