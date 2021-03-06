from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Node(models.Model):
    NODE_TYPES = [
        ('indicator', 'indicator'),
        ('operator', 'operator'),
        ('constant', 'constant')
    ]

    node_type = models.CharField(max_length=20, choices=NODE_TYPES)
    value = models.CharField(max_length=200)
    kwargs = models.JSONField()

    left_child = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='left_children')
    right_child = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='right_children')

    def evaluate_helper(self, node, ticker: str):
        if node == None:
            return ''

        left_evaluate = self.evaluate_helper(node.left_child, ticker)
        right_evaluate = self.evaluate_helper(node.right_child, ticker)

        if (node.node_type == 'indicator'):
            return left_evaluate + " " + node.value + f"({ticker})" + " " + right_evaluate
        else:
            return left_evaluate + node.value + right_evaluate

    def evaluate(self, ticker: str):
        return self.evaluate_helper(self, ticker)

    @classmethod
    def from_dict(cls, data: dict):
        node = cls(
            node_type=data['type'], value=data['value'], kwargs=data.get("kwargs", {}))

        if 'left_child' in data:
            node.left_child = cls.from_dict(data['left_child'])

        if 'right_child' in data:
            node.right_child = cls.from_dict(data['right_child'])

        node.save()

        return node


class Strategy(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='strategy_list')
    name = models.CharField(max_length=200)
    entry_node = models.ForeignKey(
        Node, on_delete=models.CASCADE, null=True, blank=True, related_name='strategies_enrties')
    exit_node = models.ForeignKey(
        Node, on_delete=models.CASCADE, null=True, blank=True, related_name='strategies_exits')

    profit_percent = models.FloatField()
    loss_percent = models.FloatField()
    lot_size = models.IntegerField(default=1)

    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Indicator(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    inputs = models.JSONField()
    parameters = models.JSONField()

    def __str__(self):
        return self.strategy.name + " " + self.name


class StrategyTicker(models.Model):
    ticker = models.CharField(max_length=200)
    exchange = models.CharField(max_length=10)
    strategy = models.ForeignKey(
        Strategy, on_delete=models.CASCADE, related_name='strategy_tickers')
    instrument_token = models.IntegerField()
    lot_size = models.IntegerField()

    def __str__(self):
        return self.strategy.name + f'[{self.exchange}:{self.ticker}]'
