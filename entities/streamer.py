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

    async def get_margins_async(self) -> Margins:
        return Margins(self.kite.margins())

    async def get_positions_async(self) -> Positions:
        return Positions(self.kite.positions())

    async def get_pnl_async(self) -> float:
        pnl = 0

        for position in self.positions.day:
            pnl += position.pnl

        return pnl
