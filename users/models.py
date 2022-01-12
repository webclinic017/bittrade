from django.db import models
from django.contrib.auth.models import User
from kiteconnect.connect import KiteConnect
from entities.trade import OrderType, Trade
import datetime

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='userprofile')
    api_key = models.CharField(max_length=200)
    api_secret = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    investment = models.IntegerField()
    max_loss = models.IntegerField()
    max_profit = models.IntegerField()
    nifty_lot = models.IntegerField()
    banknifty_lot = models.IntegerField()
    zerodha_last_login = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.user.username

    @property
    def kite(self) -> KiteConnect:
        return KiteConnect(self.api_key, self.access_token)

    @property
    def is_accesstoken_valid(self) -> bool:
        login_period = (datetime.datetime.now() -
                        self.zerodha_last_login).seconds / (60 * 60)

        return login_period <= 2
