from yubaoCtrader.trader.setting import SETTINGS
from datetime import datetime, time, timedelta
from typing import List, Set, Tuple
from time import sleep

from yubaoCtrader.trader.utility import ZoneInfo
CHINA_TZ = ZoneInfo("Asia/Shanghai")

import rqdatac

from yubaoCtrader.trader.object import HistoryRequest, BarData
from yubaoCtrader.trader.constant import Exchange, Interval
from yubaoCtrader.trader.datafeed import get_datafeed, BaseDatafeed
from yubaoCtrader.trader.database import get_database, BaseDatabase
import pdb

SETTINGS["datafeed.name"] = "rqdata"
SETTINGS["datafeed.username"] = "license"
SETTINGS["datafeed.password"] = ""

SETTINGS["database.timezone"] = "Asia/Shanghai"
SETTINGS["database.name"] = "mysql"
SETTINGS["database.database"] = "market_data"
SETTINGS["database.host"] = "localhost"
SETTINGS["database.port"] = 3306
SETTINGS["database.user"] = "root"
SETTINGS["database.password"] = ""

datafeed: BaseDatafeed = get_datafeed()
datafeed.init()

database: BaseDatabase = get_database()

suffix_list: List[str] = ["2409"]
interval: Interval = Interval.TICK
start: datetime = datetime(2024, 8, 1, tzinfo=CHINA_TZ)
end: datetime = datetime.now().astimezone(CHINA_TZ)

def download_data(symbol: str, exchange: Exchange, interval: Interval, start: datetime, end: datetime) -> bool:
    """下载并将数据写入数据库"""
    req = HistoryRequest(
        symbol = symbol,
        exchange = exchange,
        interval = interval,
        start = start,
        end = end
    )
    
    bars: List[BarData] = datafeed.query_tick_history(req)
    if bars:
        database.save_tick_data(bars)
        return True
    else:
        return False

def get_products() -> Set[Tuple[str, Exchange]]:
    """查询期货品种信息"""
    products = set()
    
    df = rqdatac.all_instruments(type = "Future")
    for _, row in df.iterrows():
        product = (row.underlying_symbol, Exchange(row.exchange))
        products.add(product)
        
    return products

def run_task() -> None:
    """执行遍历下载任务"""
    products: set = get_products()
    success: list = []
    fail: list = []
    
    for prefix, exchange in products:
        if exchange in {Exchange.DCE, Exchange.SHFE, Exchange.INE}:
            prefix = prefix.lower()
            
        if exchange == Exchange.GFEX:
            continue
            
        for suffix in suffix_list:
            symbol = prefix + suffix

            vt_symbol = symbol + '.' + exchange.value
            if vt_symbol not in vt_symbols:
                continue

            print("开始下载", vt_symbol)
            r = download_data(symbol, exchange, interval, start, end)
            if r:
                success.append(symbol)
                print("下载成功", vt_symbol)
            else:
                fail.append(symbol)
                
    if success:
        print("下载成功", success)
    
    if fail:
        print("下载失败", fail)
        
vt_symbols = ["IF2409.CFFEX"]

run_task()
