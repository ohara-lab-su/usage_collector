"""明示設定、プロジェクト設定、同梱設定を順に解決する。"""
from importlib.resources import files
from pathlib import Path
import yaml

class Settings:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else None

    def load(self):
        if self.path is not None:
            if not self.path.is_file():
                raise FileNotFoundError(str(self.path))
            text = self.path.read_text(encoding="utf-8")
        else:
            local = Path.cwd() / "config" / "settings.yml"
            if local.is_file():
                text = local.read_text(encoding="utf-8")
            else:
                text = files("usage_collector").joinpath("settings.yml").read_text(encoding="utf-8")
        result = yaml.safe_load(text)
        if not isinstance(result, dict):
            raise ValueError("設定ファイルのルートはマッピングである必要があります")
        return result
