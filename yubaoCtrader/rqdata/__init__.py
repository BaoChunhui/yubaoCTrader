import importlib_metadata

from .rqdata_datafeed import RqdataDatafeed as Datafeed
from .rqdata_gateway import RqdataGateway


try:
    __version__ = importlib_metadata.version("yubaoCtrader_rqdata")
except importlib_metadata.PackageNotFoundError:
    __version__ = "dev"
