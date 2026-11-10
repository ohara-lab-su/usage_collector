# クイックスタート

[ホーム](index.md) · [English](../en/quickstart.md)

```bash
python -m pip install .
usage_collector install scripts
python scripts/collect.py --config scripts/settings.yml --source pypi --output data
python scripts/plot.py --data data
```

`scripts/settings.yml` の `pypi.packages` を自分のパッケージに変更してください。GA4収集にはプロパティIDとADCが必要です。

```bash
python scripts/collect.py --source ga4 --ga4-days 3 --output data
python scripts/plot.py --data data --fetch --repository . --branch data
```

`--fetch` はGitリポジトリのdataブランチからCSVを取り込みます。Git同期を使わずローカルCSVを直接表示することもできます。

`usage_collector install collect` / `install plot` は個別の編集可能スクリプトをコピーします。`usage_collector run collect --source pypi` は同梱スクリプトを一時実行します。
