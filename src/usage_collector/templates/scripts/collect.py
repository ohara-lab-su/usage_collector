#!/usr/bin/env python
"""非公開リポジトリの設定に従ってPyPI/GA4データを収集する。"""
import argparse
from pathlib import Path
from usage_collector.settings import Settings
from usage_collector.collection import CollectionJob, make_collectors


def main():
    parser = argparse.ArgumentParser(description="PyPI・GA4収集")
    parser.add_argument("--config", default="config/settings.yml")
    parser.add_argument("--output", default="data")
    parser.add_argument("--source", choices=("pypi", "ga4", "all"), default="all")
    parser.add_argument("--ga4-days", type=int, default=3)
    args = parser.parse_args()
    if args.ga4_days < 1:
        parser.error("--ga4-days は1以上")
    settings = Settings(args.config).load()
    collectors = make_collectors(settings, Path(args.output), source=args.source,
                                 ga4_days=args.ga4_days,
                                 skip_unconfigured_ga4=args.source != "ga4")
    if not collectors:
        parser.error("有効な収集対象がありません")
    for source, count in CollectionJob(collectors).collect().items():
        print(f"{source}: {count} 行")


if __name__ == "__main__":
    main()
