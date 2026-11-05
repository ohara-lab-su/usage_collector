#!/usr/bin/env python
"""スクリプトの配置と、同じスクリプトのコピー不要な試験実行。"""
import argparse
import runpy
import sys
from importlib.resources import as_file, files
from pathlib import Path

SCRIPTS = {"plot": "plot.py", "collect": "collect.py"}


def main():
    parser = argparse.ArgumentParser(description="usage_collector スクリプト管理")
    subparsers = parser.add_subparsers(dest="command", required=True)
    install = subparsers.add_parser("install", help="スクリプトをカレントディレクトリへコピー")
    install.add_argument("script", choices=sorted(SCRIPTS) + ["scripts"])
    run = subparsers.add_parser("run", help="コピーせず同一スクリプトを実行")
    run.add_argument("script", choices=sorted(SCRIPTS))
    arguments = sys.argv[1:]
    if len(arguments) >= 2:
        if arguments[0] == "run":
            args = parser.parse_args(arguments[:2])
            extra = arguments[2:]
        else:
            args = parser.parse_args(arguments)
            extra = []
    else:
        args = parser.parse_args(arguments)
        extra = []
    if args.command == "install":
        if extra:
            parser.error("install に余分な引数があります: " + " ".join(extra))
        if args.script == "scripts":
            resources = files("usage_collector").joinpath("templates")
            targets = {
                "scripts/collect.py": resources.joinpath("scripts", "collect.py"),
                "scripts/plot.py": resources.joinpath("scripts", "plot.py"),
                "config/settings.yml": resources.joinpath("config", "settings.yml"),
                "collect.yml": resources.joinpath("collect.yml"),
            }
            existing = [str(Path.cwd() / name) for name in targets if (Path.cwd() / name).exists()]
            if existing:
                parser.error("既存ファイルがあるため何も作成しません: " + ", ".join(existing))
            for name, resource in targets.items():
                destination = Path.cwd() / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(resource.read_bytes())
                print("作成:", destination)
            print("collect.yml を .github/workflows/collect.yml に配置し、OWNERと設定を変更してください")
            return 0
        name = SCRIPTS[args.script]
        destination = Path.cwd() / name
        if destination.exists():
            parser.error("既存ファイルは上書きしません: " + str(destination))
        resource = files("usage_collector").joinpath("scripts", name)
        destination.write_bytes(resource.read_bytes())
        print("作成:", destination)
        return 0
    if args.command == "run":
        resource = files("usage_collector").joinpath("scripts", SCRIPTS[args.script])
        with as_file(resource) as script:
            original = sys.argv
            try:
                sys.argv = [str(script)] + extra
                runpy.run_path(str(script), run_name="__main__")
            finally:
                sys.argv = original
        return 0
    parser.error("不明なサブコマンド")


if __name__ == "__main__":
    raise SystemExit(main())
