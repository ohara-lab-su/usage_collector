"""CSV履歴更新のテスト。"""
import csv
from usage_collector.csv_store import merge_csv


def test_history_preserved(tmp_path):
    path = tmp_path / "data.csv"
    fields = ["date", "value"]
    merge_csv(path, [{"date": "2026-01-01", "value": 2}], fields, ["date"])
    merge_csv(path, [{"date": "2026-01-02", "value": 3}], fields, ["date"])
    merge_csv(path, [{"date": "2026-01-02", "value": 5}], fields, ["date"])
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert rows == [{"date": "2026-01-01", "value": "2"},
                    {"date": "2026-01-02", "value": "5"}]


def test_empty_does_not_destroy_history(tmp_path):
    path = tmp_path / "data.csv"
    merge_csv(path, [{"date": "2026-01-01", "value": 2}], ["date", "value"], ["date"])
    before = path.read_bytes()
    merge_csv(path, [], ["date", "value"], ["date"])
    assert path.read_bytes() == before
