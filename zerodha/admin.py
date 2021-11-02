from django.contrib import admin
from .models import MarketOrder, LimitOrder, APICredentials
# Register your models here.

admin.site.register(MarketOrder)
admin.site.register(LimitOrder)
admin.site.register(APICredentials)
