from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User
from kiteconnect.connect import KiteConnect
from entities.trade import OrderType, Trade
from django.utils.timezone import now

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
    zerodha_last_login = models.DateTimeField(default=now)

    def __str__(self):
        return self.user.username

    @property
    def kite(self) -> KiteConnect:
        return KiteConnect(self.api_key, self.access_token)

    @property
    def is_accesstoken_valid(self) -> bool:
        try:
            self.kite.profile()
        except:
            return False

        return True


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            api_key='.',
            access_token='.',
            api_secret='.',
            max_loss=10000,
            max_profit=10000,
            banknifty_lot=1,
            nifty_lot=1,
            investment=100000,
        )
