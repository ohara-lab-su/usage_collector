#!/usr/bin/env python
"""PyPI・GA4の時系列統計を解析するQt GUI。グラフは保存しない。"""
import json
from collections import defaultdict
from datetime import date
from importlib.resources import files

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QHBoxLayout,
                              QLabel, QMainWindow, QPushButton, QSplitter,
                              QTableWidget, QTableWidgetItem, QVBoxLayout,
                              QWidget)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from matplotlib.colors import LogNorm
from matplotlib import font_manager, rcParams


def configure_fonts():
    """利用可能な日本語フォントを優先してMatplotlibに適用する。"""
    names = {item.name for item in font_manager.fontManager.ttflist}
    for name in ("Hiragino Sans", "Hiragino Kaku Gothic ProN",
                 "Yu Gothic", "Noto Sans CJK JP", "IPAexGothic"):
        if name in names:
            rcParams["font.family"] = [name]
            break
    rcParams["axes.unicode_minus"] = False



def read_table(history, source, name):
    return history.read(source, name)


def number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def dates_in(rows):
    values = set()
    for row in rows:
        try:
            values.add(date.fromisoformat(row.get('date', '')))
        except ValueError:
            continue
    return sorted(values)


class AnalyticsWindow(QMainWindow):
    """系列・期間・分類を選択し、時系列と集計表を同期表示する。"""

    def __init__(self, history, source):
        super().__init__()
        self.source = source
        self.data = {}
        names = ('overall', 'python_major', 'python_minor', 'system')
        if source == 'ga4':
            names = ('daily', 'countries', 'regions', 'cities', 'sources', 'devices', 'pages')
        for name in names:
            self.data[name] = read_table(history, source, name)
        self.setWindowTitle(source.upper() + ' | Usage Analytics')
        self.resize(1250, 820)
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        controls = QHBoxLayout()
        layout.addLayout(controls)
        controls.addWidget(QLabel('表示'))
        self.mode = QComboBox()
        if source == 'ga4':
            self.mode.addItems(('国別地図', '日別推移', '国別推移',
                                '都道府県別', '都市別', '流入元', '端末', 'ページ'))
        else:
            self.mode.addItems(('パッケージ別', 'Python major', 'Python minor', 'OS'))
        controls.addWidget(self.mode)
        self.package = QComboBox()
        packages = sorted({r.get('package', '') for rows in self.data.values()
                           for r in rows if r.get('package')})
        self.package.addItem('すべて')
        self.package.addItems(packages)
        if source == 'pypi':
            controls.addWidget(QLabel('パッケージ'))
            controls.addWidget(self.package)
        self.region_country = QComboBox()
        if source == 'ga4':
            self.region_country.addItem('すべての国')
            countries = sorted({r.get('country', '') for name in ('countries', 'regions', 'cities')
                                for r in self.data.get(name, []) if r.get('country')})
            self.region_country.addItems(countries)
            controls.addWidget(QLabel('国'))
            controls.addWidget(self.region_country)
        self.metric = QComboBox()
        if source == 'ga4':
            self.metric.addItems(('sessions', 'activeUsers', 'screenPageViews'))
            controls.addWidget(QLabel('指標'))
            controls.addWidget(self.metric)
        controls.addWidget(QLabel('開始'))
        self.start = QDateEdit()
        self.start.setCalendarPopup(True)
        controls.addWidget(self.start)
        controls.addWidget(QLabel('終了'))
        self.end = QDateEdit()
        self.end.setCalendarPopup(True)
        controls.addWidget(self.end)
        self.back = QPushButton('◀')
        self.forward = QPushButton('▶')
        controls.addWidget(self.back)
        controls.addWidget(self.forward)
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        self.figure = Figure(figsize=(11, 5))
        self.canvas = FigureCanvasQTAgg(self.figure)
        splitter.addWidget(self.canvas)
        self.table = QTableWidget()
        self.table.setSortingEnabled(True)
        splitter.addWidget(self.table)
        splitter.setSizes((570, 210))
        all_dates = dates_in([r for rows in self.data.values() for r in rows])
        self.all_dates = all_dates
        if all_dates:
            self.start.setDate(all_dates[0])
            self.end.setDate(all_dates[-1])
        self.mode.currentIndexChanged.connect(self.update_view)
        self.package.currentIndexChanged.connect(self.update_view)
        self.metric.currentIndexChanged.connect(self.update_view)
        self.region_country.currentIndexChanged.connect(self.update_view)
        self.start.dateChanged.connect(self.update_view)
        self.end.dateChanged.connect(self.update_view)
        self.back.clicked.connect(lambda: self.shift(-1))
        self.forward.clicked.connect(lambda: self.shift(1))
        self.update_view()

    def shift(self, delta):
        """矢印ボタンで表示モードを確実に切り替える。"""
        index = (self.mode.currentIndex() + delta) % self.mode.count()
        self.mode.setCurrentIndex(index)

    def filtered(self, rows):
        start = self.start.date().toString('yyyy-MM-dd')
        end = self.end.date().toString('yyyy-MM-dd')
        selected = self.package.currentText()
        result = []
        for row in rows:
            day = row.get('date', '')
            if day < start:
                continue
            if day > end:
                continue
            if self.source == 'pypi':
                if selected != 'すべて':
                    if row.get('package') != selected:
                        continue
            if self.source == 'ga4':
                country = self.region_country.currentText()
                if country != 'すべての国':
                    if row.get('country', country) != country:
                        continue
            result.append(row)
        return result

    def table_rows(self, headings, rows):
        self.table.setSortingEnabled(False)
        self.table.clear()
        self.table.setColumnCount(len(headings))
        self.table.setHorizontalHeaderLabels(headings)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                if isinstance(value, (int, float)):
                    item.setData(Qt.ItemDataRole.DisplayRole, value)
                self.table.setItem(i, j, item)
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()

    def update_view(self, *unused):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        mode = self.mode.currentIndex()
        if self.source == 'pypi':
            names = ('overall', 'python_major', 'python_minor', 'system')
            rows = self.filtered(self.data[names[mode]])
            category = 'package'
            if mode > 0:
                category = 'category'
            self.timeseries(ax, rows, category, 'downloads')
            self.setWindowTitle('PyPI | ' + self.mode.currentText())
        else:
            names = ('countries', 'daily', 'countries', 'regions', 'cities',
                     'sources', 'devices', 'pages')
            rows = self.filtered(self.data[names[mode]])
            metric = self.metric.currentText()
            if mode == 0:
                self.world_map(ax, rows, metric)
            else:
                categories = ('country', 'date', 'country', 'region', 'city',
                              'sessionSourceMedium', 'deviceCategory', 'pagePath')
                category = categories[mode]
                if mode == 1:
                    category = '_total'
                if rows:
                    if metric not in rows[0]:
                        metric = next((m for m in ('sessions', 'activeUsers', 'screenPageViews')
                                       if m in rows[0]), metric)
                self.timeseries(ax, rows, category, metric)
            self.setWindowTitle('GA4 | ' + self.mode.currentText())
        self.figure.autofmt_xdate()
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def timeseries(self, ax, rows, category, metric):
        """横軸を日付、系列をパッケージ名またはアクセス分類とする。"""
        grouped = defaultdict(lambda: defaultdict(float))
        totals = defaultdict(float)
        for row in rows:
            key = row.get(category, 'Total')
            if category == '_total':
                key = 'Total'
            day = row.get('date', '')
            value = number(row.get(metric))
            grouped[key][day] += value
            totals[key] += value
        ranked = sorted(totals, key=totals.get, reverse=True)
        for key in ranked[:15]:
            points = sorted(grouped[key].items())
            x = []
            y = []
            for day, value in points:
                try:
                    x.append(date.fromisoformat(day))
                    y.append(value)
                except ValueError:
                    continue
            ax.plot(x, y, label=key, linewidth=1.5)
        ax.set_title(self.mode.currentText() + ' / ' + metric)
        ax.set_xlabel('Date')
        ax.set_ylabel(metric)
        ax.grid(alpha=0.25)
        if ranked:
            ax.legend(fontsize=8, ncol=2)
        # 表は日付と分類と件数を示す。系列は描画上位に制限しても表は全件表示。
        table = []
        for key in ranked:
            for day, value in sorted(grouped[key].items(), reverse=True):
                table.append((day, key, int(value)))
        table.sort(key=lambda item: (item[0], item[1]), reverse=True)
        if self.source == 'ga4':
            headings = ('日付', 'アクセス元', metric)
        else:
            headings = ('日付', 'パッケージ / 分類', metric)
        self.table_rows(headings, table)

    def world_map(self, ax, rows, metric):
        """指定期間の国別アクセスを色分けし、数値は表で示す。"""
        country_totals = defaultdict(float)
        daily = defaultdict(float)
        for row in rows:
            country = row.get('country', '')
            value = number(row.get(metric))
            country_totals[country] += value
            daily[(row.get('date', ''), country)] += value
        aliases = {'United States': 'United States of America',
                   'Türkiye': 'Turkey', 'Democratic Republic of the Congo': 'Dem. Rep. Congo'}
        mapped = {aliases.get(key, key): value for key, value in country_totals.items()}
        geo = json.loads(files('usage_collector').joinpath('world_countries.json').read_text())
        patches = []
        values = []
        for country in geo:
            geom = country['geometry']
            polygons = [geom['coordinates']]
            if geom['type'] == 'MultiPolygon':
                polygons = geom['coordinates']
            for polygon in polygons:
                patches.append(Polygon(polygon[0], closed=True))
                values.append(mapped.get(country['name'], 0))
        maximum = max(values, default=1)
        norm = LogNorm(vmin=1, vmax=max(1.01, maximum))
        cmap = __import__('matplotlib').colormaps['YlOrRd']
        colors = []
        for value in values:
            if value > 0:
                colors.append(cmap(norm(value)))
            else:
                colors.append('#e4e7ea')
        collection = PatchCollection(patches, facecolor=colors,
                                     edgecolor='#999999', linewidth=0.2)
        ax.add_collection(collection)
        ax.set_xlim(-180, 180)
        ax.set_ylim(-60, 85)
        ax.set_title('国別アクセス数 / ' + metric)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        table = [(day, country, int(value)) for (day, country), value in daily.items()]
        table.sort(key=lambda item: (item[0], item[2]), reverse=True)
        self.table_rows(('日付', 'アクセス元の国', metric), table)


def show(history, save=None):
    """二画面を同時に開く。画像出力は明示された場合だけ実施する。"""
    configure_fonts()
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    families = set(QFontDatabase.families())
    for family in ('Hiragino Sans', 'Hiragino Kaku Gothic ProN',
                   'Yu Gothic', 'Noto Sans CJK JP', 'IPAexGothic'):
        if family in families:
            app.setFont(QFont(family, 11))
            break
    windows = []
    for source in ('pypi', 'ga4'):
        window = AnalyticsWindow(history, source)
        windows.append(window)
        window.show()
    if save is not None:
        from pathlib import Path
        target = Path(save)
        for window in windows:
            output = target.with_name(target.stem + '_' + window.source + '.png')
            window.figure.savefig(output)
    return app.exec()
