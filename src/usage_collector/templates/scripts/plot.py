#!/usr/bin/env python
"""非公開リポジトリのdataブランチのCSVをローカルに取得して表示する。"""
import argparse
from pathlib import Path
from usage_collector.history import CSVHistory, GitHistorySync
from usage_collector.application import AnalyticsApplication


def main():
    parser = argparse.ArgumentParser(description="PyPI・GA4解析")
    parser.add_argument("--data", default="data")
    parser.add_argument("--repository", default=".")
    parser.add_argument("--branch", default="data")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--save", default=None)
    args = parser.parse_args()
    history = CSVHistory(Path(args.data))
    if args.fetch:
        GitHistorySync(history, branch=args.branch, repository=args.repository).sync()
    if not history.exists():
        parser.error("CSVがありません。--fetch で非公開dataブランチから取得してください")
    AnalyticsApplication(history).show(save=args.save)


if __name__ == "__main__":
    main()
