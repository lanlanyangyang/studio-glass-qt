"""Per-widget-tree appearance; no application-wide stylesheet or settings writes."""
from .qt import QtCore, QtGui, QtWidgets, Signal

THEMES = {
    "light": dict(bg_window="#f2f4f8", bg_panel="#ffffff", text="#19212f",
                  muted="#667285", border="#dce2eb", accent="#006fe6",
                  selected="#ffffff", soft="#e7f1ff", hover="#f0f4f9", glass="#ffffff"),
    "dark": dict(bg_window="#0d121a", bg_panel="#252f3d", text="#edf1f7",
                 muted="#a5abb5", border="#344151", accent="#83bdff",
                 selected="#364960", soft="#243e60", hover="#303e50", glass="#304158"),
}
_UNSET = object()


def controller_for(widget):
    while widget is not None:
        controller = getattr(widget, "_studio_glass_theme", None)
        if controller is not None:
            return controller
        widget = widget.parentWidget()
    return None


def colors(widget):
    controller = controller_for(widget)
    return controller.colors if controller else {k: QtGui.QColor(v) for k, v in THEMES["light"].items()}


def palette_for(t):
    palette = QtGui.QPalette()
    roles = {"Window": "bg_window", "Base": "bg_panel", "AlternateBase": "hover",
             "Button": "bg_panel", "WindowText": "text", "Text": "text", "ButtonText": "text",
             "Highlight": "soft", "HighlightedText": "text", "Mid": "border", "Dark": "border",
             "Light": "bg_panel", "Shadow": "muted", "PlaceholderText": "muted",
             "ToolTipBase": "bg_panel", "ToolTipText": "text"}
    for group in QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorGroup.Disabled:
        for role, name in roles.items():
            color = t["muted"] if group == QtGui.QPalette.ColorGroup.Disabled and role in ("Text", "WindowText", "ButtonText") else t[name]
            palette.setColor(group, getattr(QtGui.QPalette.ColorRole, role), color)
    return palette


class ThemeController(QtCore.QObject):
    """Attach to a QWidget (including QMainWindow) before creating controls.

    mode: light/dark/system; transparency: 0..60; motion: bool.
    Only this widget tree receives a palette. Persistence belongs to the host app.
    """
    changed = Signal()

    def __init__(self, host, *, mode="light", transparency=60, motion=True, accent=None):
        if not isinstance(host, QtWidgets.QWidget):
            raise TypeError("host must be a QWidget")
        if getattr(host, "_studio_glass_theme", None) is not None:
            raise ValueError("host already has a ThemeController")
        self._validate(mode, transparency, motion, accent)
        super().__init__(host)
        self.host = host
        self.mode, self.transparency, self.motion, self.accent = mode, transparency, motion, accent
        host._studio_glass_theme = self
        hints = QtWidgets.QApplication.styleHints()
        if hasattr(hints, "colorSchemeChanged"):
            hints.colorSchemeChanged.connect(self._system_changed)
        self._refresh()

    @staticmethod
    def _validate(mode, transparency, motion, accent):
        if mode not in ("light", "dark", "system"):
            raise ValueError("mode must be light, dark or system")
        if type(transparency) is not int or not 0 <= transparency <= 60:
            raise ValueError("transparency must be an integer from 0 to 60")
        if type(motion) is not bool:
            raise TypeError("motion must be bool")
        if accent is not None and (not isinstance(accent, str) or not QtGui.QColor(accent).isValid()):
            raise ValueError("accent must be a valid Qt color string or None")

    @property
    def effective_mode(self):
        if self.mode != "system":
            return self.mode
        hints = QtWidgets.QApplication.styleHints()
        if hasattr(hints, "colorScheme"):
            scheme = hints.colorScheme()
            if scheme == QtCore.Qt.ColorScheme.Dark:
                return "dark"
            if scheme == QtCore.Qt.ColorScheme.Light:
                return "light"
        return "dark" if QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorRole.Window).lightness() < 128 else "light"

    def configure(self, *, mode=None, transparency=None, motion=None, accent=_UNSET):
        """Update supplied values. For accent, None resets to the theme's blue."""
        values = (self.mode if mode is None else mode,
                  self.transparency if transparency is None else transparency,
                  self.motion if motion is None else motion, self.accent if accent is _UNSET else accent)
        self._validate(*values)
        self.mode, self.transparency, self.motion, self.accent = values
        self._refresh()

    def _system_changed(self, *args):
        if self.mode == "system":
            self._refresh()

    def _refresh(self):
        self.colors = {k: QtGui.QColor(v) for k, v in THEMES[self.effective_mode].items()}
        if self.accent is not None:
            self.colors["accent"] = QtGui.QColor(self.accent)
        self.host.setPalette(palette_for(self.colors))
        for widget in [self.host, *self.host.findChildren(QtWidgets.QWidget)]:
            # Nested controllers own their subtrees.
            if controller_for(widget) is self:
                callback = getattr(widget, "_appearance_changed", None)
                if callback:
                    callback()
                widget.update()
        self.changed.emit()
