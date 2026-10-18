# Integration and API

## Choose a binding

Import your existing binding first, or set `STUDIOGLASS_QT_API=pyqt6|pyside6` before any Qt imports. `studioglass.qt` exports `QtCore`, `QtGui`, `QtWidgets`, `Signal` and `BINDING`; this is a small binding selector, not a Qt replacement. Restart the process to change bindings.

## Appearance lifecycle

```python
theme = ThemeController(host, mode="system", transparency=60, motion=True)
theme.configure(mode="dark")
theme.configure(transparency=25)  # integer 0..60; affects material, not children
theme.configure(motion=False)    # ongoing custom animations settle immediately
theme.configure(accent="#236ad3")
theme.configure(accent=None)     # reset accent
theme.changed.connect(on_appearance_changed)  # no arguments
```

Create the controller before creating controls. Keep one per host; a duplicate is rejected. It owns a palette on that host tree, never `QApplication.setPalette/setStyleSheet`. Standard children inherit Qt palettes, although platform-native styles and explicit child styles may override some roles. A separately controlled child tree keeps its own appearance.

Properties are readable: `mode`, `effective_mode`, `transparency`, `motion`, `accent`, `colors` (QColor mapping). **Use configure() to change them**. `changed` reports a configuration refresh, not a business action. Updating one setting preserves the others. Invalid modes, colors, non-integer/out-of-range transparency and non-boolean motion are rejected before mutation.

`system` reads Qt's reported color scheme (Qt 6.5+), falls back to the application palette if unknown, and reacts to `colorSchemeChanged`. Platform plugins may not report the OS scheme; offer manual light/dark selection. The library does not force the system theme.

Persistence is optional host policy:

```python
settings = QtCore.QSettings("YourOrganization", "YourApplication")
saved = settings.value("glass/transparency", 60, type=int)
theme = ThemeController(host, transparency=max(0, min(60, saved)))
theme.changed.connect(lambda: settings.setValue("glass/transparency", theme.transparency))
```

## Controls

- `GlassSurface(parent=None)`: optional subtle background; ordinary QWidget layout.
- `GlassPanel(parent=None, radius=23)`: container; use layout margins >=12px so content clears its painted edges. Radius must be finite and non-negative.
- `GlassButton(..., variant="glass")`: standard QPushButton constructor overloads. Variants: `glass`, `primary`, `secondary`. Standard `setIcon`, `setCheckable`, `clicked`, `toggled`, mnemonics and focus remain available. Do not use a stylesheet to replace its custom-painted face; use a native QPushButton when full platform styling is required.
- `GlassSegmentedControl(parent=None)`: QTabBar methods and `currentChanged(int)`. Add/remove/disable tabs normally; connect to `QStackedWidget.setCurrentIndex`. Label widths adapt to the font, including icons. Native scroll buttons handle constrained width. Reordering/closable tabs and per-tab custom colors are outside the v0.1 visual contract.
- `GlassComboBox(parent=None)`: QComboBox methods and signals. Item text/icon/data, disabled model items and standard list selection are preserved. Supports editable mode using Qt's line edit. The supplied presentation is for flat lists; tree/table views, custom popup delegates and user-replaced views are outside the v0.1 contract. Popup fills stay opaque for readable text; only its shell is glass. Escape closes immediately and opening does not change selection.
- `AppearancePopup(theme, parent=None)`: optional `open_near(button)`, `slider` and `motion_box`. Labels use Qt `tr()`; install a QTranslator in your host for localization. Outside click/Escape uses native Qt popup behavior. It does not save settings or alter OS preferences.

## Keyboard and motion

Buttons use normal Qt shortcuts/Space/Enter according to their native focus/default settings. Segmented navigation uses QTabBar arrows, skipping disabled items. Combo menus keep arrows, Enter, Escape and scrolling. Give controls accessible names that describe their purpose in your application.

Button feedback scales its painting, not geometry or hit area; the normal click signal does not wait for animation. Navigation retargets from its current drawn rectangle. Popup closure is immediate to release the native grab. `motion=False` stops custom animation; it does not change global Qt animation settings or detect OS preferences automatically.

## Limits

Material caching stores one bitmap per live surface, keyed by size, DPR, colors and transparency; it does not retain every slider value. No per-frame blur or background capture occurs. Paint geometry uses logical pixels; Qt's device-pixel-ratio converts the cached raster size.

There is no desktop blur, real refraction, automatic page animation, screenshot-based theme fade, window chrome replacement, full QSS framework, report/model code or web/mobile adapter. Glass color and apparent transparency depend on the parent background. The blue-lit GlassSurface is optional. Avoid stacking many translucent panels over text/images.

For an existing application, attach a controller to the smallest subtree you want to theme. Your global stylesheets can take precedence over palette roles, especially on native or third-party controls; test that interaction rather than deleting the host stylesheet. Native file dialogs and menu bars remain native.

## Troubleshooting

- **No binding installed:** install exactly one extra in the interpreter you run.
- **Binding conflict:** start a fresh process, select the same binding as the host application.
- **Popup wrong color:** remove conflicting host QSS for QListView/combos; report a minimal example. The library reapplies its own popup palette at every opening.
- **No OS theme notification:** use manual mode; Qt plugin support differs by platform.
- **No display server / xcb error:** use `QT_QPA_PLATFORM=offscreen` for automation, or provide a display for interactive use. Offscreen rendering is not user acceptance.
- **Subtle effect:** use the optional background, and compare 0/60%. It is intentionally a light material rather than a blur filter.

Official references: [QComboBox](https://doc.qt.io/qt-6/qcombobox.html), [QStyleHints](https://doc.qt.io/qt-6/qstylehints.html#colorScheme-prop), [High DPI](https://doc.qt.io/qt-6.8/highdpi.html), [packaging optional dependencies](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#dependencies-optional-dependencies).
