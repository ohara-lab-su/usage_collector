from usage_collector import __version__
from usage_collector.collection import make_collectors
import pytest

def test_version():
    assert __version__ == "0.0.1"

def test_missing_ga4_fails(tmp_path):
    with pytest.raises(ValueError):
        make_collectors({"pypi": {"packages": []}, "ga4": {"property_id": None}}, tmp_path, skip_unconfigured_ga4=False)
