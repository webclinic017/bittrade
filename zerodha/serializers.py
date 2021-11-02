from django.db.models import fields
from rest_framework import serializers
from zerodha.models import MarketOrder, LimitOrder, Position, APICredentials


class MarketOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketOrder
        fields = '__all__'


class LimitOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitOrder
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class APICredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = APICredentials
        fields = '__all__'
