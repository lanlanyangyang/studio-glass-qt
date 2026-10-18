"""Keep your QMainWindow and business signals; add glass incrementally."""
import sys
from studioglass import ThemeController, GlassButton, GlassComboBox, GlassSegmentedControl
from studioglass.qt import QtWidgets as W

app = W.QApplication(sys.argv)
window = W.QMainWindow()
theme = ThemeController(window,mode="system")
central = W.QWidget()
window.setCentralWidget(central)
layout = W.QVBoxLayout(central)
tabs = GlassSegmentedControl()
pages = W.QStackedWidget()
for name in ("Editor","Preview"):
    tabs.addTab(name)
    pages.addWidget(W.QLabel(f"Your existing {name.lower()} content"))
tabs.currentChanged.connect(pages.setCurrentIndex)
layout.addWidget(tabs)
layout.addWidget(pages)
combo = GlassComboBox()
combo.addItem("First option",{"id":1})
combo.addItem("Second option",{"id":2})
layout.addWidget(combo)
status = W.QLabel("No action yet")
button = GlassButton("Use selected option",variant="primary")
button.clicked.connect(lambda: status.setText(str(combo.currentData())))
layout.addWidget(button)
layout.addWidget(status)
window.setWindowTitle("Studio Glass — existing window integration")
window.resize(540,360)
window.show()
sys.exit(app.exec())
