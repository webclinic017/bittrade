# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import models

ORDER_TYPES = [
    ('BUY',  'BUY'),
    ('SELL', 'SELL')
]

class MarketOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='market_orders')
    trading_symbol = models.CharField(max_length=100)
    exchange = models.CharField(max_length=10)
    quantity = models.IntegerField()
    action = models.CharField(max_length=10, choices=ORDER_TYPES)
    

class LimitOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='limit_orders')
    trading_symbol = models.CharField(max_length=100)
    exchange = models.CharField(max_length=10)
    quantity = models.IntegerField()
    price = models.FloatField()
    action = models.CharField(max_length=10, choices=ORDER_TYPES)
    

class Position(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='positions') # <-- reverse foreign key field positions
    entry_price = models.FloatField(null=False)
    instrument_token = models.CharField(max_length=50, null=False)
    ltp = models.FloatField()
    price = models.FloatField(null=True)
    quantity = models.IntegerField(null=False)
    tag = models.CharField(max_length=20, null=False)
    trading_symbol = models.CharField(max_length=50, null=False)
    uri = models.CharField(max_length=200, null=False)
    
    def __str__(self):
        return f'{self.user}[{self.trading_symbol}]'


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
