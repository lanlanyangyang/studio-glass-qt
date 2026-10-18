# Validation record — 0.1.0

This record distinguishes automated checks, widget-rendered previews and actual desktop operation. A passing check is not a claim of identical appearance on every OS, screen reader or Qt release.

## Local automated checks

| Environment | Scope | Result |
|---|---|---|
| Windows, Python 3.11.5, PyQt6 6.7.1 | 11 unittest contracts, offscreen Qt platform | Passed |
| Windows, Python 3.12.14, PySide6-Essentials 6.12.0 | Same 11 contracts, fresh binding process | Passed |

Contracts cover validated per-host appearance and isolation, native mouse/keyboard button signals, real icon/text preservation, animation interruption and disabled tab navigation, empty/removing/RTL tabs, combo selection/data/Escape and theme palettes, compact nonselectable separators, material cache invalidation and unchanged image pixels, appearance synchronization, custom accent paint, cross-parent popup cleanup and binding-conflict errors.

An initial Anaconda-based Python 3.11 environment failed while importing PySide6 6.12's QtCore DLL, before this library ran. A separate standard Python 3.12 environment imports and tests that binding successfully. If encountered, use a clean standard-Python environment rather than changing your host application's shared runtime. No universal root cause is claimed for that environment failure.

## Packaging

Both wheel and source archive are built with the standard setuptools backend. The wheel is installed without source-path injection and the gallery/checks run against the installed package. Source archive inspection excludes environments, local evidence, credentials and parent-application files. Exact commands for reproduction:

```sh
python -m build
python -m pip install --force-reinstall --no-deps dist/studio_glass_qt-0.1.0-py3-none-any.whl
python -m unittest discover -s tests -v
python -m studioglass --no-motion
```

Run the last commands without `PYTHONPATH=src`; otherwise they can silently test the checkout instead of the installed package.

## Visual evidence and platform scope

The README PNGs are widget-rendered snapshots of the neutral gallery on Windows at device pixel ratio 1.5. They use the Windows platform plugin and show actual font rendering. They are not desktop-blur evidence or proof of animation quality. Early restricted/offscreen previews with missing fonts were discarded.

Actual Windows desktop input verified an immediate single action receipt, light-to-dark theme switching, opening the themed combo and closing it with Escape, and opening Appearance with keyboard Home/End changing the displayed transparency from 60% to 0% and back to 60%. This is a limited interaction check, not an exhaustive gesture/animation review. The final combo additionally forces its native layout to settle before opening animation and guards late Qt teardown calls; both have automated checks.

GitHub Actions defines an offscreen Python 3.11 matrix across Windows/Linux/macOS and both bindings; configured jobs are not passed jobs. Consult the repository Actions page for the result of the exact commit you use.

No human macOS/Linux acceptance, exhaustive Qt-version sweep, screen-reader matrix, native OS reduced-motion synchronization, commercial deployment validation or numerical performance benchmark is claimed. Material caches retain one bitmap per live surface; no whole-window or desktop capture is used by the library. Screenshots from the demo are explicitly requested by its `--snapshot` tool only.
