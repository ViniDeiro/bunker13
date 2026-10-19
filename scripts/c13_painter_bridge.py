"""Local Painter entry point for the repository's fixed production script."""
import runpy
from PySide6.QtCore import QTimer
def start_plugin():
    QTimer.singleShot(0, lambda: runpy.run_path('/Users/vini_deiro/bankers/scripts/painter_production.py'))
def close_plugin():
    pass
