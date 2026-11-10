"""運用設定ファイルの読み込み。"""
from pathlib import Path
import yaml

class Settings:
    def __init__(self, path):
        if path is None:
            raise ValueError("設定ファイルのパスを指定してください")
        self.path = Path(path)

    def load(self):
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        with self.path.open(encoding="utf-8") as stream:
            settings = yaml.safe_load(stream)
        if not isinstance(settings, dict):
            raise ValueError("設定ファイルの形式が不正です")
        return settings
