from pathlib import Path
from importlib.resources import files
import subprocess
import sys
import os
from usage_collector.cli import SCRIPTS


def test_script_resources():
    for name in SCRIPTS.values():
        assert files("usage_collector").joinpath("scripts", name).is_file()


def test_run_plot_help(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c", "from usage_collector.cli import main; import sys; sys.argv=['usage_collector','run','plot','--help']; main()"],
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}, capture_output=True, text=True, check=True)
    assert "--refresh" in result.stdout
    assert not (tmp_path / "plot.py").exists()


def test_run_collect_help(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c", "from usage_collector.cli import main; import sys; sys.argv=['usage_collector','run','collect','--help']; main()"],
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}, capture_output=True, text=True, check=True)
    assert "--ga4-days" in result.stdout
    assert not (tmp_path / "collect.py").exists()
