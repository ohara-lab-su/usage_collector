"""PyPI Stats APIからのダウンロード統計収集。"""
from pathlib import Path
import requests
from .csv_store import merge_csv

REPORTS = {"overall": "overall", "python_major": "python_major", "python_minor": "python_minor", "system": "system"}

def collect(packages, directory, session=None):
    session = session or requests.Session()
    total = 0
    for report in REPORTS:
        records = []
        for package in packages:
            response = session.get(f"https://pypistats.org/api/packages/{package}/{report}", timeout=30)
            response.raise_for_status()
            payload = response.json()
            for row in payload.get("data", []):
                if not isinstance(row, dict) or "date" not in row:
                    continue
                category = row.get("category", "")
                if report == "overall" and category not in ("with_mirrors", "without_mirrors"):
                    continue
                records.append({"date": row["date"], "package": package, "category": category, "downloads": row.get("downloads", 0)})
        merge_csv(Path(directory) / "pypi" / f"{report}.csv", records,
                  ["date", "package", "category", "downloads"],
                  ["date", "package", "category"])
        total += len(records)
    return total
