import importlib
import traceback
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Type
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from copy import copy
from glob import glob
from concurrent.futures import Future

from yubaoCtrader.event import Event, EventEngine
from yubaoCtrader.trader.engine import BaseEngine, MainEngine
from yubaoCtrader.trader.object import (
    OrderRequest,
    SubscribeRequest,
    HistoryRequest,
    CancelRequest,
    LogData,
    TickData,
    BarData,
    OrderData,
    TradeData,
    ContractData,
)
from yubaoCtrader.trader.event import (
    EVENT_TICK,
    EVENT_ORDER,
    EVENT_TRADE
)
from yubaoCtrader.trader.constant import (
    Direction,
    OrderType,
    Interval,
    Exchange,
    Offset,
    Status
)
from yubaoCtrader.trader.utility import load_json, save_json, extract_vt_symbol, round_to
from yubaoCtrader.trader.database import BaseDatabase, get_database, DB_TZ
from yubaoCtrader.trader.datafeed import BaseDatafeed, get_datafeed

from .base import (
    APP_NAME,
    EVENT_CTA_LOG,
    EVENT_CTA_STRATEGY,
    EVENT_CTA_STOPORDER,
    EngineType,
    StopOrder,
    StopOrderStatus,
    STOPORDER_PREFIX
)
from .template import CtaTemplate, TargetPosTemplate


# 停止单状态映射
STOP_STATUS_MAP: Dict[Status, StopOrderStatus] = {
    Status.SUBMITTING: StopOrderStatus.WAITING,
    Status.NOTTRADED: StopOrderStatus.WAITING,
    Status.PARTTRADED: StopOrderStatus.TRIGGERED,
    Status.ALLTRADED: StopOrderStatus.TRIGGERED,
    Status.CANCELLED: StopOrderStatus.CANCELLED,
    Status.REJECTED: StopOrderStatus.CANCELLED
}


class CtaEngine(BaseEngine):
    """"""

    engine_type: EngineType = EngineType.LIVE  # live trading engine

    setting_filename: str = "cta_strategy_setting.json"
    data_filename: str = "cta_strategy_data.json"

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        pass

    def init_engine(self) -> None:
        pass

    def close(self) -> None:
        pass

    def register_event(self) -> None:
        pass

    def init_datafeed(self) -> None:
        pass

    def query_bar_from_datafeed(
        self, symbol: str, exchange: Exchange, interval: Interval, start: datetime, end: datetime
    ) -> List[BarData]:
        """
        Query bar data from datafeed.
        """

    def process_tick_event(self, event: Event) -> None:
        pass

    def process_order_event(self, event: Event) -> None:
        pass

    def process_trade_event(self, event: Event) -> None:
        pass

    def check_stop_order(self, tick: TickData) -> None:
        pass

    def send_server_order(
        self,
        strategy: CtaTemplate,
        contract: ContractData,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
        type: OrderType,
        lock: bool,
        net: bool
    ) -> list:
        """
        Send a new order to server.
        """

    def send_limit_order(
        self,
        strategy: CtaTemplate,
        contract: ContractData,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
        lock: bool,
        net: bool
    ) -> list:
        """
        Send a limit order to server.
        """

    def send_server_stop_order(
        self,
        strategy: CtaTemplate,
        contract: ContractData,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
        lock: bool,
        net: bool
    ) -> list:
        """
        Send a stop order to server.

        Should only be used if stop order supported
        on the trading server.
        """

    def send_local_stop_order(
        self,
        strategy: CtaTemplate,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
        lock: bool,
        net: bool
    ) -> list:
        """
        Create a new local stop order.
        """

    def cancel_server_order(self, strategy: CtaTemplate, vt_orderid: str) -> None:
        pass

    def cancel_local_stop_order(self, strategy: CtaTemplate, stop_orderid: str) -> None:
        pass

    def send_order(
        self,
        strategy: CtaTemplate,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
        stop: bool,
        lock: bool,
        net: bool
    ) -> list:
        """
        """

    def cancel_order(self, strategy: CtaTemplate, vt_orderid: str) -> None:
        pass

    def cancel_all(self, strategy: CtaTemplate) -> None:
        pass

    def get_engine_type(self) -> EngineType:
        pass

    def get_pricetick(self, strategy: CtaTemplate) -> float:
        pass

    def get_size(self, strategy: CtaTemplate) -> int:
        pass

    def load_bar(
        self,
        vt_symbol: str,
        days: int,
        interval: Interval,
        callback: Callable[[BarData], None],
        use_database: bool
    ) -> List[BarData]:
        """"""

    def load_tick(
        self,
        vt_symbol: str,
        days: int,
        callback: Callable[[TickData], None]
    ) -> List[TickData]:
        """"""

    def call_strategy_func(
        self, strategy: CtaTemplate, func: Callable, params: Any = None
    ) -> None:
        """
        Call function of a strategy and catch any exception raised.
        """

    def add_strategy(
        self, class_name: str, strategy_name: str, vt_symbol: str, setting: dict
    ) -> None:
        """
        Add a new strategy.
        """

    def init_strategy(self, strategy_name: str) -> Future:
        pass

    def _init_strategy(self, strategy_name: str) -> None:
        pass

    def start_strategy(self, strategy_name: str) -> None:
        pass

    def stop_strategy(self, strategy_name: str) -> None:
        pass

    def edit_strategy(self, strategy_name: str, setting: dict) -> None:
        pass

    def remove_strategy(self, strategy_name: str) -> bool:
        pass

    def load_strategy_class(self) -> None:
        pass

    def load_strategy_class_from_folder(self, path: Path, module_name: str = "") -> None:
        pass

    def load_strategy_class_from_module(self, module_name: str) -> None:
        pass

    def load_strategy_data(self) -> None:
        pass

    def sync_strategy_data(self, strategy: CtaTemplate) -> None:
        pass

    def get_all_strategy_class_names(self) -> list:
        pass

    def get_strategy_class_parameters(self, class_name: str) -> dict:
        pass

    def get_strategy_parameters(self, strategy_name) -> dict:
        pass

    def init_all_strategies(self) -> Dict[str, Future]:
        pass

    def start_all_strategies(self) -> None:
        pass

    def stop_all_strategies(self) -> None:
        pass

    def load_strategy_setting(self) -> None:
        pass

    def update_strategy_setting(self, strategy_name: str, setting: dict) -> None:
        pass

    def remove_strategy_setting(self, strategy_name: str) -> None:
        pass

    def put_stop_order_event(self, stop_order: StopOrder) -> None:
        pass

    def put_strategy_event(self, strategy: CtaTemplate) -> None:
        pass

    def write_log(self, msg: str, strategy: CtaTemplate = None) -> None:
        pass

    def send_email(self, msg: str, strategy: CtaTemplate = None) -> None:
        pass
