from pathlib import Path

from yubaoCtrader.trader.app import BaseApp
from yubaoCtrader.trader.constant import Direction
from yubaoCtrader.trader.object import TickData, BarData, TradeData, OrderData
from yubaoCtrader.trader.utility import BarGenerator, ArrayManager

from .base import APP_NAME
from .engine import StrategyEngine
from .template import StrategyTemplate
from .backtesting import BacktestingEngine


class PortfolioStrategyApp(BaseApp):
    """"""

    app_name: str = APP_NAME
    app_module: str = __module__
    app_path: Path = Path(__file__).parent
    display_name: str = "组合策略"
    engine_class: StrategyEngine = StrategyEngine
    widget_name: str = "PortfolioStrategyManager"
    icon_name: str = str(app_path.joinpath("ui", "strategy.ico"))
