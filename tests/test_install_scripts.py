from pathlib import Path
from unittest.mock import patch
import pytest
from usage_collector.cli import main


def test_install_scripts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("sys.argv", ["usage_collector", "install", "scripts"]):
        assert main() == 0
    assert (tmp_path / "scripts/collect.py").exists()
    assert (tmp_path / "scripts/plot.py").exists()
    assert (tmp_path / "config/settings.yml").exists()
    assert (tmp_path / "collect.yml").exists()
    with patch("sys.argv", ["usage_collector", "install", "scripts"]):
        with pytest.raises(SystemExit):
            main()
