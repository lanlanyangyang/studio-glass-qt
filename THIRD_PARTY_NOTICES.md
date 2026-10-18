# Dependency licenses and provenance

Studio Glass Qt's original Python source is MIT licensed. Its glass painting was extracted and generalized from the maintainer's own Qt desktop UI. It contains no PyGlass source, desktop wallpaper, bundled fonts, icons or application model weights. Gallery icons come from Qt's runtime standard icon API.

Dependencies are installed separately, not vendored in this repository:

| Dependency | License information | Official source |
|---|---|---|
| PyQt6 | GPLv3 or Riverbank commercial license; not LGPL | [PyQt](https://en.riverbankcomputing.com/software/pyqt), [license FAQ](https://en.riverbankcomputing.com/commercial/license-faq) |
| PySide6 / Qt for Python | LGPLv3/GPLv3 or Qt commercial license | [Qt for Python](https://doc.qt.io/qtforpython-6/), [commercial use](https://doc.qt.io/qtforpython-6/commercial/index.html) |
| Qt | Terms depend on modules and distribution | [Qt licensing](https://www.qt.io/licensing/) |

The MIT license for this library does not relicense Qt or its bindings. Choose and distribute dependencies in accordance with their terms. Build tools and GitHub Actions are not runtime dependencies.
