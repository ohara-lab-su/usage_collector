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
