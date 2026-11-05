"""Google Analytics Data APIからの時系列取得。認証方式は固定しない。"""
from datetime import date, timedelta
from pathlib import Path
from .csv_store import merge_csv

REPORTS = {
    "daily": (["date"], ["sessions", "activeUsers", "screenPageViews"]),
    "pages": (["date", "pagePath"], ["screenPageViews"]),
    "countries": (["date", "country"], ["sessions", "activeUsers"]),
    "regions": (["date", "country", "region"], ["sessions", "activeUsers"]),
    "cities": (["date", "country", "region", "city"], ["sessions", "activeUsers"]),
    "sources": (["date", "sessionSourceMedium"], ["sessions"]),
    "devices": (["date", "deviceCategory"], ["sessions"]),
}


def fetch(client, property_id, name, start_date, end_date, limit=10000):
    """公式クライアントでページングし、日別行を取得する。"""
    from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
    dimensions, metrics = REPORTS[name]
    rows = []
    offset = 0
    while True:
        request = RunReportRequest(
            property="properties/" + str(property_id),
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name=value) for value in dimensions],
            metrics=[Metric(name=value) for value in metrics],
            limit=limit, offset=offset,
        )
        response = client.run_report(request)
        for item in response.rows:
            record = {"date": ""}
            for index, field in enumerate(dimensions):
                value = item.dimension_values[index].value
                if field == "date":
                    value = value[:4] + "-" + value[4:6] + "-" + value[6:]
                record[field] = value
            for index, field in enumerate(metrics):
                record[field] = item.metric_values[index].value
            rows.append(record)
        offset += len(response.rows)
        if offset >= response.row_count:
            break
        if len(response.rows) == 0:
            raise RuntimeError("GA4ページングが途中で停止しました")
    return rows


def collect(property_id, directory, days=30, client=None):
    """認証情報はGoogle標準のADCから取得し、明示クライアントも受け入れる。"""
    if client is None:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        client = BetaAnalyticsDataClient()
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    total = 0
    for name, (dimensions, metrics) in REPORTS.items():
        path = Path(directory) / "ga4" / (name + ".csv")
        report_start = start
        if not path.exists():
            report_start = end - timedelta(days=29)
        rows = fetch(client, property_id, name,
                     report_start.isoformat(), end.isoformat())
        fields = dimensions + metrics
        merge_csv(path, rows, fields, dimensions)
        total += len(rows)
    return total


class GA4ReportClient:
    def __init__(self, client, property_id):
        self.client = client
        self.property_id = property_id

    def fetch(self, name, start_date, end_date):
        return fetch(self.client, self.property_id, name, start_date, end_date)
