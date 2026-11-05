# usage_collector

`usage_collector` is a reusable Python library for collecting PyPI Stats and Google Analytics 4 (GA4) reports, maintaining CSV histories, analyzing time series, and visualizing them with PySide6. It is independent of the private repository where actual data and credentials are stored. Version: `0.0.0` (pre-release). Python >=3.10.

## Architecture

The public library implements `collection.py` (collectors and orchestration), `pypi.py` and `ga4.py` (provider APIs), `csv_store.py` and `history.py` (CSV upsert and optional Git sync), `analysis.py` and `analytics_api.py` (headless analytics), `application.py` and `gui.py` (GUI), and `cli.py` (editable script installation). Operational configuration and collected CSV files belong in a separate **private** `usage_collector_data` repository.

The collectors currently write CSV files to a supplied directory; they are not fully storage-agnostic. `GitHistorySync` is optional, and Git synchronization is not required for local analysis.

## Installation

```bash
python -m pip install .
usage_collector install scripts
```

The second command creates editable `scripts/collect.py`, `scripts/plot.py`, `config/settings.yml`, and `collect.yml` in the current directory, refusing to overwrite existing files. Place `collect.yml` at `.github/workflows/collect.yml` in your private operations repository and replace `OWNER` in the installation URL. The standalone `usage_collector install collect` and `install plot` commands install the separate standalone execution scripts; `install scripts` installs editable operational templates.

## Quick start

Edit `config/settings.yml` to list PyPI packages and optionally a GA4 property ID.

```bash
python scripts/collect.py --source pypi --output data
python scripts/plot.py --data data
```

For GA4, set `GA4_PROPERTY_ID` and use Google Application Default Credentials (`GOOGLE_APPLICATION_CREDENTIALS` pointing to a service account JSON file is one option). Grant the service account read access to the GA4 property. Never commit credentials. In GitHub Actions, use the `GOOGLE_CREDENTIALS_JSON` secret and `GA4_PROPERTY_ID` variable in the **private** repository.

## Collection APIs

```python
from usage_collector import Settings, make_collectors, CollectionJob
settings = Settings('config/settings.yml').load()
collectors = make_collectors(settings, 'data', source='pypi')
print(CollectionJob(collectors).collect())
```

`PyPICollector(packages, directory, session=None)` and `GA4Collector(property_id, directory, days=3, client=None)` support dependency injection. The GA4 client uses the Google Analytics Data API; the PyPI client uses the public PyPI Stats endpoints (`overall`, `python_major`, `python_minor`, `system`). PyPI overall records exclude mirrors.

GA4 reports: `daily`, `pages`, `countries`, `regions`, `cities`, `sources`, and `devices`. Data is written as `data/pypi/*.csv` and `data/ga4/*.csv` with keyed upserts. For an absent GA4 report CSV, collection backfills 30 days; subsequent runs use the requested window.

## Analytics APIs

```python
from usage_collector import CSVHistory, PyPIAnalytics, GA4Analytics
history = CSVHistory('data')
print(PyPIAnalytics(history).downloads('python_minor'))
print(GA4Analytics(history).report('countries', 'sessions'))
print(GA4Analytics(history).report('pages', 'screenPageViews'))
```

Results map tuples of dimension values to date/value mappings. `TimeSeries(rows).group(dimensions, metric, start=None, end=None)` supports generic grouping. `CSVHistory.read(source, report)` returns CSV dictionaries. These APIs work without launching Qt.

## GUI and extensibility

```python
from usage_collector import CSVHistory
from usage_collector.application import AnalyticsApplication
app = AnalyticsApplication(CSVHistory('data'))
app.show()
# app.create_window('ga4') can be used in a host Qt application.
```

`gui.AnalyticsWindow(history, source)` is a PySide6 `QMainWindow` that may be subclassed. The host application must create/manage `QApplication` and the Qt event loop when using `create_window`. Existing visualization modes include PyPI package/Python/OS statistics and GA4 maps, trends, traffic sources, devices, and pages.

## Deployment and security

Keep `usage_collector` public and `usage_collector_data` private. In the private repository, retain protected `main` for scripts, configuration and the workflow, and `data` for collected CSVs. The workflow installs the public package and commits only to the private `data` branch. Public GitHub repositories must not contain GA4 data or historical secrets. `contents: write` is required for the private workflow to push to `data`; branch protection rules must permit this.

## Known limitations

The CSV schema currently does not include GA4 property ID, so multiple properties must use separate data directories. Git sync requires an accessible repository and remote and may require local troubleshooting. PyPI Stats is an external service with rate limits and possible reporting delays. `0.0.0` denotes pre-release status.

See [English docs](docs/en/index.md), [installation](docs/en/installation.md), [quick start](docs/en/quickstart.md), [API reference](docs/en/api.md), and [Japanese README](README.ja.md).


[Installation](installation.md) · [Quick start](quickstart.md) · [API](api.md) · [日本語](../ja/index.md)
