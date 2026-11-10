# CHANGELOG

## 0.0.1 — 分離構成の修正（2026-11-10）

- 既存の `install scripts`、`install collect`、`install plot`、`run collect`、`run plot` を維持。
- 運用設定を `scripts/settings.yml` に統一し、生成用テンプレートはライブラリ内に1個だけ保持。
- PyPI・GA4の同時収集、認証情報不足時のエラー、作業ディレクトリに依存しないパスを修正。
- GUI、Git同期、解析・CSV保存、Actionsテンプレートの既存機能を維持。
- 日英README・Pagesの設定パスとバージョンを更新。

## 0.0.0 — 開発中（2026-11-05）

- PyPI Stats APIの一時的なHTTP 502等に再試行を追加。系列単位で失敗を隔離し、既存CSVを保持。全系列失敗時は異常終了。

- `collectors`、`storage`、`analysis`、`gui` の名前空間に整理。曖昧な `collect`/`collector`、`plot`/`gui`、`storage`/`history` の二重公開を廃止。
- 編集可能な `scripts/collect.py` と `scripts/plot.py` を唯一の実行プログラムとして維持。`usage_collector install` と `run` は同一スクリプトを利用。
- 設定を `usage_collector.settings.Settings` に集約。同梱標準設定と利用者の `config/settings.yml` の優先順位を明文化。
- PyPI、GA4の国・地域・都市別データ取得、CSV履歴統合、2画面GUI、国別地図と日付別明細を収録。
- 本バージョンは開発中であり、正式リリースではない。

### モジュール構成の整理

- `collectors/`、`storage/`、`config/`、`analysis/`、`gui/` の多段ディレクトリを廃止し、単一階層のモジュールへ統合。
- `scripts/collect.py` と `scripts/plot.py` は編集可能なオブジェクト組み立てスクリプトとして維持。
- PyPI/GA4収集、地域別CSV、Git同期、時系列解析、Qt GUI、地図表示の既存実装を移設し、機能を削除しない。
- インポートパス、README、テストを更新。バージョンは `0.0.0` のまま。

### Git履歴同期の修正（開発中・0.0.0）

- `GitHistorySync.sync()` の `git archive` とtar展開への依存を廃止し、`git ls-tree` / `git show` でCSVを取得する方式に変更。
- `data` ブランチ直下の `ga4/`・`pypi/` と、`data/ga4/`・`data/pypi/` の両配置をサポート。
- ローカルGitリポジトリを使った同期テストを追加。既存CSVへのマージ動作を維持。

### Git履歴同期の修正（0.0.0、2026-11-05）

- `data` ブランチのCSVを、`pypi/`、`ga4/`、`data/pypi/`、`data/ga4/`、`data/data/...` などの配置から検出するよう変更。
- CSVが検出できない場合は、ブランチ内の実際のパス一覧（先頭20件）を例外に表示し、配置の問題を特定できるよう変更。
- 二重にネストしたデータディレクトリの同期テストを追加。

### Git履歴同期の修正（0.0.0、2026-11-05）

- `GitHistorySync` の参照先を可変の `FETCH_HEAD` から専用Git refに変更し、取得コミットのハッシュを確定してからCSVを読み込む。
- `git ls-tree -r -z` により再帰的にCSVを列挙し、`git show` でファイル内容を取得する。`git archive` は使用しない。
- Git操作失敗時は標準エラーを含む診断を出力し、CSV未検出時はコミットIDとツリー内のパスを報告する。
- ローカルGitリポジトリとクローン済みリポジトリを使った回帰テストを追加。

### Git同期の修正（2026-11-05）

- GitHubの `data` ブランチ取得結果が空の場合、取得前の `origin/data` に有効なCSVがあればそれを利用する。
- `FETCH_HEAD` に依存せず、コミットごとにCSVを検証してから読み込む。
- 取得失敗時は参照別のファイル数とCSV件数を表示する。既存CSVは削除しない。

- GUIスクリプトの作業ディレクトリ依存を除去し、ソースツリーの `data/` を優先するよう修正。Git同期は `origin/data` 参照へ直接fetchする単純な構成に変更。

- `usage_collector install scripts` により運用リポジトリ用の収集・表示スクリプト、設定例、Actions例を一括生成可能にした。
