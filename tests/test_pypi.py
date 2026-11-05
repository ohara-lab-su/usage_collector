"""PyPI Statsの正常・異常応答テスト。"""
import pytest
from usage_collector.pypi import fetch


class Response:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return {"data": self.data}


class Session:
    def __init__(self, data):
        self.data = data

    def get(self, url, timeout):
        return Response(self.data)


def test_mirror_filter():
    data = [{"date": "2026-01-01", "category": "with_mirrors", "downloads": 4},
            {"date": "2026-01-01", "category": "without_mirrors", "downloads": 3}]
    result = fetch("example", "overall", session=Session(data))
    assert len(result) == 1
    assert result[0]["downloads"] == 3


def test_malformed_response():
    with pytest.raises(ValueError):
        fetch("example", "overall", session=Session({"invalid": 1}))


def test_partial_http_error_keeps_other_series(tmp_path):
    import requests
    from usage_collector.pypi import collect
    class PartialSession:
        def get(self, url, timeout):
            if url.endswith("/system"):
                raise requests.HTTPError("502 Bad Gateway")
            return Response([{"date": "2026-11-01", "category": "without_mirrors", "downloads": 2}])
    assert collect(["example"], tmp_path, session=PartialSession()) == 3
    assert (tmp_path / "pypi" / "overall.csv").exists()
    assert not (tmp_path / "pypi" / "system.csv").exists()


def test_all_http_errors_raise(tmp_path):
    import requests
    from usage_collector.pypi import collect
    class BrokenSession:
        def get(self, url, timeout):
            raise requests.HTTPError("502 Bad Gateway")
    with pytest.raises(RuntimeError, match="全系列"):
        collect(["example"], tmp_path, session=BrokenSession())


def test_retry_policy():
    from usage_collector.pypi import create_session
    retry = create_session().get_adapter("https://").max_retries
    assert 502 in retry.status_forcelist
    assert 429 in retry.status_forcelist
    assert retry.total == 5
