class AvailableMarginType:
    def __init__(self, adhoc_margin: float, cash: float, collateral: float, intraday_payin: float):
        self.adhoc_margin = adhoc_margin
        self.cash = cash
        self.collateral = collateral
        self.intraday_payin = intraday_payin


class UtilisedMarginType:
    def __init__(
        self,
        debits: float,
        exposure: float,
        m2m_relised: float,
        m2m_unrelised: float,
        option_premium: float,
        payout: float,
        span: float,
        holding_sales: float,
        turnover: float
    ):

        self.debits = debits
        self.exposure = exposure
        self.m2m_relised = m2m_relised
        self.m2m_unrealised = m2m_unrelised
        self.option_premium = option_premium
        self.payout = payout
        self.span = span
        self.holding_sales = holding_sales
        self.turnover = turnover


class Equity:
    def __init__(self, enabled: bool, net: float, available: AvailableMarginType, utilized: UtilisedMarginType) -> None:
        self.enabled = enabled = enabled
        self.net = net
        self.available = available
        self.utilized = utilized


class Commodity:
    def __init__(self, enabled: bool, net: float, available: AvailableMarginType, utilized: UtilisedMarginType) -> None:
        self.enabled = enabled = enabled
        self.net = net
        self.available = available
        self.utilized = utilized


class Margins:
    def __init__(self, margins: dict):
        self.equity = Equity()
        self.commodity = Commodity()

        self.equity.enabled = margins["equity"]["enabled"]
        self.equity.net = margins["equity"]["net"]
        self.equity.available = AvailableMarginType(
            margins["equity"]["available"]["adhoc_margin"],
            margins["equity"]["available"]["cash"],
            margins["equity"]["available"]["collateral"],
            margins["equity"]["available"]["intraday_payin"]
        )

        self.commodity.enabled = margins["commodity"]["enabled"]
        self.commodity.net = margins["commodity"]["net"]
        self.commodity.available = AvailableMarginType(
            margins["equity"]["commodity"]["adhoc_margin"],
            margins["equity"]["commodity"]["cash"],
            margins["equity"]["commodity"]["collateral"],
            margins["equity"]["commodity"]["intraday_payin"]
        )
