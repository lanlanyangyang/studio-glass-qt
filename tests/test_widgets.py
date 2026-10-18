"""Run in a fresh process per binding: python -m unittest discover -s tests -v."""
import os
import subprocess
import sys
import unittest
from studioglass import ThemeController, GlassSurface, GlassPanel, GlassButton, GlassSegmentedControl, GlassComboBox, AppearancePopup
from studioglass.qt import QtCore as C, QtGui as G, QtWidgets as W, BINDING
from studioglass.widgets import _glass
QtTest = __import__(BINDING+".QtTest",fromlist=["QTest"])
QTest = QtTest.QTest
Qt = C.Qt


class WidgetContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = W.QApplication.instance() or W.QApplication([])

    def setUp(self):
        self.host = GlassSurface()
        self.host.resize(640,420)
        self.theme = ThemeController(self.host)
        self.layout = W.QVBoxLayout(self.host)

    def tearDown(self):
        self.host.close()
        self.host.deleteLater()
        self.app.sendPostedEvents(None,C.QEvent.Type.DeferredDelete)
        self.app.processEvents()

    def show(self):
        self.host.show()
        self.app.processEvents()

    def test_validation_and_controller_isolation(self):
        other = W.QWidget()
        original = other.palette().color(G.QPalette.ColorRole.Window)
        self.theme.configure(mode="dark",transparency=0,accent="#0a70db")
        self.theme.configure(transparency=60)
        self.assertEqual(self.theme.accent,"#0a70db")
        self.assertEqual(other.palette().color(G.QPalette.ColorRole.Window),original)
        self.assertEqual(self.theme.effective_mode,"dark")
        for value in (-1,61,True,25.5):
            with self.assertRaises(ValueError):
                self.theme.configure(transparency=value)
        with self.assertRaises(ValueError):
            self.theme.configure(mode="sepia")
        with self.assertRaises(ValueError):
            self.theme.configure(accent="not a color")
        with self.assertRaises(ValueError):
            ThemeController(self.host)
        self.theme.configure(mode="system",accent=None)
        self.assertIn(self.theme.effective_mode,("light","dark"))
        other.deleteLater()

    def test_button_native_signals_icon_and_keyboard(self):
        button = GlassButton("1. &Run 中文",variant="primary")
        icon = self.app.style().standardIcon(W.QStyle.StandardPixmap.SP_DialogApplyButton)
        button.setIcon(icon)
        button.setCheckable(True)
        self.layout.addWidget(button)
        clicks,toggles = [],[]
        button.clicked[bool].connect(clicks.append)
        button.toggled.connect(toggles.append)
        self.show()
        geometry = button.geometry()
        QTest.mouseClick(button,Qt.MouseButton.LeftButton)
        self.assertEqual(clicks,[True])
        self.assertEqual(toggles,[True])
        self.assertEqual(button.text(),"1. &Run 中文")
        self.assertEqual(button.icon().cacheKey(),icon.cacheKey())
        self.assertEqual(button.geometry(),geometry)
        button.setFocus()
        QTest.keyClick(button,Qt.Key.Key_Space)
        self.assertEqual(clicks,[True,False])
        button.setEnabled(False)
        QTest.mouseClick(button,Qt.MouseButton.LeftButton)
        self.assertEqual(len(clicks),2)
        self.theme.configure(motion=False)
        self.assertEqual(button.press_animation.state(),C.QAbstractAnimation.State.Stopped)

    def test_segment_interrupt_resize_remove_disabled_and_rtl(self):
        nav = GlassSegmentedControl()
        self.layout.addWidget(nav)
        for text in ("Short","A much longer section","中文页面"):
            nav.addTab(text)
        self.show()
        self.assertGreater(nav.tabSizeHint(1).width(),nav.tabSizeHint(0).width())
        nav.setCurrentIndex(2)
        QTest.qWait(35)
        current = C.QRectF(nav._selection)
        nav.setCurrentIndex(0)
        self.assertEqual(nav.slide_animation.startValue(),current)
        QTest.qWait(270)
        self.assertEqual(nav._selection,nav._target())
        nav.setTabEnabled(1,False)
        nav.setFocus()
        QTest.keyClick(nav,Qt.Key.Key_Right)
        self.assertEqual(nav.currentIndex(),2)
        self.theme.configure(motion=False)
        nav.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.host.resize(580,400)
        self.app.processEvents()
        self.assertEqual(nav._selection,nav._target())
        while nav.count():
            nav.removeTab(0)
        self.app.processEvents()
        nav.grab()
        self.assertEqual(nav.currentIndex(),-1)

    def test_combo_data_keyboard_escape_and_palette(self):
        combo = GlassComboBox()
        combo.addItem("First",{"id":1})
        combo.addItem("中文选项",{"id":2})
        combo.addItem("Unavailable",{"id":3})
        combo.model().item(2).setEnabled(False)
        self.layout.addWidget(combo)
        changes = []
        combo.currentIndexChanged.connect(changes.append)
        global_effect = self.app.isEffectEnabled(Qt.UIEffect.UI_AnimateCombo)
        self.show()
        for mode in ("dark","light","dark","light"):
            self.theme.configure(mode=mode)
            combo.showPopup()
            QTest.qWait(180)
            self.assertEqual(combo.view().palette().color(G.QPalette.ColorRole.Base),self.theme.colors["bg_panel"])
            self.assertTrue(combo.view().isVisible())
            self.assertTrue(combo.view().viewport().rect().contains(combo.view().visualRect(combo.model().index(2,0))))
            QTest.keyClick(combo.view(),Qt.Key.Key_Escape)
            self.app.processEvents()
            self.assertFalse(combo.view().isVisible())
            self.assertEqual(combo.currentIndex(),0)
        self.assertEqual(changes,[])
        self.assertEqual(self.app.isEffectEnabled(Qt.UIEffect.UI_AnimateCombo),global_effect)
        combo.showPopup()
        QTest.keyClick(combo.view(),Qt.Key.Key_Down)
        QTest.keyClick(combo.view(),Qt.Key.Key_Return)
        self.app.processEvents()
        self.assertEqual(combo.currentData(),{"id":2})
        self.assertEqual(changes,[1])
        self.theme.configure(motion=False)
        combo.showPopup()
        self.assertEqual(combo.popup_animation.state(),C.QAbstractAnimation.State.Stopped)
        combo.hidePopup()

    def test_material_cache_and_image_independence(self):
        panel = GlassPanel()
        self.layout.addWidget(panel)
        image = G.QImage(20,20,G.QImage.Format.Format_ARGB32)
        image.fill(G.QColor("#e52c61"))
        label = W.QLabel()
        label.setPixmap(G.QPixmap.fromImage(image))
        before = label.pixmap().toImage()
        self.layout.addWidget(label)
        self.show()
        bitmap = _glass(panel)
        self.assertIs(bitmap,_glass(panel))
        self.assertEqual(bitmap.devicePixelRatioF(),panel.devicePixelRatioF())
        for value in (0,25,60):
            self.theme.configure(transparency=value)
            new_bitmap = _glass(panel)
            self.assertIs(new_bitmap,_glass(panel))
            self.assertEqual(label.pixmap().toImage(),before)
        self.theme.configure(mode="dark")
        self.assertIsNot(new_bitmap,_glass(panel))

    def test_appearance_sync_does_not_duplicate_updates(self):
        popup = AppearancePopup(self.theme)
        self.theme.configure(transparency=25,motion=False)
        self.assertEqual(popup.slider.value(),25)
        self.assertFalse(popup.motion_box.isChecked())
        changes = []
        self.theme.changed.connect(lambda: changes.append(1))
        popup.slider.setValue(60)
        self.assertEqual(self.theme.transparency,60)
        self.assertEqual(len(changes),1)
        popup.close()

    def test_import_rejects_invalid_or_mixed_binding(self):
        env = dict(os.environ,STUDIOGLASS_QT_API="bad")
        result = subprocess.run([sys.executable,"-c","import studioglass"],env=env,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("must be pyqt6 or pyside6",result.stderr)
        opposite = "pyside6" if BINDING=="PyQt6" else "pyqt6"
        env["STUDIOGLASS_QT_API"] = opposite
        result = subprocess.run([sys.executable,"-c",f"import {BINDING}; import studioglass"],env=env,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("binding conflict",result.stderr)
        result = subprocess.run([sys.executable,"-c","from studioglass import GlassComboBox; from studioglass.qt import QtWidgets as W; app=W.QApplication([]); combo=GlassComboBox(); combo.addItems(['One','Two']); combo.show(); combo.showPopup(); app.processEvents()"],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertNotIn("RuntimeError",result.stderr)

    def test_custom_accent_reaches_primary_paint(self):
        button = GlassButton("Run",variant="primary")
        self.layout.addWidget(button)
        self.theme.configure(accent="#d12938",motion=False)
        self.show()
        image = button.grab().toImage()
        # Away from label, focus and antialiased corner.
        color = image.pixelColor(round(15*image.devicePixelRatio()),round(20*image.devicePixelRatio()))
        self.assertLess(abs(color.red()-209)+abs(color.green()-41)+abs(color.blue()-56),8)

    def test_popup_follows_controller_lifetime_even_with_other_parent(self):
        other = W.QWidget()
        popup = AppearancePopup(self.theme,parent=other)
        destroyed = []
        popup.destroyed.connect(lambda:destroyed.append(True))
        self.host.deleteLater()
        self.app.sendPostedEvents(None,C.QEvent.Type.DeferredDelete)
        self.app.sendPostedEvents(None,C.QEvent.Type.DeferredDelete)
        self.assertEqual(destroyed,[True])
        # Replace host so teardown still owns a valid QWidget.
        self.host = W.QWidget()
        other.deleteLater()

    def test_combo_separator_is_compact_and_unselectable(self):
        combo = GlassComboBox()
        combo.addItems(["First","Second"])
        combo.insertSeparator(1)
        self.layout.addWidget(combo)
        self.show()
        self.assertLess(combo.view().sizeHintForRow(1),combo.view().sizeHintForRow(0))
        self.assertFalse(combo.model().flags(combo.model().index(1,0)) & Qt.ItemFlag.ItemIsSelectable)

    def test_combo_icon_paints_in_editable_and_standard_modes(self):
        combo = GlassComboBox()
        pixmap = G.QPixmap(16,16)
        pixmap.fill(G.QColor("#ff0000"))
        combo.addItem(G.QIcon(pixmap),"Sample")
        self.layout.addWidget(combo)
        self.show()
        for editable in (False,True):
            combo.setEditable(editable)
            self.app.processEvents()
            image = combo.grab().toImage()
            red = sum(1 for x in range(image.width()) for y in range(image.height())
                      if image.pixelColor(x,y).red()>245 and image.pixelColor(x,y).green()<10 and image.pixelColor(x,y).blue()<10)
            self.assertGreater(red,80)


if __name__=="__main__":
    unittest.main()
