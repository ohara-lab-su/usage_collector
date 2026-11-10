"""CSV履歴の読み込みとGitブランチからの取得。"""
import csv
import subprocess
import tempfile
from pathlib import Path

class CSVHistory:
    def __init__(self, directory):
        self.directory = Path(directory)

    def exists(self):
        return any(self.directory.glob("*/*.csv"))

    def read(self, source, report):
        path = self.directory / source / (report + ".csv")
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))

class GitHistorySync:
    def __init__(self, history, remote="origin", branch="data", repository=None):
        self.history = history
        self.remote = remote
        self.branch = branch
        self.repository = Path(repository or Path.cwd())

    def sync(self):
        subprocess.run(["git", "fetch", self.remote, self.branch], cwd=self.repository, check=True)
        with tempfile.TemporaryDirectory() as temp:
            archive = subprocess.run(["git", "archive", "--format=tar", "FETCH_HEAD", "data"],
                                     cwd=self.repository, check=True, capture_output=True).stdout
            import io
            import tarfile
            with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
                for member in stream.getmembers():
                    if not member.isfile() or not member.name.startswith("data/") or not member.name.endswith(".csv"):
                        continue
                    relative = Path(member.name).relative_to("data")
                    target = self.history.directory / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with stream.extractfile(member) as source, target.open("wb") as dest:
                        dest.write(source.read())
