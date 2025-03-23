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


class TradeResult:
    """配对后的完整开平交易"""
    
    def __init__(self, size: int = 1) -> None:
        self.size = size

        # 交易成本
        self.long_cost = 0.0
        self.short_cost = 0.0

        # 交易仓位
        self.long_volume = 0.0
        self.short_volume = 0.0
        self.net_volume = 0.0

        # 开平时点
        self.open_dt: datetime = None
        self.close_dt: datetime = None

        # 成交记录
        self.trades: list[TradeData] = []

        # 交易盈亏
        self.pnl: float = 0
        
    def update_trade(self, trade: TradeData) -> bool:
        """更新成交"""
        # 添加成交记录
        trade.volume = round(float(trade.volume), 3)
        trade.price = round(float(trade.price), 2)
        
        self.trades.append(trade)

        # 更新成交数量和成本
        trade_cost = trade.price * trade.volume * self.size

        if trade.direction == Direction.LONG:
            self.long_volume += trade.volume
            self.long_cost += trade_cost
        else:
            self.short_volume += trade.volume
            self.short_cost += trade_cost

        self.net_volume = self.long_volume - self.short_volume

        if not round(round(float(self.net_volume), 3)*1000):
            self.calculate_result()
            return True
        else:
            return False

    def calculate_result(self) -> None:
        """计算盈亏"""
        # 卖出收到现金，买入付出现金
        self.pnl = self.short_cost - self.long_cost

        self.open_dt = self.trades[0].datetime
        self.close_dt = self.trades[-1].datetime


class ResultManager:
    """交易配对管理器"""

    def __init__(self, size: int = 1) -> None:
        """构造函数"""
        self.size = size

        # 第一条开平交易
        self.result: TradeResult = TradeResult(self.size)

        # 开平交易列表
        self.results: list[TradeResult] = []

    def update_trade(self, trade: TradeData) -> None:
        """更新成交"""
        trade_copy = deepcopy(trade)
        if not trade.volume:
            return
        closed = self.result.update_trade(trade_copy)

        # 如果完成平仓，则创建下一条开平交易
        if closed:
            self.results.append(self.result)
            self.result = TradeResult(self.size)

    def get_results(self) -> list[TradeResult]:
        """获取记录"""
        return self.results
    
    def clear_results(self) -> None:
        """清除开平交易列表"""
        self.results.clear()


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


class PnlTracker:
    """盈亏跟踪器"""
    
    def __init__(self, size: int = 1, last_tracker: "PnlTracker" = None) -> None:
        """构造函数"""
        
        # 合约大小
        self.size: int = size
        
        # 上根K线
        if not last_tracker:
            self.start_pos = 0.0
            self.pre_close = 0.0
        else:
            self.start_pos = last_tracker.end_pos
            self.pre_close = last_tracker.close_price
            
        # 当前K线
        self.datetime: datetime = None
        self.end_pos = self.start_pos
        self.close_price = 0.0

        # 盈亏相关
        self.holding_pnl = 0.0
        self.trading_pnl = 0.0
        self.total_pnl = 0.0

        # 数据容器
        self.trades: list[TradeData] = []
        
    def update_trade(self, trade: TradeData) -> None:
        """更新成交"""
        self.trades.append(trade)

    def update_bar(self, bar: BarData) -> None:
        """更新K线"""
        self.close_price = bar.close_price
        self.datetime = bar.datetime
        
    def calculate_pnl(self):
        """计算盈亏"""
        # 持仓盈亏
        close_change = self.close_price - self.pre_close
        self.holding_pnl = close_change * self.start_pos * self.size

        # 交易盈亏
        for trade in self.trades:
            price_change = self.close_price - float(trade.price)

            if trade.direction == Direction.LONG:
                side: int = 1
            else:
                side: int = -1

            self.trading_pnl += price_change * side * float(trade.volume) * self.size
            self.end_pos += side * float(trade.volume)

        # 汇总盈亏
        self.total_pnl = self.holding_pnl + self.trading_pnl


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
