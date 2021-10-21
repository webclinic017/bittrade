import redis
import os
from jwt import JWT, jwk_from_pem
from django.conf import settings

db = redis.Redis(host=os.environ['REDIS_CHANNEL'])

with open(os.path.join(settings.BASE_DIR, 'secrets', 'public.pem'), 'rb') as f:
    verifying_key = jwk_from_pem(f.read())

jwt = JWT()


def verify_message(message):
    try:
        data = jwt.decode(message, verifying_key)
    except:
        return {}, False
    return data, {}
