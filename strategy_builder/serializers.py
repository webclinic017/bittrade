from rest_framework.serializers import ModelSerializer, SerializerMethodField
from strategy_builder.models import Strategy, Node, StrategyTicker, TechenicalIndicator


class StrategyTickerSerializer(ModelSerializer):
    class Meta:
        model = StrategyTicker
        fields = '__all__'


class NodeSerializer(ModelSerializer):
    left_child = SerializerMethodField()
    right_child = SerializerMethodField()

    class Meta:
        model = Node
        fields = '__all__'

    def get_left_child(self, obj):
        if obj.left_child != None:
            return NodeSerializer(obj.left_child).data

        return None

    def get_right_child(self, obj):
        if obj.right_child != None:
            return NodeSerializer(obj.right_child).data

        return None


class StrategySerializer(ModelSerializer):
    entry_node = NodeSerializer()
    exit_node = NodeSerializer()
    strategy_tickers = StrategyTickerSerializer(many=True)

    class Meta:
        model = Strategy
        fields = '__all__'


class TechenicalIndicatorSerializer(ModelSerializer):
    class Meta:
        model = TechenicalIndicator
        fields = '__all__'
