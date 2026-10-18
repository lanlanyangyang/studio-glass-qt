# Contributing

Use one Qt binding per fresh process. Install with `python -m pip install -e ".[pyqt6]" build` (or `[pyside6]`), run `python -m unittest discover -s tests -v`, then `python -m build`. Check keyboard/focus, disabled states, interruption, both themes and 0/60% transparency when changing painting.

Please include OS, Python, binding/Qt versions, scale factor and a small runnable reproduction in issues. Share neutral sample content only, with no private files, credentials or personal records.

Keep changes within Qt Widgets. Prefer Qt's existing input, models and signal behavior over parallel custom implementations. Add a regression check for a reproduced defect. State whether evidence is headless, simulated input, an actual displayed window or human interaction; don't label one as another.

The repository's original code contributions are distributed under its MIT license. See THIRD_PARTY_NOTICES.md for dependency terms.
