# インストールと運用環境

[ホーム](index.md) · [English](../en/installation.md)

Python 3.10以上を用意し、公開リポジトリのルートで `python -m pip install .` を実行します。PySide6、matplotlib、requests、PyYAML、Google Analytics Data API関連ライブラリは通常の依存関係として導入されます。

運用用ディレクトリで `usage_collector install scripts` を実行すると、編集可能な `scripts/collect.py` と `scripts/plot.py`、`config/settings.yml`、`collect.yml` が生成されます。既存ファイルがあれば一括して中止します。

GitHub Actionsは非公開リポジトリの `main` に `.github/workflows/collect.yml` を置き、公開ライブラリをpipで導入してから収集します。`data` ブランチにはCSVだけをコミットします。リポジトリのActions Secretsに `GOOGLE_CREDENTIALS_JSON`、Variablesに `GA4_PROPERTY_ID` を登録します。サービスアカウントにはGA4プロパティの閲覧権限が必要です。`main` の保護は維持できますが、`data` へのActions書き込みは許可してください。

ローカルではGoogle ADCを利用します。`GOOGLE_APPLICATION_CREDENTIALS` にJSON鍵のファイルパスを設定できます。秘密鍵はGitに追加しないでください。PyPI Statsの公開APIには認証不要です。
