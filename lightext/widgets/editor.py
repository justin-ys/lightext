from PyQt5.QtWidgets import QTextEdit, QWidget, QTabWidget, QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton, \
    QScrollArea, QLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QPoint
from PyQt5.Qt import QIcon, QSize, QRect
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont, QRegion
from ntpath import basename
from functools import partial
from math import floor

from lightext import config
from lightext.signals import LightextSignals


class TabWindow(QWidget):
    class __closeWidget__(QPushButton):
        #TODO: Get hovering working in QLabel, or something. QPushButton is ugly
        def __init__(self):
            self.bank = config.ResourceBank()
            super().__init__()
            img = self.bank.load_resource("close")
            self.setIcon(QIcon(img))
            self.setFixedSize(QSize(16,16))

    class lineNumberBar(QWidget):
        def __init__(self):
            super().__init__()
            self.blank = 0
            self.line = 1
            self.positions = []
            self.heights = []
            self.width_hint = 20

            palette = self.palette()
            palette.setColor(palette.Background, QColor(233, 237, 245, 200))
            self.setAutoFillBackground(True)
            self.setPalette(palette)

        def paintEvent(self, event):
            painter = QPainter(self)
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            number = 1
            boundingbox = painter.boundingRect(self.contentsRect(), Qt.AlignLeft|Qt.AlignVCenter, str(number))
            for height in self.heights:
                boundingbox = painter.boundingRect(self.contentsRect(), Qt.AlignLeft|Qt.AlignVCenter, str(number))
                # TODO: Find why adding 3 to the height makes it correct, ie find the right way to calculate height
                # in the first place
                painter.drawText(0, height+floor((boundingbox.height()/4))+3, str(number))
                number += 1
            self.width_hint = boundingbox.width()
            self.updateGeometry()

        def sizeHint(self):
            return QSize(self.width_hint, 0)

        def renderLines(self, blocks):
            heights = []
            for rect in blocks:
                heights.append(rect.topLeft().y()+(rect.height()/2))
            self.heights = heights
            self.update()

        def updateHeight(self, size: QSize):
            #Sets height of linebar based on rect given
            self.resize(self.width(), size.height())

        def scrollTo(self, value):
            self.scroll(0, value)

    class ScrollableEditor(QScrollArea):
        def __init__(self, editor, linebar):
            super().__init__()
            self._editor = editor
            self.linebar = linebar

            hbox = QHBoxLayout(self)
            hbox.setSizeConstraint(QLayout.SetMinimumSize)
            hbox.setSpacing(0)

            container = QWidget()
            container.setLayout(hbox)

            editor.blockListConnect(linebar.renderLines)
            editor.resizeSignalConnect(linebar.updateHeight)
            editor.newBlockList.connect(self.ensure_editior_visible)
            hbox.addWidget(linebar)
            hbox.addWidget(editor)

            self.setWidgetResizable(True)
            self.setWidget(container)
            self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

            self.path = None

        def ensure_editior_visible(self):
            block = self._editor.textCursor().block()
            rect = self._editor.document().documentLayout().blockBoundingRect(block)
            y = rect.bottomRight().y()
            self.ensureVisible(0, y)

        def editor(self):
            return self._editor


        def open(self, path):
            self._editor.open(path)
            self.path = path

        def save(self, path):
            self._editor.save(path)
            self.path = path

    def __init__(self):
        super(TabWindow, self).__init__()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)

        hbox = QHBoxLayout()
        hbox.addWidget(self.tabs)
        self.setLayout(hbox)

        self.tabs.currentChanged.connect(self.updateWindowTitle)

        editor = TextEditor()
        self.new()

    def save(self):
        tab = self.tabs.currentWidget()

        if tab.path is None:
            path, _ = QFileDialog.getSaveFileName(self, "Save as...", "", "Plaintext (*.txt)")
            if path:
                tab.save(path)
                self.tabs.setTabText(self.tabs.currentIndex(), basename(path))

        else:
            tab.save(tab.path)

    def open(self):
        path, _ = QFileDialog.getOpenFileName(self, caption="Open file...")
        if path:
            tab = self.new()
            self.tabs.setCurrentWidget(tab)
            tab.open(path)
            self.tabs.setTabText(self.tabs.currentIndex(), basename(path))
            self.updateWindowTitle()

    def new(self):
        editor = TextEditor()
        linebar = self.lineNumberBar()
        scrollArea = self.ScrollableEditor(editor, linebar)

        index = self.tabs.addTab(scrollArea, "New file")
        close = self.__closeWidget__()
        close.clicked.connect(partial(self.__closeTab__, index))
        self.tabs.tabBar().setTabButton(index, self.tabs.tabBar().RightSide, close)
        self.updateWindowTitle()
        return self.tabs.widget(index)

    def __closeTab__(self, index, success):
        return self.tabs.removeTab(index)

    def updateWindowTitle(self):
        title = self.tabs.tabText(self.tabs.currentIndex())
        LightextSignals.changeWindowTitle.emit("Lightext - " + title)


class TextEditor(QTextEdit):

    newBlockList = pyqtSignal(list)
    resizeSignal = pyqtSignal(QSize)

    def __init__(self):
        super().__init__()
        self.document().blockCountChanged.connect(self.updateBlocks)
        self.newBlockList.connect(self.autoResize)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cursorPositionChanged.connect(self.update_cursor_blocks)
        self.document().setDocumentMargin(1)
        self.setStyleSheet("background-color: rgba(123, 111, 145, 60)")
        if isinstance(self.parentWidget(), QScrollArea):
            self.parentWidget().verticalScrollBar().valueChanged.connect(self.update_cursor_blocks)
        self._last_selected_block = None

    def save(self, location):
        with open(location, "w") as f:
            f.write(self.toPlainText())

    def open(self, location):
        with open(location, "r") as f:
            self.setPlainText(f.read())


    def autoResize(self, blockRects: QRect):
        # Strange calculation error seems to get the height wrong by ~2px, which causes yet stranger graphical glitches
        # if left that way
        height = sum([rect.height() for rect in blockRects]) + 2
        self.setMinimumHeight(height)

    def blockListConnect(self, slot):
        self.newBlockList.connect(slot)

    def updateBlocks(self):
        # Get bounding rectangle of each QTextBlock in document, put it into a list and emit a signal containing it
        block = self.document().firstBlock()
        blocks = []
        while block.isValid():
            blocks.append(self.document().documentLayout().blockBoundingRect(block))
            block = block.next()
        self.newBlockList.emit(blocks)

    def resizeSignalConnect(self, slot):
        self.resizeSignal.connect(slot)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.resizeSignal.emit(self.size())
        self.update()

    def update_cursor_blocks(self):
        block = self.textCursor().block()
        if self._last_selected_block:
            currentBlockRect = self.document().documentLayout().blockBoundingRect(block).toRect()
            lastBlockRect = self.document().documentLayout().blockBoundingRect(self._last_selected_block).toRect()
            region = QRegion(currentBlockRect).united(QRegion(lastBlockRect))
            self.viewport().update(region)
        self._last_selected_block = block

    def paintEvent(self, ev):
        painter = QPainter(self.viewport())
        block = self.textCursor().block()
        rect = self.document().documentLayout().blockBoundingRect(block)
        painter.fillRect(rect, QBrush(QColor(10, 10, 10,20)))
        super().paintEvent(ev)

    def wheelEvent(self, ev):
        # Disable scrolling in QTextEdit's AbstractScrollArea, because the parent widget does the scrolling
        ev.ignore()