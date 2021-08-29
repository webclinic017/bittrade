from rest_framework.serializers import ModelSerializer
from .models import MarketOrder, LimitOrder

class MarketOrderSerializer(ModelSerializer):
    class Meta:
        model = MarketOrder
        fields = '__all__'

class LimitOrderSerializer(ModelSerializer):
    class Meta:
        model = LimitOrder
        fields = '__all__'