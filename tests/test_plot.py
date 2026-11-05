"""CSVとGUI起動サービスを検証する。"""
from usage_collector.history import CSVHistory
from usage_collector.analysis import TimeSeries
from usage_collector.application import AnalyticsApplication

def test_history_and_timeseries(tmp_path):
    source = tmp_path / "pypi"
    source.mkdir()
    (source / "overall.csv").write_text("date,package,downloads\n2026-11-01,a,3\n2026-11-02,b,4\n", encoding="utf-8")
    history = CSVHistory(tmp_path)
    assert history.exists()
    assert len(history.read("pypi", "overall")) == 2
    assert TimeSeries(history.read("pypi", "overall")).group(["package"], "downloads")[("a",)]["2026-11-01"] == 3
    assert AnalyticsApplication(history).history is history
