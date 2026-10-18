"""Run after installation: python examples/minimal.py"""
import sys
from studioglass import ThemeController, GlassSurface, GlassButton
from studioglass.qt import QtWidgets as W

app = W.QApplication(sys.argv)
window = GlassSurface()
theme = ThemeController(window,mode="light",transparency=60)
layout = W.QVBoxLayout(window)
layout.setContentsMargins(32,32,32,32)
button = GlassButton("Switch theme")
button.clicked.connect(lambda: theme.configure(mode="dark" if theme.effective_mode=="light" else "light"))
layout.addWidget(button)
window.setWindowTitle("Studio Glass — minimal example")
window.resize(360,180)
window.show()
sys.exit(app.exec())
