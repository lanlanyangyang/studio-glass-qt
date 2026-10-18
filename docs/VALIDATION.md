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

The initial CI run passed both Windows and both macOS jobs. Both Ubuntu jobs stopped at QtGui import because `libEGL.so.1` was missing. The workflow now installs `libegl1` and `libopengl0` explicitly on Linux, with the same requirement documented for users.

After that, Linux / Python 3.11.17 / PySide6-Essentials 6.12.0 passed all assertions but crashed at interpreter shutdown (`none_dealloc`). A separate CI process importing **only PySide6**, not this library, observed None references falling 5178 → 4978 after 200 `QLabel.setText` calls and then to 4780 after 200 `processEvents` calls. This isolates a runtime-level problem; no upstream issue or exact build/ABI root cause is claimed. The optional dependency excludes 6.12.0 on Python <3.12. CI retains the bare-Qt check for the replacement version, full tests/normal exit, and an additional Python 3.12 Linux/PySide job. Earlier failures remain in Actions history.

A macOS run exposed a timing-sensitive test that slept exactly 270ms for a 240ms animation. The check now waits, with a 2s bound, for the animation's stopped state before asserting its final rectangle. The animation duration itself is unchanged.

No human macOS/Linux acceptance, exhaustive Qt-version sweep, screen-reader matrix, native OS reduced-motion synchronization, commercial deployment validation or numerical performance benchmark is claimed. Material caches retain one bitmap per live surface; no whole-window or desktop capture is used by the library. Screenshots from the demo are explicitly requested by its `--snapshot` tool only.
