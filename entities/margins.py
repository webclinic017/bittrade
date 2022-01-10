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
    def __init__(self, enabled: bool, net: float, available: AvailableMarginType, utilised: UtilisedMarginType) -> None:
        self.enabled = enabled = enabled
        self.net = net
        self.available = available
        self.utilised = utilised


class Commodity:
    def __init__(self, enabled: bool, net: float, available: AvailableMarginType, utilised: UtilisedMarginType) -> None:
        self.enabled = enabled
        self.net = net
        self.available = available
        self.utilised = utilised


class Margins:
    def __init__(self, margins: dict):
        self.equity = Equity(
            enabled=margins["equity"]["enabled"],
            net=margins["equity"]["net"],
            available=AvailableMarginType(
                margins["equity"]["available"]["adhoc_margin"],
                margins["equity"]["available"]["cash"],
                margins["equity"]["available"]["collateral"],
                margins["equity"]["available"]["intraday_payin"],
                margins["equity"]["available"]["live_balance"]
            ),
            utilised=UtilisedMarginType(
                margins["equity"]["utilised"]["debits"],
                margins["equity"]["utilised"]["exposure"],
                margins["equity"]["utilised"]["m2m_relised"],
                margins["equity"]["utilised"]["m2m_unrelised"],
                margins["equity"]["utilised"]["option_premium"],
                margins["equity"]["utilised"]["payout"],
                margins["equity"]["utilised"]["span"],
                margins["equity"]["utilised"]["holding_sales"],
                margins["equity"]["utilised"]["turnover"],
            )
        )
        self.commodity = Commodity(
            enabled=margins["commodity"]["enabled"],
            net=margins["commodity"]["net"],
            available=AvailableMarginType(
                margins["commodity"]["available"]["adhoc_margin"],
                margins["commodity"]["available"]["cash"],
                margins["commodity"]["available"]["collateral"],
                margins["commodity"]["available"]["intraday_payin"],
                margins["commodity"]["available"]["live_balance"]
            ),
            utilised=UtilisedMarginType(
                margins["commodity"]["utilised"]["debits"],
                margins["commodity"]["utilised"]["exposure"],
                margins["commodity"]["utilised"]["m2m_relised"],
                margins["commodity"]["utilised"]["m2m_unrelised"],
                margins["commodity"]["utilised"]["option_premium"],
                margins["commodity"]["utilised"]["payout"],
                margins["commodity"]["utilised"]["span"],
                margins["commodity"]["utilised"]["holding_sales"],
                margins["commodity"]["utilised"]["turnover"],
            )

        )

        self.data = margins
