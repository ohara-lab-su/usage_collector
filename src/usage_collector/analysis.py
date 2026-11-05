"""収集済みデータの集計。GUIに依存しない。"""
from collections import defaultdict

class TimeSeries:
    def __init__(self, rows):
        self.rows = list(rows)

    def group(self, dimensions, metric, start=None, end=None):
        result = defaultdict(lambda: defaultdict(float))
        for row in self.rows:
            day = row.get("date", "")
            if start is not None:
                if day < start:
                    continue
            if end is not None:
                if day > end:
                    continue
            key = tuple(row.get(field, "") for field in dimensions)
            try:
                value = float(row.get(metric, 0))
            except (ValueError, TypeError):
                continue
            result[key][day] += value
        return {key: dict(sorted(days.items())) for key, days in result.items()}
