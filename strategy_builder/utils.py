import operator


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
