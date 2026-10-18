"""Select one Qt binding before importing widgets; never mix bindings."""
import importlib
import importlib.util
import os
import sys

loaded = [name for name in ("PyQt6", "PySide6") if name in sys.modules]
requested = os.environ.get("STUDIOGLASS_QT_API", "").lower()
names = {"pyqt6": "PyQt6", "pyside6": "PySide6"}
if requested and requested not in names:
    raise ImportError("STUDIOGLASS_QT_API must be pyqt6 or pyside6")
if len(loaded) > 1 or (loaded and requested and names[requested] != loaded[0]):
    raise ImportError("Qt binding conflict: use a fresh process with only one Qt binding")
binding = loaded[0] if loaded else names.get(requested)
if not binding:
    binding = next((name for name in names.values() if importlib.util.find_spec(name)), None)
if not binding or importlib.util.find_spec(binding) is None:
    raise ImportError('Install a binding: pip install "studio-glass-qt[pyqt6]" or "studio-glass-qt[pyside6]"')
QtCore = importlib.import_module(f"{binding}.QtCore")
QtGui = importlib.import_module(f"{binding}.QtGui")
QtWidgets = importlib.import_module(f"{binding}.QtWidgets")
Signal = QtCore.pyqtSignal if binding == "PyQt6" else QtCore.Signal
BINDING = binding
if binding == "PyQt6":
    from PyQt6 import sip
    def is_valid(obj):
        return not sip.isdeleted(obj)
else:
    from shiboken6 import isValid as is_valid
