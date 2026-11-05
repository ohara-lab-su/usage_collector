# usage_collector

PyPI StatsとGoogle Analytics 4（GA4）の統計を収集・保存・解析するPythonライブラリ。バージョンは`0.0.0`。

このリポジトリは**公開ライブラリ専用**で、認証情報・実運用の対象パッケージ一覧・収集したCSV・GitHub Actionsの運用ワークフローを含めません。運用用リポジトリ`usage_collector_data`と独立しています。

## インストール

```sh
python -m pip install .
```

## モジュール

`usage_collector.collection`: `PyPICollector`、`GA4Collector`、`CollectionJob`、`make_collectors`。`usage_collector.pypi`と`usage_collector.ga4`はAPI取得とCSVへの保存、`usage_collector.csv_store`はCSVのキー付き更新、`usage_collector.history.CSVHistory`はCSV履歴の読み込みを担当します。`GitHistorySync`は明示的に指定したGitリポジトリのdataブランチからCSVを読み取る補助機能であり、収集・表示の必須依存ではありません。`usage_collector.analysis`と`usage_collector.application`は解析・GUI表示を担当します。

```python
from usage_collector.collection import PyPICollector, CollectionJob
CollectionJob({"pypi": PyPICollector(["example-package"], "data")}).collect()
```

`usage_collector run collect --config config/settings.yml --output data`で収集できます。`usage_collector run plot --data data`で既存CSVを表示できます。GUIはローカルCSVがない場合、**自動的にGit取得しません**。Git取得が必要な場合のみ`--fetch`を指定します。`usage_collector install collect`と`usage_collector install plot`で編集可能なスクリプトを出力できます。

## GA4認証

Google公式のApplication Default Credentials（ADC）を使用します。サービスアカウントJSONをGitにコミットせず、実行環境の`GOOGLE_APPLICATION_CREDENTIALS`で認証ファイルを指定してください。プロパティIDは環境変数`GA4_PROPERTY_ID`または設定の`ga4.property_id`から読み取ります。

## 設定

`config/settings.yml`は公開用サンプルです。実際のパッケージ名とGA4プロパティIDは運用リポジトリ側に設定してください。PyPIは認証不要、GA4はADCが必要です。CSVは`data/pypi`および`data/ga4`以下に作成します。

## 運用との分離

非公開リポジトリ`usage_collector_data`の`main`に設定、`scripts/collect.py`、ワークフローを置き、`data`ブランチにCSVを保存します。Actionsは公開ライブラリを`pip install`し、ローカルの収集スクリプトを実行します。公開ライブラリから非公開リポジトリへの認証・アクセスは不要です。データブランチの更新には非公開リポジトリの`GITHUB_TOKEN`の`contents: write`権限が必要です。

