from django.contrib import admin
from .models import MarketOrder, LimitOrder
# Register your models here.

admin.site.register(MarketOrder)
admin.site.register(LimitOrder)
