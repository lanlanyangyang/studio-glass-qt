# Studio Glass Qt

[中文说明](README.zh-CN.md) · [API & integration](docs/INTEGRATION.md) · [Validation](docs/VALIDATION.md)

A small glass-style control library for **Qt 6 Widgets**, supporting **PyQt6 and PySide6**. Extracted from an original desktop UI and made independent of its application engine.

Soft blue light, translucent surfaces, fine edge highlights and interruptible spring feedback. **60% material transparency** is the default. The appearance belongs to your widget tree, not the whole application.

![Light gallery](docs/images/light.png)
![Dark gallery](docs/images/dark.png)

These are widget-rendered gallery snapshots, not proof of native platform blur or animation quality. See the validation record for actual test coverage.

## Install from GitHub

Python 3.10+ and one Qt binding are required. This project is **not published on PyPI**.

The `pyside6` extra installs the official **PySide6-Essentials** wheel, which supplies Core/Gui/Widgets/QtTest without downloading WebEngine or other unused Addons.
On Python <3.12 it excludes 6.12.0 after a bare-Qt reference-count failure reproduced in Linux CI; use the supplied extra when installing. See [validation details](docs/VALIDATION.md).

```sh
python -m venv .venv
# Activate .venv using your platform's usual command, then choose ONE:
python -m pip install "studio-glass-qt[pyqt6] @ git+https://github.com/lanlanyangyang/studio-glass-qt.git"
# Or:
python -m pip install "studio-glass-qt[pyside6] @ git+https://github.com/lanlanyangyang/studio-glass-qt.git"
python -m studioglass
```

For reproducible installation, append a reviewed tag or commit after `.git`, for example `.git@<commit-sha>`. If Git is unavailable, download the repository ZIP, extract it, then install from its directory:

```sh
python -m pip install ".[pyqt6]"
python -m studioglass --theme dark
```

## Use in an existing app

```python
from studioglass import ThemeController, GlassButton
from studioglass.qt import QtWidgets as W

app = W.QApplication([])
window = W.QWidget()  # QMainWindow also works
theme = ThemeController(window, mode="light", transparency=60)
layout = W.QVBoxLayout(window)
button = GlassButton("Run", variant="primary")
button.clicked.connect(lambda: print("Your existing action runs immediately"))
layout.addWidget(button)
window.show()
app.exec()
```

Use `GlassSurface` instead of `QWidget` for the optional blue-lit background. You can replace one control at a time; there is no required application shell.

| Component | Native base / purpose |
|---|---|
| `ThemeController` | Per-host light/dark/system theme, accent, transparency, motion |
| `GlassSurface` | Optional window background |
| `GlassPanel` | Cached glass container for a normal Qt layout |
| `GlassButton` | `QPushButton`; native clicked/toggled, QIcon and keyboard behavior |
| `GlassSegmentedControl` | `QTabBar`; connect `currentChanged` to your stack |
| `GlassComboBox` | `QComboBox`; standard item data and themed list popup |
| `AppearancePopup` | Optional transparency/motion controls |

```python
theme.configure(mode="dark", transparency=60, motion=False)
theme.configure(accent="#236ad3")
theme.configure(accent=None)  # restore theme blue
```

## Binding & platform scope

- If your app has already imported one binding, it is reused. Otherwise PyQt6 is preferred if installed, then PySide6. Select explicitly with `STUDIOGLASS_QT_API=pyqt6` or `pyside6` **before importing**. Mixed bindings in one process are rejected.
- Qt 6.5+ APIs are used. Locally verified versions are listed in [VALIDATION](docs/VALIDATION.md); the minimum dependency bound is not a claim that every version has been tested.
- Widgets use logical pixels. Material caches include device pixel ratio, size, theme and transparency.
- Text uses the host's font; no bundled font or forced Chinese/system font. Supply translations through Qt's normal translation mechanism.
- Standard Qt accessibility, focus and keyboard behavior are retained. Set meaningful accessible names in your app. Custom painting does not make every screen-reader/platform combination automatically verified.
- Motion is opt-out with `motion=False`; it is **not automatically synchronized with OS reduced-motion preferences**.

## What this effect does

It paints cached gradients, translucent fills, restrained shadows and edge highlights. It does **not** blur the desktop, capture widgets, refract real content or use an Apple private API. It does not make the entire window transparent. Text and working content stay opaque.

Glass looks most apparent over a gently varied background. On a flat solid color the difference is intentionally subtle. The package supplies no wallpaper, engine, report generator, application configuration or startup JIT cache.

Native file dialogs remain native. Tooltips, system window frames and arbitrary third-party controls are not replaced. Theme changes update colors directly; screenshot-based full-window transitions are deliberately excluded. See [integration limits](docs/INTEGRATION.md#limits).

## Develop

```sh
python -m pip install -e ".[pyqt6]" build
python -m unittest discover -s tests -v
python -m build
```

For headless checks set `QT_QPA_PLATFORM=offscreen`. Test each binding in a separate process. GitHub Actions defines Windows/Linux/macOS checks; consult actual run results before treating those platforms as verified.

## License

Original library code: **MIT**, see [LICENSE](LICENSE). No upstream PyGlass implementation is included. Qt and the selected binding keep their own licenses: PyQt6 is GPLv3/commercial; PySide6 is LGPLv3/GPLv3/commercial. MIT does not replace those obligations. See [dependency notices](THIRD_PARTY_NOTICES.md).
