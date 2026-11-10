# Installation and deployment

[Home](index.md) · [日本語](../ja/installation.md)

Requires Python >=3.10. From the public source repository run `python -m pip install .`. Normal dependencies include PySide6, matplotlib, requests, PyYAML and Google Analytics Data API libraries.

Run `usage_collector install scripts` in your operations directory to create editable `scripts/collect.py`, `scripts/plot.py`, `scripts/settings.yml`, and `collect.yml`. Installation aborts if any target exists.

Place the workflow at `.github/workflows/collect.yml` on the private repository's protected `main` branch. It installs the public package and pushes CSV files only to the private `data` branch. Add the `GOOGLE_CREDENTIALS_JSON` Actions secret and `GA4_PROPERTY_ID` variable. Grant the service account GA4 property read access. Ensure Actions may write to the `data` branch.

Local GA4 access uses Google ADC; `GOOGLE_APPLICATION_CREDENTIALS` may point to a JSON key. Never commit credentials. PyPI Stats requires no authentication.
