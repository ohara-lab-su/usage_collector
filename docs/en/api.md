# Python API reference

[Home](index.md) · [日本語](../ja/api.md)

## Collection

`PyPICollector(packages, directory, session=None).collect()` fetches four PyPI Stats series and upserts CSV, returning the fetched row count. `GA4Collector(property_id, directory, days=3, client=None).collect()` fetches seven GA4 reports. `CollectionJob({name: collector}).collect()` returns per-source counts. `make_collectors(settings, directory, source='all', ga4_days=3, skip_unconfigured_ga4=True)` creates configured collectors.

## Provider clients

`pypi.PyPIStatsClient(session=None).fetch(package, dimension)` and `ga4.GA4ReportClient(client, property_id).fetch(name, start_date, end_date)` fetch rows without saving them. GA4 report names: `daily, pages, countries, regions, cities, sources, devices`.

## Storage and analytics

`CSVHistory(directory).read(source, name)` returns dictionaries. `TimeSeries(rows).group(dimensions, metric, start=None, end=None)` aggregates values by date. `PyPIAnalytics(history).downloads(report='overall', start=None, end=None)` and `GA4Analytics(history).report(name='daily', metric='sessions', start=None, end=None)` provide domain-specific analysis. Supported GA4 metrics depend on the report.

```python
from usage_collector import CSVHistory, PyPIAnalytics, GA4Analytics
h = CSVHistory('data')
print(PyPIAnalytics(h).downloads('system'))
print(GA4Analytics(h).report('cities', 'activeUsers'))
```

## GUI extensions

`AnalyticsApplication(history).show(save=None)` opens both PyPI and GA4 windows. `create_window('pypi'|'ga4')` returns an `AnalyticsWindow` for integration into an existing Qt application. Subclass `AnalyticsWindow` to customize the GUI. Headless users can call the analytics APIs directly.

## Limitations

GA4 CSV does not include a property identifier; use separate directories for multiple properties. Collectors currently include CSV persistence, so full storage backend abstraction is not yet implemented.
