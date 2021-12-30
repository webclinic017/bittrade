from kiteconnect import KiteConnect
from .margins import Margins
from .positions import Positions


class KiteStreamer:
    def __init__(self, kite: KiteConnect):
        self.kite = kite

    @property
    def margins(self) -> Margins:
        return Margins(self.kite.margins())

    @property
    def positions(self) -> Positions:
        return Positions(self.kite.positions())
