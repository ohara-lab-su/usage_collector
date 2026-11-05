"""ローカルGitリポジトリでCSV同期を検証する。"""
import subprocess
from usage_collector.history import CSVHistory, GitHistorySync

def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()

def check_sync(tmp_path, prefix):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "test")
    directory = repo / prefix / "ga4"
    directory.mkdir(parents=True)
    (directory / "daily.csv").write_text("date,sessions\n2026-01-01,12\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "data")
    git(repo, "branch", "data")
    history = CSVHistory(tmp_path / "local")
    assert GitHistorySync(history, remote=".", branch="data", repository=repo).sync() == 1
    assert history.read("ga4", "daily")[0]["sessions"] == "12"

def test_root(tmp_path):
    check_sync(tmp_path, "")

def test_nested(tmp_path):
    check_sync(tmp_path, "data")


def test_double_nested(tmp_path):
    check_sync(tmp_path, "data/data")


def test_remote_tracking_independent_of_fetch_head(tmp_path):
    """FETCH_HEADの内容や既存の追跡ブランチに依存せず取得する。"""
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "-q")
    git(source, "config", "user.email", "test@example.com")
    git(source, "config", "user.name", "test")
    folder = source / "data" / "pypi"
    folder.mkdir(parents=True)
    (folder / "overall.csv").write_text(
        "date,package,dimension,category,downloads\n2026-11-01,example,overall,without_mirrors,9\n"
    )
    git(source, "add", ".")
    git(source, "commit", "-qm", "initial")
    git(source, "branch", "data")
    destination = tmp_path / "checkout"
    subprocess.run(["git", "clone", "-q", str(source), str(destination)], check=True)
    # FETCH_HEADを別ブランチのfetchで変更する。
    git(destination, "fetch", "origin", "HEAD")
    history = CSVHistory(tmp_path / "csv")
    sync = GitHistorySync(history, remote="origin", branch="data", repository=destination)
    assert sync.sync() == 1
    assert history.read("pypi", "overall")[0]["downloads"] == "9"


def test_empty_remote_branch_rejected(tmp_path):
    """空の最新ブランチを古いデータで黙って置き換えない。"""
    import pytest
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "-q")
    git(source, "config", "user.email", "test@example.com")
    git(source, "config", "user.name", "test")
    folder = source / "data" / "ga4"
    folder.mkdir(parents=True)
    (folder / "daily.csv").write_text("date,sessions\n2026-11-05,3\n")
    git(source, "add", ".")
    git(source, "commit", "-qm", "with data")
    git(source, "branch", "data")
    checkout = tmp_path / "checkout"
    subprocess.run(["git", "clone", "-q", str(source), str(checkout)], check=True)
    git(source, "checkout", "-q", "data")
    git(source, "rm", "-qr", "data")
    git(source, "commit", "-qm", "empty data")
    history = CSVHistory(tmp_path / "cache")
    with pytest.raises(RuntimeError, match="CSVがありません"):
        GitHistorySync(history, repository=checkout).sync()


def test_script_resolves_project_data_independent_of_cwd(tmp_path, monkeypatch):
    """PyCharmが別ディレクトリをcwdにしても、スクリプト位置からdataを発見する。"""
    import runpy
    import sys
    from pathlib import Path
    from usage_collector.application import AnalyticsApplication
    from usage_collector.history import GitHistorySync

    root = tmp_path / "project"
    script = root / "src" / "usage_collector" / "scripts" / "plot.py"
    script.parent.mkdir(parents=True)
    source = Path(__file__).resolve().parents[1] / "src" / "usage_collector" / "scripts" / "plot.py"
    script.write_bytes(source.read_bytes())
    (root / "pyproject.toml").write_text('[project]\nname="test"\nversion="0.0.0"\n')
    folder = root / "data" / "pypi"
    folder.mkdir(parents=True)
    (folder / "overall.csv").write_text("date,downloads\n2026-11-05,4\n")
    other = tmp_path / "unrelated"
    other.mkdir()
    monkeypatch.chdir(other)
    monkeypatch.setattr(sys, "argv", [str(script)])
    def unexpected_sync(self):
        raise AssertionError("既存CSVがあるのにGit同期が呼ばれた")
    monkeypatch.setattr(GitHistorySync, "sync", unexpected_sync)
    captured = []
    monkeypatch.setattr(AnalyticsApplication, "show", lambda self, save=None: captured.append(self.history.directory))
    runpy.run_path(str(script), run_name="__main__")
    assert captured == [root / "data"]
