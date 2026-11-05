"""PyPI・GA4の収集、CSV履歴管理、解析を提供する公開ライブラリ。"""
from .analysis import TimeSeries
from .analytics_api import GA4Analytics, PyPIAnalytics, UsageAnalytics
from .collection import CollectionJob, GA4Collector, PyPICollector, make_collectors
from .history import CSVHistory, GitHistorySync
from .settings import Settings
__version__ = "0.0.0"
