from PyQt5.QtWidgets import QTextEdit, QWidget, QTabWidget, QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton, \
    QScrollArea, QLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.Qt import QIcon, QSize, QRect
from PyQt5.QtGui import QPainter, QBrush, QColor
from ntpath import basename
from functools import partial

from lightext import config
from lightext.signals import LightextSignals

#git test
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

        def paintEvent(self, event):
            painter = QPainter(self)
            brush = QBrush(QColor(233, 237, 245, 200))
            painter.setBrush(brush)
            painter.fillRect(self.contentsRect(), brush)
            number = 1
            for height in self.heights:
                painter.drawText(0, height, str(number))
                number += 1
            self.width_hint = painter.boundingRect(self.contentsRect(), Qt.AlignLeft, str(number)).width()
            self.updateGeometry()

        def sizeHint(self):
            return QSize(self.width_hint, 0)

        def renderLines(self, blocks):
            heights = []
            for rect in blocks:
                heights.append(rect.topLeft().y()+13)
            self.heights = heights
            self.update()

        def updateHeight(self, size: QSize):
            #Sets height of linebar based on rect given
            self.resize(self.width(), size.height())

        def scrollTo(self, value):
            self.scroll(0, value)

    class scrollableEditor(QScrollArea):
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
            hbox.addWidget(linebar)
            hbox.addWidget(editor)

            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.setWidgetResizable(True)
            self.setWidget(container)
            self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

            self.path = None

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
        scrollArea = self.scrollableEditor(editor, linebar)

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

    def save(self, location):
        with open(location, "w") as f:
            f.write(self.toPlainText())

    def open(self, location):
        with open(location, "r") as f:
            self.setPlainText(f.read())


    def autoResize(self, blockRects: QRect):
        height = sum([rect.height() for rect in blockRects])
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

