from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=200)
    api_secret = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    investment = models.IntegerField()
    max_loss = models.IntegerField()
    max_profit = models.IntegerField()
    nifty_lot = models.IntegerField()
    banknifty_lot = models.IntegerField()

    def __str__(self):
        return self.user.username
