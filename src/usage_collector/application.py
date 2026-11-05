#!/usr/bin/env python
"""GUIアプリケーションの起動部品。データ同期やCLI引数解析は行わない。"""
from pathlib import Path

class AnalyticsApplication:
    def __init__(self, history):
        self.history = history

    def show(self, save=None):
        from .gui import show
        return show(self.history, save=save)

    def run(self, save=None):
        return self.show(save=save)

    def create_window(self, source):
        """GUIを組み込む際に、独立したウィンドウを生成する。"""
        from .gui import AnalyticsWindow
        return AnalyticsWindow(self.history, source)
