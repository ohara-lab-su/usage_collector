"""収集オブジェクトの組み合わせとスクリプト起動を検証する。"""
import subprocess
import sys
from pathlib import Path
from usage_collector.collection import CollectionJob, make_collectors

def test_job():
    class Dummy:
        def collect(self):
            return 5
    assert CollectionJob({"pypi": Dummy()}).collect() == {"pypi": 5}

def test_missing_ga4(tmp_path):
    settings = {"pypi": {"packages": []}, "ga4": {"property_id": None}}
    import os
    from unittest.mock import patch
    with patch.dict(os.environ, {"GA4_PROPERTY_ID": ""}):
        assert "ga4" not in make_collectors(settings, tmp_path)

def test_editable_script_collect(tmp_path):
    root = Path(__file__).resolve().parents[1]
    config = tmp_path / "settings.yml"
    config.write_text("pypi:\n  packages: []\nga4:\n  property_id: null\n", encoding="utf-8")
    script = root / "src" / "usage_collector" / "scripts" / "collect.py"
    result = subprocess.run([sys.executable, str(script), "--config", str(config), "--source", "pypi", "--output", str(tmp_path / "data")], cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "pypi: 0 行" in result.stdout
