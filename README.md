# usage_collector

PyPI Stats と Google Analytics 4（GA4）の利用統計を取得し、日別CSVとして蓄積・解析・可視化するPythonライブラリです。Python API、CLI、PySide6 GUI、運用リポジトリ向けの実行スクリプト・GitHub Actionsテンプレートを提供します。

**開発バージョン：`0.0.0`／Python 3.10以上。** このリポジトリは公開可能な**ライブラリ本体**です。実際の収集対象、Google認証情報、収集済みCSVは利用者の運用環境で管理します。本書は、分離後のソースコードに対応した設計・API・運用・再構築手順をまとめています。

## 1. 設計と責務の分離

```text
【公開】usage_collector（ライブラリ）
  PyPI Stats API ── pypi.py ──┐
                              ├─ collection.py ─ csv_store.py ─ CSV
  GA4 Data API ─── ga4.py ────┘                            │
                                                          ▼
                          analysis.py ◀─ history.CSVHistory
                               │                          │
                               └── application.py / gui.py

  cli.py ─ install / run
     └─ templates/ ─ 運用側の scripts・設定例・Actions例を生成

【非公開】usage_collector_data（利用者の運用リポジトリの一例）
  main：scripts/collect.py、scripts/plot.py、config/settings.yml、Actions
  data：data/pypi/*.csv、data/ga4/*.csv
  GitHub Secrets：GA4認証JSON／Variables：GA4プロパティID
```

ライブラリは**運用リポジトリ名を前提としません**。`usage_collector_data` は一つの構成例です。PyPI・GA4の取得ロジック、CSVの更新、Gitからの履歴取り込み、解析、GUIを別モジュールに分けています。ただし、**現行の `PyPICollector` / `GA4Collector` はCSVへの保存まで実行します**。データ取得と保存を完全に独立させた抽象ストレージAPIではありません。

Git同期は任意です。ローカルCSVを直接読み込む場合、Gitの設定や認証は不要です。公開ライブラリから非公開リポジトリへ自動アクセスする仕組みもありません。

## 2. 導入と必要環境

`pyproject.toml` に通常の依存関係として `requests`、`PyYAML`、`google-analytics-data`、`google-auth`、`matplotlib`、`PySide6` を定義しています。extrasは不要です。Git同期を使う場合は別途Gitが必要です。

```bash
python -m pip install .
usage_collector --help
python -m pytest -q tests
```

PyPIなどに配布済みのパッケージを使う場合は、配布元に応じて `pip install` の指定を変更します。GitHub上の公開ソースをインストールする例：

```bash
python -m pip install 'git+https://github.com/ohara-lab-su/usage_collector.git@main'
```

このURLは公開リポジトリの配置例です。利用するリポジトリの実際の公開状態を確認してください。開発中のライブラリを編集しながら使う場合は `python -m pip install -e .` も利用できます。

## 3. CLI：`install` と `run`

`usage_collector` は `pyproject.toml` の `[project.scripts]` で登録されたコマンドです。

```bash
usage_collector install scripts
usage_collector install collect
usage_collector install plot
usage_collector run collect --config config/settings.yml --output data
usage_collector run plot --data data
```

### `usage_collector install scripts`（推奨）

**カレントディレクトリ**に、利用者が編集・管理するための4ファイルを生成します。

```text
./
├── scripts/
│   ├── collect.py        # 収集アプリケーション
│   └── plot.py           # 履歴表示アプリケーション
├── config/
│   └── settings.yml      # 収集対象の設定例
└── collect.yml           # GitHub Actionsの配置用テンプレート
```

`collect.yml` は手動で `.github/workflows/collect.yml` に配置します。**既存ファイルが一つでもある場合、4ファイルとも作成せず終了**します。既存の設定やスクリプトを上書きしません。テンプレートのスクリプトは実行可能な通常のPythonファイルで、編集して利用できます。

`install collect` と `install plot` は従来互換の単独スクリプトを、それぞれカレントディレクトリの `collect.py` / `plot.py` に生成します。これらも既存ファイルを上書きしません。`run collect` と `run plot` は、パッケージに同梱されたスクリプトを**コピーせず**実行します。運用側テンプレートと同梱の `run` 用スクリプトでは、引数やデフォルトのデータディレクトリが異なるため、以下を区別してください。

### 収集コマンド

```bash
usage_collector run collect --source pypi --config config/settings.yml --output data
usage_collector run collect --source ga4 --ga4-days 3 --output data
usage_collector run collect --source all --output data

python scripts/collect.py --source pypi --config config/settings.yml --output data
python scripts/collect.py --source ga4 --ga4-days 3 --output data
```

`--source` は `pypi`、`ga4`、`all`、`--ga4-days` は1以上の整数です。`all` でGA4プロパティIDが未設定ならGA4をスキップし、`ga4` を明示した場合はエラーになります。`--output` はCSVの親ディレクトリです。

### 表示コマンド

```bash
usage_collector run plot --data data
usage_collector run plot --data data --save figure.png
usage_collector run plot --data data --refresh --config config/settings.yml

python scripts/plot.py --data data
python scripts/plot.py --data data --repository . --branch data --fetch
```

`--refresh` は**同梱の `run plot` 用スクリプト**にあるAPI再収集オプションです。`--fetch` はGit履歴からの明示的なCSV取り込みです。`install scripts` で生成した `scripts/plot.py` は `--repository` を持ちますが、`--refresh` は持ちません。GUIを表示するだけならCSVを用意して `--fetch` を付けないでください。

## 4. 設定ファイル

```yaml
pypi:
  packages:
    - example-package
    - another-package

ga4:
  property_id: null
```

`pypi.packages` は対象パッケージ名の配列です。`ga4.property_id` はGA4の数値プロパティIDで、環境変数 `GA4_PROPERTY_ID` が設定されていれば**環境変数を優先**します。秘密鍵をYAMLに書かないでください。

`Settings(path).load()` は明示されたファイルを読みます。引数なしの場合は、カレントディレクトリの `config/settings.yml` を優先し、存在しなければライブラリ同梱のサンプル設定を使います。設定のルートはYAMLマッピングである必要があります。**実運用では `--config` を明示することを推奨します。**

## 5. PyPI Stats：収集内容と仕様

PyPI Stats公開APIを使用し、PyPIアカウントやAPIキーなしでダウンロード統計を取得します。エンドポイントは次の4種類です。

| CSV | API区分 | 内容 |
| --- | --- | --- |
| `pypi/overall.csv` | `overall` | 日別ダウンロード数。`without_mirrors` のみ採用 |
| `pypi/python_major.csv` | `python_major` | Pythonメジャーバージョン別 |
| `pypi/python_minor.csv` | `python_minor` | Pythonマイナーバージョン別 |
| `pypi/system.csv` | `system` | OS区分別 |

取得先の形式は `https://pypistats.org/api/packages/{package}/{dimension}` です。CSVの列は次のとおりです。

```csv
date,package,dimension,category,downloads
2026-11-01,example-package,overall,without_mirrors,42
```

更新キーは `date + package + dimension + category`。複数パッケージを同一CSVに保存でき、同じ日付・区分を再取得した場合はその行を更新します。取得失敗時は既存CSVを保持します。HTTP 429/500/502/503/504などはリトライ対象です。失敗した系列は警告して次へ進み、全系列失敗時は例外になります。取得件数は**取得した行数**であり、ダウンロード数の合計ではありません。

## 6. GA4：認証と収集内容

GA4はGoogle Analytics Data APIを使用します。認証はGoogle公式クライアントの **Application Default Credentials（ADC）** に委ねます。ローカルのサービスアカウントJSONを利用する場合：

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GA4_PROPERTY_ID=123456789
usage_collector run collect --source ga4 --output data
```

Google CloudでData APIを利用できるようにし、サービスアカウントに対象GA4プロパティの読み取り権限を付与してください。サービスアカウントJSONはGitにコミットせず、公開リポジトリにも配置しません。GitHub Actionsのテンプレートでは、GitHub Secret `GOOGLE_CREDENTIALS_JSON` を実行時に一時ファイルへ書き出し、`GOOGLE_APPLICATION_CREDENTIALS` を設定します。`GA4_PROPERTY_ID` はGitHub Variableを参照します。**このテンプレートはWorkload Identity FederationではなくJSON鍵方式です。**

| CSV | GA4ディメンション | GA4指標 |
| --- | --- | --- |
| `ga4/daily.csv` | `date` | `sessions`, `activeUsers`, `screenPageViews` |
| `ga4/pages.csv` | `date`, `pagePath` | `screenPageViews` |
| `ga4/countries.csv` | `date`, `country` | `sessions`, `activeUsers` |
| `ga4/regions.csv` | `date`, `country`, `region` | `sessions`, `activeUsers` |
| `ga4/cities.csv` | `date`, `country`, `region`, `city` | `sessions`, `activeUsers` |
| `ga4/sources.csv` | `date`, `sessionSourceMedium` | `sessions` |
| `ga4/devices.csv` | `date`, `deviceCategory` | `sessions` |

GA4のAPIが返す `YYYYMMDD` はCSVでは `YYYY-MM-DD` に変換します。APIのページングは `row_count` に達するまで実行します。収集終了日は**実行日の前日**です。既存CSVがあれば通常 `--ga4-days`（デフォルト3日）分を再取得し、該当レポートのCSVがなければ**初回30日分**を取得します。GA4の遅延反映を考慮した直近日の再取得に対応しますが、古い履歴を自動的に全期間取得する機能ではありません。

**現行CSVにGA4プロパティID列はありません。** 複数プロパティを扱う場合は、必ず別の出力ディレクトリに保存してください。同じ `ga4/*.csv` に複数プロパティを混在させると、同じディメンションキーの行が上書きされます。

## 7. CSV履歴の更新・読み込み

`usage_collector.csv_store.merge_csv(path, rows, fields, keys)` は、指定キーに一致する既存レコードを置換し、その他の履歴を保持します。更新時は同一ディレクトリに一時ファイルを作り、`os.replace` で置換します。空の `rows` は既存CSVを消しません。

```python
from usage_collector.history import CSVHistory

history = CSVHistory("data")
pypi_rows = history.read("pypi", "overall")
ga4_rows = history.read("ga4", "daily")
print(history.exists(), len(pypi_rows), len(ga4_rows))
```

`CSVHistory.read(source, name)` はファイルが存在しない場合に空リストを返し、存在する場合は文字列値の辞書のリストを返します。`CSVHistory.exists()` は配下にCSVが一つでもあれば真です。**すべてのCSVが揃っているかを検査する機能ではありません。**

## 8. Python API：独自アプリケーションから使う

収集の組み合わせは `usage_collector.collection` のクラスで指定します。

```python
from usage_collector.collection import CollectionJob, PyPICollector, GA4Collector

job = CollectionJob({
    "pypi": PyPICollector(["example-package"], "data"),
    # "ga4": GA4Collector("123456789", "data", days=3),
})
result = job.collect()
print(result)  # {'pypi': 取得した行数}
```

設定から組み立てる場合：

```python
from usage_collector.settings import Settings
from usage_collector.collection import CollectionJob, make_collectors

settings = Settings("config/settings.yml").load()
collectors = make_collectors(settings, "data", source="all", ga4_days=3)
result = CollectionJob(collectors).collect()
```

個別のAPI応答を取得したい場合は `usage_collector.pypi.fetch(package, dimension)`、`usage_collector.ga4.fetch(client, property_id, name, start_date, end_date)` を利用できます。`ga4.fetch` の `client` はGoogle Analytics Data APIのクライアントです。`PyPIStatsClient`、`GA4ReportClient` も用意しています。API呼び出しをテスト時に差し替えるため、PyPIにはHTTPセッション、GA4にはクライアントを注入できます。

```python
from usage_collector.analysis import TimeSeries
from usage_collector.history import CSVHistory

rows = CSVHistory("data").read("pypi", "overall")
series = TimeSeries(rows).group(["package"], "downloads",
                                start="2026-11-01", end="2026-11-30")
```

`TimeSeries.group(dimensions, metric, start=None, end=None)` はディメンションの組み合わせと日付ごとに数値を合計し、辞書を返します。CSVを直接加工したい開発者はGUIを経由する必要がありません。

## 9. GUI：PyPI・GA4の履歴を表示

```python
from usage_collector.history import CSVHistory
from usage_collector.application import AnalyticsApplication

AnalyticsApplication(CSVHistory("data")).show()
```

PySide6とMatplotlibを利用します。PyPIとGA4は別ウィンドウとして表示され、収集済みのCSVからグラフ・表を構成します。GA4の地域情報については地図描画用の同梱 `world_countries.json` を利用します。GUI起動時に自動でGitからデータを取得したり、GA4の認証を要求したりはしません。データ更新は収集スクリプトまたは明示的な `--refresh` で行います。

## 10. GitHub Actions：公開ライブラリと非公開データを分離する

推奨運用例：

```text
usage_collector（Public）
  src/usage_collector/  README.md  tests/  pyproject.toml

usage_collector_data（Private）
  main（保護）
    scripts/collect.py
    scripts/plot.py
    config/settings.yml
    .github/workflows/collect.yml
  data
    data/pypi/*.csv
    data/ga4/*.csv
  Settings → Secrets: GOOGLE_CREDENTIALS_JSON
  Settings → Variables: GA4_PROPERTY_ID
```

初期構築は次の順序です。

1. 非公開の運用リポジトリを作成し、`main` を設定します。`data` ブランチも作成します。`main` は保護したままで構いません。
2. 非公開リポジトリの作業ツリーで `usage_collector install scripts` を実行し、`config/settings.yml` の対象パッケージを設定します。
3. `collect.yml` の `OWNER` を公開ライブラリのGitHub所有者に置き換え、`.github/workflows/collect.yml` に配置します。ライブラリの公開先が異なる場合はインストールURLを変更します。
4. GitHub ActionsのSecretsに `GOOGLE_CREDENTIALS_JSON`、Variablesに `GA4_PROPERTY_ID` を登録します。GA4を使わない場合はVariableを設定せず、GA4の収集ステップをスキップできます。
5. Actionsの `GITHUB_TOKEN` が `data` ブランチに書き込めることを確認します。ワークフローには `permissions: contents: write` が指定されていますが、リポジトリ側の権限・ブランチ保護規則も適用されます。
6. Actionsの `workflow_dispatch` で手動実行し、`data` ブランチにCSVが作成されることを確認します。以後は定期実行されます。

同梱テンプレートのワークフローは `main` をチェックアウトし、公開ライブラリをGitHubから `pip install` します。次に `origin/data` から一時worktreeを作成し、**そのworktree内のCSVを更新して `data` ブランチにだけコミット・push** します。`main` への自動pushは行いません。定期実行時刻は `17 18 * * *`（UTC 18:17、日本時間の翌日03:17）です。

**公開リポジトリのActionsが非公開リポジトリを呼び出す設計ではありません。** 非公開側が公開ライブラリを通常の依存パッケージとして取得する構成です。したがって、ライブラリ取得のために非公開リポジトリのアクセストークンを公開側へ渡す必要はありません。

### 既存運用リポジトリを改名した場合

既存の `usage_collector` を `usage_collector_data` にリネームして運用設定を引き継いだ場合、通常のサービスアカウントJSONをGitHub Secretsに保存する方式では、Google側のサービスアカウントを再作成する必要はありません。ただし、**ワークフローのライブラリインストール先**は新しい公開 `usage_collector` に変更してください。GitHub Secrets・Variablesの実際の登録状況と、Actionsの実行結果は運用側で確認してください。

## 11. 非公開 `data` ブランチの履歴をローカルへ取得

運用側のテンプレート `scripts/plot.py` は、`--fetch` を付けた場合に限り `GitHistorySync` を実行します。

```bash
python scripts/plot.py --repository . --branch data --data data --fetch
python scripts/plot.py --data data
```

`GitHistorySync` は指定リポジトリの `refs/heads/data` を取得し、Gitツリーから `pypi/*.csv`、`ga4/*.csv` を読み、ローカル `CSVHistory` へマージします。対象リポジトリに対するGitの**読み取り権限**が必要です。通常は非公開リポジトリのローカルクローンで実行します。Gitの作業ブランチを切り替える処理ではありません。

**既知の制約：** 過去の運用環境では、`origin/data` にCSVが存在するにもかかわらずGit同期が空ツリーと判定された事象がありました。現行実装のすべてのGit環境での正常動作は保証していません。CSVがローカルに存在する場合は `--fetch` を付けずに表示してください。`--fetch` が失敗した場合、リポジトリ、ブランチ、Git参照、CSVのパスを切り分けてください。

## 12. 公開・運用上の注意

ソースコード、公開APIへのアクセス処理、設定例、Actionsのテンプレートは公開できます。一方、GA4の国・地域・都市別統計、流入元、ページ別アクセス数などの**実データは非公開運用側に保存**してください。公開ライブラリ側のGit履歴に実データや秘密鍵が過去にコミットされていないかも確認が必要です。現在のブランチから削除しただけでは過去のGit履歴は消えません。

公開用の設定例に本物のGA4プロパティIDや秘密鍵を埋め込む必要はありません。収集結果は日別CSVであり、利用者を個別に識別するアクセスログではありませんが、研究室の運用統計として公開可否を判断してください。

## 13. 実装ファイルとテスト

| ファイル | 役割 |
| --- | --- |
| `collection.py` | `PyPICollector`、`GA4Collector`、`CollectionJob`、設定からの生成 |
| `pypi.py` | PyPI Stats APIの取得、HTTP再試行、CSV更新 |
| `ga4.py` | GA4 Data APIの7レポート、ページング、CSV更新 |
| `csv_store.py` | キー付きCSVマージ、原子的ファイル置換 |
| `history.py` | `CSVHistory`、`GitHistorySync` |
| `settings.py` | YAML設定の読み込み |
| `analysis.py` | `TimeSeries` による日別集計 |
| `gui.py` / `application.py` | PySide6 GUIと起動用API |
| `cli.py` | `install` / `run` コマンド |
| `scripts/` | ライブラリ同梱の単独実行スクリプト |
| `templates/` | 運用リポジトリ向けの編集可能な雛形 |
| `tests/` | CLI、収集、CSV、Git同期、表示などのテスト |

```bash
python -m pytest -q tests
python -m compileall -q src/usage_collector
```

テストで確認できるのはローカルで再現した条件です。実際のGA4権限、GitHub ActionsのSecrets、保護ブランチへのアクセス、GitHubからのインストール、実運用のGit同期は、対象環境で別途確認してください。

## 14. 拡張の方向性と現状の制約

PyPIとGA4以外の収集元を追加する場合、既存の `CollectionJob` に `collect()` メソッドを持つ独自の収集クラスを登録できます。ただし、**`make_collectors` とCLIの `--source` は現在 `pypi` / `ga4` / `all` の固定選択**です。新しい収集元をCLIから扱うには、設定とコマンドの拡張が必要です。

現行のGA4 CSVはプロパティIDをキーに含めず、CSVの保存先はローカルファイルです。SQLite等のストレージ切替や複数GA4プロパティの単一CSV統合は未実装です。また、Git履歴の同期機能はCSVの**取得・マージ**であり、ライブラリ側がGitへpushするAPIではありません。Gitへのコミットとpushは運用側のActionsが担当します。

このように、ライブラリの機能と運用側の責務を明確に区別することで、利用者は収集対象、保存場所、実行スケジュール、可視化方法を自分の環境に合わせて変更できます。
