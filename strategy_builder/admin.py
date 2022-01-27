from django.contrib import admin
from strategy_builder.models import (
    Node,
    Strategy,
    StrategyTicker,
)

# Register your models here.
admin.site.register(Node)
admin.site.register(Strategy)
admin.site.register(StrategyTicker)
