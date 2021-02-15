from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QSize, QRect
from PyQt5.QtGui import QPainter, QBrush, QColor, QRegion

from lightext.widgets.bases import LightextEditor

class Editor(LightextEditor):

    resizeSignal = pyqtSignal(QSize)

    def __init__(self):
        super().__init__()
        self.cursorPositionChanged.connect(self.update_cursor_blocks)
        self.setStyleSheet("background-color: rgba(123, 111, 145, 60)")
        self.document().setDocumentMargin(1)
        self.path = None
        self._last_selected_block = None

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
        # Update the areas of the previously selected and currently selected blocks in the editor to avoid artifacts
        block = self.textCursor().block()
        if self._last_selected_block:
            currentBlockRect = self.document().documentLayout().blockBoundingRect(block).toRect()
            lastBlockRect = self.document().documentLayout().blockBoundingRect(self._last_selected_block).toRect()
            viewportoffset = self.verticalScrollBar().value()
            currentBlockRect.moveTop(currentBlockRect.y()-viewportoffset)
            lastBlockRect.moveTop(lastBlockRect.y()-viewportoffset)
            region = QRegion(currentBlockRect).united(QRegion(lastBlockRect))
            self.viewport().update(region)
        self._last_selected_block = block

    def paintEvent(self, ev):
        painter = QPainter(self.viewport())
        viewportoffset = self.verticalScrollBar().value()
        block = self.textCursor().block()
        rect = self.document().documentLayout().blockBoundingRect(block)
        rect.moveTop(rect.y()-viewportoffset)
        rect.setWidth(rect.width())
        painter.fillRect(rect, QBrush(QColor(10, 10, 10,20)))
        painter.end()
        super().paintEvent(ev)