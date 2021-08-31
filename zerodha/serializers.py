from rest_framework import serializers
from zerodha.models import MarketOrder, LimitOrder

class MarketOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketOrder
        fields = '__all__'

class LimitOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitOrder
        fields = '__all__'