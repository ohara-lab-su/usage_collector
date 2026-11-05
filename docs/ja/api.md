# Python APIリファレンス

[ホーム](index.md) · [English](../en/api.md)

## 収集

`PyPICollector(packages, directory, session=None).collect()` はPyPI Statsの4系列を収集してCSVへマージし、取得行数を返します。`GA4Collector(property_id, directory, days=3, client=None).collect()` は7レポートを取得します。`CollectionJob({name: collector}).collect()` は名前と行数の辞書を返します。`make_collectors(settings, directory, source='all', ga4_days=3, skip_unconfigured_ga4=True)` は設定から収集器を構成します。

## 低レベルAPI

`pypi.PyPIStatsClient(session=None).fetch(package, dimension)`、`ga4.GA4ReportClient(client, property_id).fetch(name, start_date, end_date)` はAPIから行の辞書を取得します。GA4レポート名は `daily, pages, countries, regions, cities, sources, devices`。

## 履歴と解析

`CSVHistory(directory).read(source, name)` は行の辞書配列を返します。`TimeSeries(rows).group(dimensions, metric, start=None, end=None)` は日付別に合算します。`PyPIAnalytics(history).downloads(report='overall', start=None, end=None)` はPyPI統計、`GA4Analytics(history).report(name='daily', metric='sessions', start=None, end=None)` はGA4統計です。GA4で利用できる指標はレポートごとに異なります。

```python
from usage_collector import CSVHistory, PyPIAnalytics, GA4Analytics
h = CSVHistory('data')
print(PyPIAnalytics(h).downloads('system'))
print(GA4Analytics(h).report('cities', 'activeUsers'))
```

## GUI拡張

`AnalyticsApplication(history).show(save=None)` はPyPI/GA4の2画面を表示します。`create_window('pypi'|'ga4')` は既存Qtアプリに組み込める `AnalyticsWindow` を返します。`AnalyticsWindow` を継承して表示を拡張できます。GUIを利用しない解析には上記のAPIを使ってください。

## 制約

GA4のCSVにプロパティID列がないため、複数プロパティは保存ディレクトリを分けてください。Collectorは現状CSV保存を内包しており、完全なStorage抽象化は未実装です。
