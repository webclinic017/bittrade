from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token

model = Token

@database_sync_to_async
def get_user(key):
    return model.objects.select_related('user').get(key=key)

class QueryMiddleWare:
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        key = str(scope['query_string']).split('=')[1].replace("'", "")
        user = await get_user(key)
        scope['user'] = user
        return await self.app(scope, receive, send)