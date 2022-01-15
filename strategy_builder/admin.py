from django.contrib import admin
from strategy_builder.models import (
    Node,
    Strategy
)

# Register your models here.
admin.site.register(Node)
admin.site.register(Strategy)
