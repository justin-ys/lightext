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


    class ScrollableEditor(QScrollArea):
        def __init__(self, editor):
            super().__init__()
            self._editor = editor

            hbox = QHBoxLayout(self)
            hbox.setSizeConstraint(QLayout.SetMinimumSize)
            hbox.setSpacing(0)

            container = QWidget()
            container.setLayout(hbox)

            editor.newBlockList.connect(self.ensure_editior_visible)
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
        scrollArea = self.ScrollableEditor(editor)

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
        self.setStyleSheet("background-color: rgba(123, 111, 145, 60)")
        self.document().setDocumentMargin(1)
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

    def getBlockRects(self):
        block = self.document().firstBlock()
        blocks = []
        while block.isValid():
            blocks.append(self.document().documentLayout().blockBoundingRect(block))
            block = block.next()
        return blocks

    def updateBlocks(self):
        blocks = self.getBlockRects()
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

    def _paintLineBar(self, painter):
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        number = 1
        boundingbox = painter.boundingRect(self.contentsRect(), Qt.AlignLeft, str(number))
        heights = [blockRect.topLeft().y() for blockRect in self.getBlockRects()]
        for height in heights:
            boundingbox = painter.boundingRect(self.contentsRect(), Qt.AlignLeft, str(number))
            # Set only left margin
            frameformat = self.document().rootFrame().frameFormat()
            frameformat.setLeftMargin(boundingbox.width()+4)
            self.document().rootFrame().setFrameFormat(frameformat)
            # TODO: Find why adding 5 to the height makes it correct, ie find the right way to calculate height
            # in the first place
            painter.drawText(0, height + floor((boundingbox.height() / 2))+5, str(number))
            number += 1
        painter.setCompositionMode(painter.CompositionMode_DestinationAtop)
        painter.fillRect(QRect(0,0, boundingbox.bottomRight().x()+4, self.contentsRect().bottomRight().y()),
                         QBrush(QColor(233, 237, 245, 240)))

    def paintEvent(self, ev):
        painter = QPainter(self.viewport())
        block = self.textCursor().block()
        rect = self.document().documentLayout().blockBoundingRect(block)
        rect.setWidth(rect.width())
        painter.fillRect(rect, QBrush(QColor(10, 10, 10,20)))
        self._paintLineBar(painter)
        super().paintEvent(ev)

    def wheelEvent(self, ev):
        # Disable scrolling in QTextEdit's AbstractScrollArea, because the parent widget does the scrolling
        ev.ignore()