"""CSV履歴の管理と、Git上の収集データの読み込み。"""
import csv
import io
import subprocess
from pathlib import Path

from .csv_store import merge_csv


class CSVHistory:
    def __init__(self, directory):
        self.directory = Path(directory)

    def read(self, source, name):
        path = self.directory / source / (name + ".csv")
        if not path.is_file():
            return []
        with path.open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))

    def exists(self):
        return any(self.directory.rglob("*.csv"))

    def merge(self, relative, rows):
        if not rows:
            return 0
        fields = list(rows[0])
        metrics = {"downloads", "sessions", "activeUsers", "screenPageViews"}
        keys = [field for field in fields if field not in metrics]
        return merge_csv(self.directory / relative, rows, fields, keys)


class GitHistorySync:
    """指定リポジトリのdataブランチからCSVを読み出す。作業ツリーは変更しない。"""

    def __init__(self, history, remote="origin", branch="data", repository=None):
        self.history = history
        self.remote = remote
        self.branch = branch
        self.repository = Path(repository).resolve() if repository is not None else Path.cwd().resolve()

    def _git(self, *args, binary=False):
        result = subprocess.run(["git", "-C", str(self.repository), *args],
                                capture_output=True, check=False)
        if result.returncode:
            message = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"git {' '.join(args)}: {message}")
        if binary:
            return result.stdout
        return result.stdout.decode("utf-8", errors="replace").strip()

    @staticmethod
    def _relative_csv(name):
        parts = Path(name).parts
        for index, component in enumerate(parts):
            if component in ("pypi", "ga4") and index == len(parts) - 2:
                if parts[-1].lower().endswith(".csv"):
                    return Path(component) / parts[-1]
        return None

    def sync(self):
        """リモート追跡参照を明示的に更新し、その参照からCSVを取得する。"""
        if not (self.repository / ".git").exists():
            raise RuntimeError(f"Gitリポジトリがありません: {self.repository}")
        tracking = f"refs/usage_collector/{self.branch}"
        source = f"refs/heads/{self.branch}"
        # fetch先をorigin/dataに固定する。FETCH_HEADや現在の作業ブランチは参照しない。
        self._git("fetch", "--no-tags", self.remote, f"+{source}:{tracking}")
        commit = self._git("rev-parse", "--verify", f"{tracking}^{{commit}}")
        names = self._git("ls-tree", "-r", "-z", "--name-only", commit, binary=True)
        paths = [item.decode("utf-8") for item in names.split(b"\0") if item]
        selected = [(name, self._relative_csv(name)) for name in paths]
        selected = [(name, rel) for name, rel in selected if rel is not None]
        if not selected:
            raise RuntimeError(f"{tracking} ({commit[:12]}) にCSVがありません。"
                               f"リポジトリ: {self.repository}、Gitツリー: {paths[:15]}")
        count = 0
        for name, relative in selected:
            data = self._git("show", f"{commit}:{name}", binary=True)
            rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
            if rows:
                self.history.merge(relative, rows)
                count += 1
        if not count:
            raise RuntimeError(f"{tracking} のCSV {len(selected)}件にデータ行がありません")
        return count
