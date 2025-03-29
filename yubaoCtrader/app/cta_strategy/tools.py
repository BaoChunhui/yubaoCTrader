from concurrent.futures.process import _ThreadWakeup
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List
from copy import deepcopy

from yubaoCtrader.trader.object import BarData, TradeData, Direction
from yubaoCtrader.app.cta_strategy import StopOrder
from yubaoCtrader.trader.object import OrderData
from yubaoCtrader.trader.constant import Status
from yubaoCtrader.app.cta_strategy.base import (
    BacktestingMode,
    EngineType,
    STOPORDER_PREFIX,
    StopOrder,
    StopOrderStatus,
    INTERVAL_DELTA_MAP
)


class OrderRecorder(object):
    """记录活跃的委托"""
    
    def __init__(self) -> None:
        """初始化构造函数"""
        # self.stop_orders: Dict[str, StopOrder] = {}
        # self.limit_orders: Dict[str, OrderData] = {}
        self.active_limit_orders: Dict[str, OrderData] = {}
        self.active_stop_orders: Dict[str, StopOrder] = {}
        
    def update_limit_order(self, order: OrderData) -> None:
        """更新限价单委托"""
        order = deepcopy(order)

        if order.status == Status.SUBMITTING or order.status == Status.NOTTRADED or order.status == Status.PARTTRADED:
            self.active_limit_orders[order.vt_orderid] = order

        elif order.status == Status.ALLTRADED or order.status == Status.CANCELLED:
            if order.vt_orderid in self.active_limit_orders:
                self.active_limit_orders.pop(order.vt_orderid)
                
        elif order.status == Status.REJECTED:
            print(f"报单{order.vt_orderid}被拒绝")
                
        else:
            print(f"异常：不存在的报单类型{order.status.value}")
            
    def get_active_limit_orders(self) -> Dict[str, OrderData]:
        active_limit_orders = deepcopy(self.active_limit_orders)
        return active_limit_orders

    def update_stop_order(self, stop_order: StopOrder) -> None:
        """更新停止单委托"""
        stop_order = deepcopy(stop_order)
        
        if stop_order.status == StopOrderStatus.WAITING:
            self.active_stop_orders[stop_order.stop_orderid] = stop_order
        
        elif stop_order.status == StopOrderStatus.TRIGGERED or stop_order.status == StopOrderStatus.CANCELLED:
            if stop_order.stop_orderid in self.active_stop_orders:
                self.active_stop_orders.pop(stop_order.stop_orderid)
                
        else:
            print(f"异常：不存在的报单类型{stop_order.status.value}")
        
    def get_active_stop_orders(self) -> Dict[str, StopOrder]:
        active_stop_orders = deepcopy(self.active_stop_orders)
        return active_stop_orders


class DailyResult:
    """"""

    def __init__(self, date: date, close_price: float) -> None:
        """"""
        self.date: date = date
        self.close_price: float = close_price
        self.pre_close: float = 0

        self.trades: List[TradeData] = []
        self.trade_count: int = 0

        self.start_pos = 0
        self.end_pos = 0

        self.turnover: float = 0
        self.commission: float = 0
        self.slippage: float = 0

        self.trading_pnl: float = 0
        self.holding_pnl: float = 0
        self.total_pnl: float = 0
        self.net_pnl: float = 0

    def add_trade(self, trade: TradeData) -> None:
        """"""
        self.trades.append(trade)

    def calculate_pnl(
        self,
        pre_close: float,
        start_pos: float,
        size: int,
        rate: float,
        slippage: float
    ) -> None:
        """"""
        # If no pre_close provided on the first day,
        # use value 1 to avoid zero division error
        if pre_close:
            self.pre_close = pre_close
        else:
            self.pre_close = 1

        # Holding pnl is the pnl from holding position at day start
        self.start_pos = start_pos
        self.end_pos = start_pos

        self.holding_pnl = self.start_pos * (self.close_price - self.pre_close) * size

        # Trading pnl is the pnl from new trade during the day
        self.trade_count = len(self.trades)

        for trade in self.trades:
            if trade.direction == Direction.LONG:
                pos_change = trade.volume
            else:
                pos_change = -trade.volume

            self.end_pos += pos_change

            turnover: float = trade.volume * size * trade.price
            self.trading_pnl += pos_change * \
                (self.close_price - trade.price) * size
            self.slippage += trade.volume * size * slippage

            self.turnover += turnover
            self.commission += turnover * rate

        # Net pnl takes account of commission and slippage cost
        self.total_pnl = self.trading_pnl + self.holding_pnl
        self.net_pnl = self.total_pnl - self.commission - self.slippage
