"""GUI非依存のPyPI・GA4履歴解析API。"""
from .analysis import TimeSeries
from .history import CSVHistory

class UsageAnalytics:
    """CSV履歴から集計系列を取得する共通API。"""
    def __init__(self, history):
        self.history = history

    def rows(self, source, report):
        return self.history.read(source, report)

    def series(self, source, report, dimensions, metric, start=None, end=None):
        return TimeSeries(self.rows(source, report)).group(dimensions, metric, start, end)

class PyPIAnalytics(UsageAnalytics):
    """PyPI統計のパッケージ別・環境別解析。"""
    REPORTS = ('overall', 'python_major', 'python_minor', 'system')

    def downloads(self, report='overall', start=None, end=None):
        if report not in self.REPORTS:
            raise ValueError('未知のPyPIレポート: ' + report)
        return self.series('pypi', report, ('package', 'category'), 'downloads', start, end)

class GA4Analytics(UsageAnalytics):
    """GA4統計の指標・ディメンション別解析。"""
    REPORTS = {
        'daily': ('sessions', 'activeUsers', 'screenPageViews'),
        'pages': ('screenPageViews',),
        'countries': ('sessions', 'activeUsers'),
        'regions': ('sessions', 'activeUsers'),
        'cities': ('sessions', 'activeUsers'),
        'sources': ('sessions',),
        'devices': ('sessions',),
    }
    DIMENSIONS = {
        'daily': (), 'pages': ('pagePath',), 'countries': ('country',),
        'regions': ('country','region'), 'cities': ('country','region','city'),
        'sources': ('sessionSourceMedium',), 'devices': ('deviceCategory',),
    }

    def report(self, name='daily', metric='sessions', start=None, end=None):
        if name not in self.REPORTS or metric not in self.REPORTS[name]:
            raise ValueError(f'未対応のGA4レポート/指標: {name}/{metric}')
        return self.series('ga4', name, self.DIMENSIONS[name], metric, start, end)
