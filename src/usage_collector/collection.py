"""収集処理の部品。GUIやスクリプトへの依存を持たない。"""
import os
from pathlib import Path
from . import pypi, ga4

class PyPICollector:
    def __init__(self, packages, directory, session=None):
        self.packages = list(packages)
        self.directory = Path(directory)
        self.session = session

    def collect(self):
        return pypi.collect(self.packages, self.directory, session=self.session)

class GA4Collector:
    def __init__(self, property_id, directory, days=3, client=None):
        self.property_id = property_id
        self.directory = Path(directory)
        self.days = days
        self.client = client

    def collect(self):
        if not self.property_id:
            raise ValueError("GA4_PROPERTY_ID が未設定です")
        return ga4.collect(self.property_id, self.directory, days=self.days, client=self.client)

class CollectionJob:
    def __init__(self, collectors):
        self.collectors = dict(collectors)

    def collect(self):
        result = {}
        for name, collector in self.collectors.items():
            result[name] = collector.collect()
        return result

def make_collectors(settings, directory, source="all", ga4_days=3, skip_unconfigured_ga4=False):
    result = {}
    if source in ("all", "pypi"):
        result["pypi"] = PyPICollector(settings.get("pypi", {}).get("packages", []), directory)
    if source in ("all", "ga4"):
        property_id = os.environ.get("GA4_PROPERTY_ID")
        if not property_id:
            property_id = settings.get("ga4", {}).get("property_id")
        if property_id:
            result["ga4"] = GA4Collector(property_id, directory, ga4_days)
        elif not skip_unconfigured_ga4:
            raise ValueError("GA4_PROPERTY_ID が未設定です")
    return result
