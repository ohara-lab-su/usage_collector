#!/usr/bin/env python
"""編集可能な収集アプリケーション。部品を組み合わせて収集対象を変更できる。"""
import argparse
import sys

# ソースツリーからスクリプトを直接実行した場合もライブラリを解決する。
from pathlib import Path as _Path
_source_root = _Path(__file__).resolve().parents[2]
if (_source_root / "usage_collector").is_dir():
    if str(_source_root) not in sys.path:
        sys.path.insert(0, str(_source_root))
from pathlib import Path
from usage_collector.settings import Settings
from usage_collector.collection import CollectionJob, make_collectors

parser = argparse.ArgumentParser(description="PyPI・GA4統計をCSVへ収集")
parser.add_argument("--config", default=None)
parser.add_argument("--output", default="data")
parser.add_argument("--source", choices=("all", "pypi", "ga4"), default="all")
parser.add_argument("--ga4-days", type=int, default=3)
args = parser.parse_args()
if args.ga4_days < 1:
    parser.error("--ga4-days は1以上を指定してください")

# 設定や対象の組み合わせは、このスクリプトを編集して自由に変更できる。
settings = Settings(args.config).load()
directory = Path(args.output)
collectors = make_collectors(settings, directory, args.source, args.ga4_days,
                             skip_unconfigured_ga4=(args.source != "ga4"))
if args.source == "all":
    if "ga4" not in collectors:
        print("GA4: プロパティID未設定のためスキップ", flush=True)
job = CollectionJob(collectors)
results = job.collect()
for source, count in results.items():
    print("{}: {} 行".format(source, count), flush=True)
