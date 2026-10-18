"""Original cached Qt painting. No image capture, blur, engine or global effects."""
import math
from .qt import QtCore as C, QtGui as G, QtWidgets as W, is_valid
from .theme import colors, controller_for, palette_for

Qt = C.Qt


def _motion(widget):
    controller = controller_for(widget)
    return controller.motion if controller else True


def _glass(widget, inset=4, radius=23, owner=None):
    t = colors(owner or widget)
    controller = controller_for(owner or widget)
    transparency = controller.transparency if controller else 60
    dpr = widget.devicePixelRatioF()
    key = (widget.width(), widget.height(), dpr, inset, radius, transparency,
           tuple(v.rgba() for v in t.values()))
    if getattr(widget, "_glass_key", None) == key:
        return widget._glass_bitmap
    bitmap = G.QPixmap(max(1, round(widget.width()*dpr)), max(1, round(widget.height()*dpr)))
    bitmap.setDevicePixelRatio(dpr)
    bitmap.fill(Qt.GlobalColor.transparent)
    p = G.QPainter(bitmap)
    p.setRenderHint(G.QPainter.RenderHint.Antialiasing)
    rect = C.QRectF(widget.rect()).adjusted(inset, inset, -inset, -inset)
    p.setPen(Qt.PenStyle.NoPen)
    light = t["bg_window"].lightness() > 128
    for spread in range(inset, 0, -1):
        p.setBrush(G.QColor(0, 15, 40, 2 if light else 4))
        p.drawRoundedRect(rect.adjusted(-spread*.65, -spread*.3, spread*.65, spread), radius+spread*.5, radius+spread*.5)
    gradient = G.QLinearGradient(rect.topLeft(), rect.bottomRight())
    top, bottom = G.QColor(t["glass"]), G.QColor(t["bg_panel"])
    top.setAlpha(round(255*(1-transparency/100)))
    bottom.setAlpha(top.alpha())
    gradient.setColorAt(0, top)
    gradient.setColorAt(1, bottom)
    p.setBrush(gradient)
    p.setPen(G.QPen(t["border"], .8))
    p.drawRoundedRect(rect, radius, radius)
    if light:
        sheen = G.QLinearGradient(rect.topLeft(), rect.bottomRight())
        for stop, alpha in ((0, 0), (.45, 75), (.6, 0), (1, 0)):
            sheen.setColorAt(stop, G.QColor(255, 255, 255, alpha))
        p.setBrush(sheen)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, radius, radius)
    edge = G.QLinearGradient(rect.topLeft(), rect.bottomLeft())
    for stop, alpha in ((0, 190 if light else 100), (.45, 100 if light else 24), (1, 40 if light else 8)):
        edge.setColorAt(stop, G.QColor(255 if light else 219, 255 if light else 235, 255, alpha))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(G.QPen(edge, .9))
    p.drawRoundedRect(rect.adjusted(.7, .7, -.7, -.7), max(0, radius-1), max(0, radius-1))
    p.end()
    widget._glass_key, widget._glass_bitmap = key, bitmap
    return bitmap


class GlassSurface(W.QWidget):
    """Optional window background with a restrained blue top light."""
    def paintEvent(self, event):
        t = colors(self)
        p = G.QPainter(self)
        p.fillRect(self.rect(), t["bg_window"])
        light = t["bg_window"].lightness() > 128
        glow = G.QRadialGradient(self.width()*.52, -130, max(self.width()*.6, 500))
        tint = G.QColor(t["accent"])
        tint.setAlpha(24 if light else 14)
        glow.setColorAt(0, tint)
        glow.setColorAt(1, G.QColor(0, 0, 0, 0))
        p.fillRect(self.rect(), glow)
        lights = ((.30, -65, 220, G.QColor(97,156,219,60)), (.72, -65, 220, G.QColor(174,190,224,70))) if light else ((.52, -18, 235, G.QColor(93,135,195,32)),)
        for x, y, radius, tint in lights:
            glow = G.QRadialGradient(self.width()*x, y, radius)
            glow.setColorAt(0, tint)
            glow.setColorAt(1, G.QColor(0,0,0,0))
            p.fillRect(C.QRect(0,0,self.width(),min(155,self.height())), glow)


class GlassPanel(W.QWidget):
    """A glass-painted container. Add a normal Qt layout with >=12 px margins."""
    def __init__(self, parent=None, *, radius=23):
        super().__init__(parent)
        if not isinstance(radius, (int, float)) or not math.isfinite(radius) or radius < 0:
            raise ValueError("radius must be finite and non-negative")
        self.radius = radius

    def paintEvent(self, event):
        G.QPainter(self).drawPixmap(0, 0, _glass(self, radius=self.radius))


class GlassButton(W.QPushButton):
    """QPushButton with an internal press spring. clicked/toggled stay native."""
    def __init__(self, *args, variant="glass", **kwargs):
        super().__init__(*args, **kwargs)
        if variant not in ("glass", "primary", "secondary"):
            raise ValueError("variant must be glass, primary or secondary")
        self.variant = variant
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self._press = 0.0
        self.press_animation = C.QVariantAnimation(self)
        self.press_animation.valueChanged.connect(self._frame)
        self.pressed.connect(lambda: self._animate(1.0))
        self.released.connect(lambda: self._animate(0.0))

    def sizeHint(self):
        size = super().sizeHint()
        return C.QSize(max(84, size.width()+24), max(42, size.height()+12))

    def _animate(self, value):
        self.press_animation.stop()
        if not _motion(self):
            self._frame(value)
            return
        curve = C.QEasingCurve(C.QEasingCurve.Type.OutCubic if value else C.QEasingCurve.Type.OutBack)
        curve.setOvershoot(.6)
        self.press_animation.setDuration(85 if value else 230)
        self.press_animation.setEasingCurve(curve)
        self.press_animation.setStartValue(self._press)
        self.press_animation.setEndValue(value)
        self.press_animation.start()

    def _frame(self, value):
        self._press = float(value)
        self.update()

    def _appearance_changed(self):
        if not _motion(self):
            self.press_animation.stop()
            self._press = float(self.isDown())

    def paintEvent(self, event):
        t = colors(self)
        p = G.QPainter(self)
        p.setRenderHint(G.QPainter.RenderHint.Antialiasing)
        rect = C.QRectF(self.rect()).adjusted(3,3,-3,-3)
        p.translate(rect.center())
        p.scale(1-.027*self._press, 1-.027*self._press)
        p.translate(-rect.center())
        primary = self.variant == "primary"
        controller = controller_for(self)
        action_color = t["accent"] if controller and controller.accent is not None else G.QColor("#087cf4" if t["bg_window"].lightness()<128 else "#006fe6")
        fill = G.QColor(action_color) if primary else G.QColor(t["bg_panel"])
        channels = [value/12.92 if value<=.04045 else ((value+.055)/1.055)**2.4 for value in action_color.getRgbF()[:3]]
        luminance = sum(a*b for a,b in zip(channels,(.2126,.7152,.0722)))
        ink = G.QColor("black" if luminance>.179 else "white") if primary else G.QColor(t["text"])
        if not self.isEnabled():
            fill, ink = t["border"], t["muted"]
        elif self.isChecked():
            fill = G.QColor(t["soft"])
            ink = t["accent"]
        elif self.underMouse():
            fill = fill.darker(106) if primary else G.QColor(t["soft"])
        radius = 19 if self.variant == "glass" else 13
        if self.variant == "glass" and self.isEnabled() and not self.underMouse() and not self.isChecked():
            p.drawPixmap(0,0,_glass(self, 3, radius))
        else:
            p.setBrush(fill)
            p.setPen(G.QPen(fill if primary else t["border"], 1))
            p.drawRoundedRect(rect, radius, radius)
        if self.hasFocus() or self.isDefault():
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(G.QPen(t["accent"], 1.5, Qt.PenStyle.DotLine))
            p.drawRoundedRect(rect.adjusted(-1,-1,1,1),radius+1,radius+1)
        option = W.QStyleOptionButton()
        self.initStyleOption(option)
        option.rect = rect.toRect().adjusted(10,0,-10,0)
        for group in G.QPalette.ColorGroup.Active, G.QPalette.ColorGroup.Inactive, G.QPalette.ColorGroup.Disabled:
            option.palette.setColor(group, G.QPalette.ColorRole.ButtonText, ink)
        # Qt draws the real QIcon, mnemonic, RTL placement and standard label.
        self.style().drawControl(W.QStyle.ControlElement.CE_PushButtonLabel, option, p, self)


class GlassSegmentedControl(W.QTabBar):
    """Native QTabBar navigation. Connect currentChanged to QStackedWidget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)
        self.setExpanding(False)
        self.setUsesScrollButtons(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._selection = C.QRectF()
        self.slide_animation = C.QVariantAnimation(self)
        self.slide_animation.setDuration(240)
        curve = C.QEasingCurve(C.QEasingCurve.Type.OutBack)
        curve.setOvershoot(.45)
        self.slide_animation.setEasingCurve(curve)
        self.slide_animation.valueChanged.connect(self._frame)
        self.currentChanged.connect(self._selected)

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        return C.QSize(max(96, size.width()+16), max(48, size.height()+12))

    def _target(self):
        return C.QRectF(self.tabRect(self.currentIndex())).adjusted(6,6,-6,-6) if self.currentIndex() >= 0 else C.QRectF()

    def _selected(self, index):
        target = self._target()
        self.slide_animation.stop()
        if not self.isVisible() or not _motion(self) or self._selection.isEmpty():
            self._frame(target)
            return
        self.slide_animation.setStartValue(self._selection)
        self.slide_animation.setEndValue(target)
        self.slide_animation.start()

    def _frame(self, rect):
        self._selection = C.QRectF(rect)
        self.update()

    def tabLayoutChange(self):
        super().tabLayoutChange()
        if hasattr(self, "slide_animation"):
            self.slide_animation.stop()
            self._selection = self._target()

    def _appearance_changed(self):
        if not _motion(self):
            self.slide_animation.stop()
            self._selection = self._target()

    def paintEvent(self, event):
        t = colors(self)
        p = G.QPainter(self)
        p.setRenderHint(G.QPainter.RenderHint.Antialiasing)
        p.drawPixmap(0,0,_glass(self))
        p.setClipRect(self.rect().adjusted(4,4,-4,-4))
        if self.currentIndex() >= 0:
            p.setBrush(t["selected"])
            p.setPen(G.QPen(t["accent"] if self.hasFocus() else t["border"], .8))
            p.drawRoundedRect(self._selection,19,19)
            edge = G.QLinearGradient(self._selection.topLeft(), self._selection.topRight())
            for stop, alpha in ((0,0),(.5,180),(1,0)):
                edge.setColorAt(stop,G.QColor(255,255,255,alpha))
            p.setPen(G.QPen(edge,1))
            p.drawLine(self._selection.topLeft()+C.QPointF(18,1),self._selection.topRight()+C.QPointF(-18,1))
        for index in range(self.count()):
            option = W.QStyleOptionTab()
            self.initStyleOption(option,index)
            option.rect = self.tabRect(index).adjusted(10,0,-10,0)
            ink = t["accent"] if index == self.currentIndex() else t["muted"]
            option.palette.setColor(G.QPalette.ColorRole.WindowText,ink)
            option.palette.setColor(G.QPalette.ColorGroup.Disabled,G.QPalette.ColorRole.WindowText,t["muted"])
            self.style().drawControl(W.QStyle.ControlElement.CE_TabBarTabLabel,option,p,self)


class _ComboDelegate(W.QStyledItemDelegate):
    def __init__(self, combo):
        super().__init__(combo)
        self.combo = combo

    def sizeHint(self, option, index):
        if index.data(Qt.ItemDataRole.AccessibleDescriptionRole)=="separator":
            return C.QSize(40,12)
        size = super().sizeHint(option,index)
        return C.QSize(size.width()+58,max(44,size.height()+12))

    def paint(self, painter, option, index):
        t = colors(self.combo)
        painter.save()
        if index.data(Qt.ItemDataRole.AccessibleDescriptionRole)=="separator":
            painter.setPen(G.QPen(t["border"],1))
            painter.drawLine(option.rect.left()+12,option.rect.center().y(),option.rect.right()-12,option.rect.center().y())
            painter.restore()
            return
        self.initStyleOption(option,index)
        painter.setRenderHint(G.QPainter.RenderHint.Antialiasing)
        rect = C.QRectF(option.rect).adjusted(3,2,-3,-2)
        selected = index == self.combo.model().index(self.combo.currentIndex(),self.combo.modelColumn(),self.combo.rootModelIndex())
        hover = bool(option.state & (W.QStyle.StateFlag.State_MouseOver | W.QStyle.StateFlag.State_Selected))
        focused = bool(option.state & W.QStyle.StateFlag.State_HasFocus)
        painter.setPen(Qt.PenStyle.NoPen)
        if selected or hover:
            painter.setBrush(t["soft"] if selected else t["hover"])
            painter.drawRoundedRect(rect,10,10)
        if focused:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(G.QPen(t["accent"],1))
            painter.drawRoundedRect(rect.adjusted(.5,.5,-.5,-.5),10,10)
        option.rect = rect.toRect().adjusted(10,0,-30,0)
        option.state &= ~(W.QStyle.StateFlag.State_Selected | W.QStyle.StateFlag.State_MouseOver | W.QStyle.StateFlag.State_HasFocus)
        option.backgroundBrush = G.QBrush(Qt.BrushStyle.NoBrush)
        option.palette = palette_for(t)
        self.combo.style().drawControl(W.QStyle.ControlElement.CE_ItemViewItem,option,painter,self.combo.view())
        if selected:
            painter.setPen(G.QPen(t["accent"],1.8,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap))
            x,y = int(rect.right()-19),int(rect.center().y())
            painter.drawLine(x-5,y,x-1,y+4)
            painter.drawLine(x-1,y+4,x+6,y-4)
        painter.restore()


class GlassComboBox(W.QComboBox):
    """Standard QComboBox data/signals, themed list popup, immediate close."""
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMinimumHeight(42)
        self.setSizeAdjustPolicy(W.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(16)
        self.setStyleSheet("QComboBox {combobox-popup:0;} QComboBox QLineEdit {background:transparent; border:none;}")
        view = W.QListView()
        view.setMouseTracking(True)
        view.setFrameShape(W.QFrame.Shape.NoFrame)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setView(view)
        self.setItemDelegate(_ComboDelegate(self))
        self._popup = view.window()
        self._popup.setObjectName("studioGlassPopup")
        self._popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._popup.installEventFilter(self)
        self.popup_animation = C.QVariantAnimation(self)
        self.popup_animation.setDuration(150)
        self.popup_animation.setEasingCurve(C.QEasingCurve.Type.OutCubic)
        self.popup_animation.valueChanged.connect(self._popup_frame)

    def _appearance_changed(self):
        if not hasattr(self,"_popup"):
            return
        t = colors(self)
        for widget in (self._popup,self.view(),self.view().viewport()):
            widget.setPalette(palette_for(t))
        self._popup.setStyleSheet(f"QFrame#studioGlassPopup {{background:transparent; border:none;}} QListView {{background:{t['bg_panel'].name()}; color:{t['text'].name()}; border:0; border-radius:11px; outline:0;}} QListView::item {{background:transparent; border:none;}}")
        if self._popup.layout():
            self._popup.layout().setContentsMargins(12,12,12,12)
        self.view().viewport().setAutoFillBackground(False)
        if not _motion(self):
            self.popup_animation.stop()
            if hasattr(self,"_popup_geometry"):
                self._popup.setGeometry(self._popup_geometry)
            self._popup.setWindowOpacity(1)
        self._popup.update()
        self.view().viewport().update()

    def paintEvent(self,event):
        t = colors(self)
        p = G.QPainter(self)
        p.setRenderHint(G.QPainter.RenderHint.Antialiasing)
        p.setBrush(t["bg_panel"])
        p.setPen(G.QPen(t["accent"] if self.hasFocus() else t["border"],1))
        p.drawRoundedRect(C.QRectF(self.rect()).adjusted(1,1,-1,-1),12,12)
        option = W.QStyleOptionComboBox()
        self.initStyleOption(option)
        option.palette = palette_for(t)
        # Some Windows native styles ignore palette text colors in CE_ComboBoxLabel.
        # Paint only the closed label; keep Qt's actual model/input/popup behavior.
        field = self.style().subControlRect(W.QStyle.ComplexControl.CC_ComboBox,option,W.QStyle.SubControl.SC_ComboBoxEditField,self)
        field = field.adjusted(5,0,-5,0)
        if not option.currentIcon.isNull():
            icon_rect = C.QRect(field.left(),field.center().y()-self.iconSize().height()//2,self.iconSize().width(),self.iconSize().height())
            icon_rect = W.QStyle.visualRect(self.layoutDirection(),field,icon_rect)
            option.currentIcon.paint(p,icon_rect,Qt.AlignmentFlag.AlignCenter,G.QIcon.Mode.Normal if self.isEnabled() else G.QIcon.Mode.Disabled)
            if self.layoutDirection()==Qt.LayoutDirection.RightToLeft:
                field.adjust(0,0,-self.iconSize().width()-6,0)
            else:
                field.adjust(self.iconSize().width()+6,0,0,0)
        if not self.isEditable():
            p.setPen(t["text"] if self.isEnabled() else t["muted"])
            p.drawText(field,Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeading,self.fontMetrics().elidedText(option.currentText,Qt.TextElideMode.ElideRight,field.width()))
        x,y = (15 if self.layoutDirection()==Qt.LayoutDirection.RightToLeft else self.width()-18),self.height()/2
        p.setPen(G.QPen(t["text"] if self.isEnabled() else t["muted"],1.5))
        p.drawPolyline(G.QPolygonF([C.QPointF(x-4,y-2),C.QPointF(x,y+2),C.QPointF(x+4,y-2)]))

    def eventFilter(self,watched,event):
        if watched == self._popup and event.type()==C.QEvent.Type.Paint:
            G.QPainter(watched).drawPixmap(0,0,_glass(watched,10,23,owner=self))
            return True
        return super().eventFilter(watched,event)

    def showPopup(self):
        if self.count()==0:
            return
        self._appearance_changed()
        super().showPopup()
        self.popup_animation.stop()
        available = self.screen().availableGeometry()
        width = min(max(self.width(),self.view().sizeHintForColumn(self.modelColumn())+44),available.width()-16)
        rows = min(self.count(),self.maxVisibleItems())
        height = min(sum(max(1,self.view().sizeHintForRow(i)) for i in range(rows))+24,available.height()-16)
        point = self.mapToGlobal(C.QPoint(0,self.height()+3))
        x = max(available.left()+8,min(point.x(),available.right()-width-7))
        y = point.y() if point.y()+height <= available.bottom()-7 else self.mapToGlobal(C.QPoint()).y()-height-3
        y = max(available.top()+8,min(y,available.bottom()-height-7))
        self._popup_geometry = C.QRect(x,y,width,height)
        self._popup.setMaximumHeight(available.height()-16)
        self._popup.setGeometry(self._popup_geometry)
        self._popup.layout().activate()
        self.view().doItemsLayout()
        self._popup.setWindowOpacity(1)
        if _motion(self):
            self.popup_animation.setStartValue(0.0)
            self.popup_animation.setEndValue(1.0)
            self.popup_animation.start()

    def _popup_frame(self,value):
        if self._popup.isVisible():
            self._popup.setWindowOpacity(.6+.4*value)
            self._popup.move(self._popup_geometry.topLeft()+C.QPoint(0,round(-6*(1-value))))

    def hidePopup(self):
        # Qt can invoke this virtual during teardown after its child popup died.
        if not is_valid(self._popup) or not is_valid(self.popup_animation):
            return
        self.popup_animation.stop()
        super().hidePopup()
        self._popup.setWindowOpacity(1)


class AppearancePopup(W.QFrame):
    """Optional appearance control. Settings are in-memory until the host saves them."""
    def __init__(self,controller,parent=None):
        super().__init__(parent or controller.host,Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.controller = controller
        controller.destroyed.connect(self.deleteLater)
        self._studio_glass_theme = controller
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(290)
        layout = W.QVBoxLayout(self)
        layout.setContentsMargins(24,22,24,22)
        layout.setSpacing(12)
        row = W.QHBoxLayout()
        row.addWidget(W.QLabel(self.tr("Glass transparency")))
        row.addStretch()
        self.value_label = W.QLabel()
        row.addWidget(self.value_label)
        layout.addLayout(row)
        self.slider = W.QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0,60)
        self.slider.setAccessibleName(self.tr("Glass transparency, zero to sixty percent"))
        self.slider.valueChanged.connect(lambda value: controller.configure(transparency=value))
        layout.addWidget(self.slider)
        self.motion_box = W.QCheckBox(self.tr("Enable motion"))
        self.motion_box.toggled.connect(lambda value: controller.configure(motion=value))
        layout.addWidget(self.motion_box)
        reset = GlassButton(self.tr("Reset to 60%"),variant="secondary")
        reset.clicked.connect(lambda: controller.configure(transparency=60))
        layout.addWidget(reset)
        controller.changed.connect(self._sync)
        self._sync()

    def _sync(self):
        blocker = C.QSignalBlocker(self.slider)
        self.slider.setValue(self.controller.transparency)
        del blocker
        blocker = C.QSignalBlocker(self.motion_box)
        self.motion_box.setChecked(self.controller.motion)
        del blocker
        self.value_label.setText(f"{self.controller.transparency}%")
        self.setPalette(palette_for(self.controller.colors))
        self.update()

    def paintEvent(self,event):
        p = G.QPainter(self)
        p.drawPixmap(0,0,_glass(self,8))
        p.setRenderHint(G.QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(colors(self)["bg_panel"])
        p.drawRoundedRect(C.QRectF(self.rect()).adjusted(14,14,-14,-14),12,12)

    def open_near(self,button):
        self.adjustSize()
        screen = button.screen().availableGeometry()
        point = button.mapToGlobal(C.QPoint(button.width()-self.width(),button.height()+8))
        point.setX(max(screen.left()+8,min(point.x(),screen.right()-self.width()-7)))
        point.setY(max(screen.top()+8,min(point.y(),screen.bottom()-self.height()-7)))
        self.move(point)
        self.show()
        self.slider.setFocus()
