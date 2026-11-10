# Quick start

[Home](index.md) · [日本語](../ja/quickstart.md)

```bash
python -m pip install .
usage_collector install scripts
python scripts/collect.py --config scripts/settings.yml --source pypi --output data
python scripts/plot.py --data data
```

Edit `pypi.packages` in `scripts/settings.yml`. GA4 requires a property ID and ADC.

```bash
python scripts/collect.py --source ga4 --ga4-days 3 --output data
python scripts/plot.py --data data --fetch --repository . --branch data
```

`--fetch` imports CSV from the Git data branch; local CSV analysis does not require Git. `usage_collector install collect` and `install plot` install individual editable scripts. `usage_collector run collect --source pypi` runs a packaged script without copying it.
