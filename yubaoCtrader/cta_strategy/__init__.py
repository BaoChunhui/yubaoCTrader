from pathlib import Path
from typing import Type

from yubaoCtrader.trader.app import BaseApp
from yubaoCtrader.trader.constant import Direction
from yubaoCtrader.trader.object import TickData, BarData, TradeData, OrderData
from yubaoCtrader.trader.utility import BarGenerator, ArrayManager

from .base import APP_NAME, StopOrder
from .engine import CtaEngine
from .template import CtaTemplate, CtaSignal, TargetPosTemplate


class CtaStrategyApp(BaseApp):
    """"""

    app_name: str = APP_NAME
    app_module: str = __module__
    app_path: Path = Path(__file__).parent
    display_name: str = "CTA策略"
    engine_class: Type[CtaEngine] = CtaEngine
    widget_name: str = "CtaManager"
    icon_name: str = str(app_path.joinpath("ui", "cta.ico"))
