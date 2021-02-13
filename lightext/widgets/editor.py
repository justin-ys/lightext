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

    def __init__(self):
        super(TabWindow, self).__init__()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)

        hbox = QHBoxLayout()
        hbox.addWidget(self.tabs)
        self.setLayout(hbox)
        self.tabs.currentChanged.connect(self.updateWindowTitle)
        self.new()

    def save(self):
        tab = self.tabs.currentWidget()

        if tab.path is None:
            # See about native dialog in open()
            path, _ = QFileDialog.getSaveFileName(self, "Save as...", "", "Plaintext (*.txt)",
                                                  options=QFileDialog.DontUseNativeDialog)
            if path:
                tab.save(path)
                self.tabs.setTabText(self.tabs.currentIndex(), basename(path))

        else:
            tab.save(tab.path)

    def open(self):
        # Native dialog looks better. But today, suddenly, it unexplainably just stopped working. Tragic.
        # Don't keep for a release version.
        path, _ = QFileDialog.getOpenFileName(self, caption="Open file...", options=QFileDialog.DontUseNativeDialog)
        if path:
            tab = self.new()
            self.tabs.setCurrentWidget(tab)
            tab.open(path)
            self.tabs.setTabText(self.tabs.currentIndex(), basename(path))
            self.updateWindowTitle()

    def new(self):
        editor = TextEditor()
        index = self.tabs.addTab(editor, "New file")
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

    resizeSignal = pyqtSignal(QSize)

    def __init__(self):
        super().__init__()
        self.cursorPositionChanged.connect(self.update_cursor_blocks)
        self.setStyleSheet("background-color: rgba(123, 111, 145, 60)")
        self.document().setDocumentMargin(1)
        self.path = None
        self._last_selected_block = None

    def save(self, location):
        with open(location, "w") as f:
            f.write(self.toPlainText())
        self.path = location

    def open(self, location):
        with open(location, "r") as f:
            self.setPlainText(f.read())
        self.path = location

    def getBlockRects(self, initialBlock=None, endBlock = None, inclusive = False):
        '''

        :param initialBlock: The block to begin the search at (if not specified, the first block in the editor)
        :param endBlock: The block to end the search at (if not specified, the last block in the editor)
        :param inclusive: Whether to include the last block
        :return: A list of the boundingRects of the editor's QTextBlocks in order, starting from initialBlock
                 and ending at endBlock
        '''
        if not initialBlock:
            block = self.document().firstBlock()
        else:
            block = initialBlock
        blocks = []
        if endBlock:
            endBlockRect = self.document().documentLayout().blockBoundingRect(endBlock)
        while block.isValid():
            rect = self.document().documentLayout().blockBoundingRect(block)
            if endBlock:
                # Comparisons of blocks directly do not work, comparisons of their boundingrects do
                if rect == endBlockRect:
                    if inclusive:
                        blocks.append(rect)
                    break
            blocks.append(rect)
            block = block.next()
        return blocks


    def resizeSignalConnect(self, slot):
        self.resizeSignal.connect(slot)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.resizeSignal.emit(self.size())

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
        #Find top and bottom blocks in viewport. We only need to paint these
        topBlock = self.document().findBlock(self.cursorForPosition(QPoint(0,0)).position())
        bottomright = self.viewport().contentsRect().bottomRight()
        bottomBlock = self.document().findBlock(self.cursorForPosition(bottomright).position())
        number = len(self.getBlockRects(endBlock=topBlock))+1
        boundingbox = painter.boundingRect(self.contentsRect(), Qt.AlignLeft, str(number))
        topHeight = self.verticalScrollBar().value()
        heights = [rect.topLeft().y()-topHeight for rect in self.getBlockRects(topBlock, bottomBlock, inclusive=True)]
        for height in heights:
            boundingbox = painter.boundingRect(self.contentsRect(), Qt.AlignLeft, str(number))
            linebarwidth = boundingbox.width()+4
            # Set only left margin
            frameformat = self.document().rootFrame().frameFormat()
            if frameformat.leftMargin() != linebarwidth:
                frameformat.setLeftMargin(linebarwidth)
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
        offset = self.verticalScrollBar().value()
        block = self.textCursor().block()
        rect = self.document().documentLayout().blockBoundingRect(block)
        rect.moveTop(rect.y()-offset)
        rect.setWidth(rect.width())
        painter.fillRect(rect, QBrush(QColor(10, 10, 10,20)))
        self._paintLineBar(painter)
        super().paintEvent(ev)
