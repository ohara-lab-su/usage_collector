#!/usr/bin/env python
"""編集可能な解析アプリケーション。データ同期・解析・GUIを組み合わせる。"""
import argparse
import sys

# ソースツリーからスクリプトを直接実行した場合もライブラリを解決する。
from pathlib import Path as _Path
_source_root = _Path(__file__).resolve().parents[2]
if (_source_root / "usage_collector").is_dir():
    if str(_source_root) not in sys.path:
        sys.path.insert(0, str(_source_root))
from pathlib import Path
from usage_collector.history import CSVHistory, GitHistorySync
from usage_collector.application import AnalyticsApplication
from usage_collector.settings import Settings
from usage_collector.collection import CollectionJob, make_collectors

parser = argparse.ArgumentParser(description="PyPI・GA4の解析GUI")
parser.add_argument("--branch", default="data")
parser.add_argument("--remote", default="origin")
parser.add_argument("--data", default=None)
parser.add_argument("--config", default=str(Path(__file__).resolve().parent / "settings.yml"))
parser.add_argument("--refresh", action="store_true")
parser.add_argument("--fetch", action="store_true")
parser.add_argument("--save", metavar="PNG")
args = parser.parse_args()

# ライブラリの表示スクリプトはローカルCSVを参照する。Git取得は明示指定時だけ行う。
project_root = Path(__file__).resolve().parents[1]
data_directory = Path(args.data).resolve() if args.data else project_root / "data"
history = CSVHistory(data_directory)
if args.fetch:
    GitHistorySync(history, remote=args.remote, branch=args.branch, repository=project_root).sync()
if not history.exists() and not args.refresh:
    parser.error(f"CSVがありません: {data_directory}。--data で指定するか、運用側で収集してください")

if args.refresh:
    settings = Settings(args.config).load()
    collectors = make_collectors(settings, history.directory)
    CollectionJob(collectors).collect()

# ここを編集すれば、別の表示クラスや独自の解析処理に置き換えられる。
application = AnalyticsApplication(history)
application.show(save=args.save)
