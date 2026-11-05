"""PyPI Stats公開APIからの時系列取得。"""
from urllib.parse import quote
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def create_session():
    """一時的なHTTP障害を再試行するセッション。"""
    session = requests.Session()
    retry = Retry(total=5, connect=5, read=5, status=5, backoff_factor=1.0,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=frozenset(("GET",)), respect_retry_after_header=True)
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session
from .csv_store import merge_csv

FIELDS = ["date", "package", "dimension", "category", "downloads"]
ENDPOINTS = ("overall", "python_major", "python_minor", "system")


def fetch(package, dimension, session=None):
    """APIが正常に応答した場合のみ行を返す。ゼロ件は正常として扱う。"""
    if dimension not in ENDPOINTS:
        raise ValueError("未知の集計区分: " + dimension)
    if session is None:
        session = create_session()
    url = "https://pypistats.org/api/packages/" + quote(package, safe="") + "/" + dimension
    response = session.get(url, timeout=45)
    response.raise_for_status()
    payload = response.json()
    data = payload["data"]
    if not isinstance(data, list):
        raise ValueError("PyPI Statsの応答形式が不正です")
    rows = []
    for item in data:
        category = item["category"]
        if dimension == "overall":
            if category != "without_mirrors":
                continue
        rows.append({"date": item["date"], "package": package,
                     "dimension": dimension, "category": str(category),
                     "downloads": int(item["downloads"])})
    return rows


def collect(packages, directory, session=None):
    """取得に成功した系列だけを保存し、一時的なHTTP障害では次の系列へ進む。"""
    from pathlib import Path
    if session is None:
        session = create_session()
    total = 0
    success = 0
    failures = []
    for package in packages:
        for dimension in ENDPOINTS:
            try:
                rows = fetch(package, dimension, session=session)
            except requests.RequestException as exc:
                failures.append((package, dimension, str(exc)))
                logger.warning("PyPI Stats取得失敗: %s / %s: %s", package, dimension, exc)
                continue
            path = Path(directory) / "pypi" / (dimension + ".csv")
            merge_csv(path, rows, FIELDS, ["date", "package", "dimension", "category"])
            total += len(rows)
            success += 1
    if failures:
        logger.warning("PyPI Stats: %d系列成功、%d系列失敗。失敗系列のCSVは保持", success, len(failures))
    if failures and success == 0:
        raise RuntimeError("PyPI Statsの全系列が取得できませんでした。最後のエラー: " + failures[-1][2])
    return total


class PyPIStatsClient:
    def __init__(self, session=None):
        self.session = session

    def fetch(self, package, dimension):
        return fetch(package, dimension, self.session)
