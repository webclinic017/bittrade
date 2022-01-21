import operator
from strategy_builder.models import Strategy
from channels.layers import get_channel_layer


class TradeUtil:
    operators = {
        "and": operator.and_,
        "or": operator.or_,
        ">": operator.gt,
        "<": operator.lt,
        "==": operator.eq,
        ">=": operator.ge,
        "<=": operator.le,
        "!=": operator.ne,
    }

    indicators = [
        'sma',
        'ema',
        'rsi',
        'momentum',
    ]

    @classmethod
    def evaluate_expression(cls, a, operator, b):
        return cls.operators[operator](a, b)


def start_strategy(strategy_id):
    strategy = Strategy.objects.get(pk=strategy_id)
    user = strategy.user.userprofile.id
