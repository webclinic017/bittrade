class AvailableMarginType:
    def __init__(self, adhoc_margin: float, cash: float, collateral: float, intraday_payin: float, live_balance: float):
        self.adhoc_margin = adhoc_margin
        self.cash = cash
        self.collateral = collateral
        self.intraday_payin = intraday_payin
        self.live_balance = live_balance


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

        self.data = margins

        self.equity.enabled = margins["equity"]["enabled"]
        self.equity.net = margins["equity"]["net"]

        self.equity.available = AvailableMarginType(
            margins["equity"]["available"]["adhoc_margin"],
            margins["equity"]["available"]["cash"],
            margins["equity"]["available"]["collateral"],
            margins["equity"]["available"]["intraday_payin"],
            margins["equity"]["available"]["live_balance"]
        )

        self.equity.utilized = UtilisedMarginType(
            margins["equity"]["utilized"]["debits"],
            margins["equity"]["utilized"]["exposure"],
            margins["equity"]["utilized"]["m2m_relised"],
            margins["equity"]["utilized"]["m2m_unrelised"],
            margins["equity"]["utilized"]["option_premium"],
            margins["equity"]["utilized"]["payout"],
            margins["equity"]["utilized"]["span"],
            margins["equity"]["utilized"]["holding_sales"],
            margins["equity"]["utilized"]["turnover"],
        )

        self.commodity.enabled = margins["commodity"]["enabled"]
        self.commodity.net = margins["commodity"]["net"]

        self.commodity.available = AvailableMarginType(
            margins["commodity"]["available"]["adhoc_margin"],
            margins["commodity"]["available"]["cash"],
            margins["commodity"]["available"]["collateral"],
            margins["commodity"]["available"]["intraday_payin"],
            margins["commodity"]["available"]["live_balance"]
        )

        self.commodity.utilized = UtilisedMarginType(
            margins["commodity"]["utilized"]["debits"],
            margins["commodity"]["utilized"]["exposure"],
            margins["commodity"]["utilized"]["m2m_relised"],
            margins["commodity"]["utilized"]["m2m_unrelised"],
            margins["commodity"]["utilized"]["option_premium"],
            margins["commodity"]["utilized"]["payout"],
            margins["commodity"]["utilized"]["span"],
            margins["commodity"]["utilized"]["holding_sales"],
            margins["commodity"]["utilized"]["turnover"],
        )
