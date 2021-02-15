from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QPoint
from PyQt5.Qt import QRect
from math import floor

def paint(editor):
    painter = QPainter(editor.viewport())
    font = painter.font()
    font.setPointSize(10)
    painter.setFont(font)
    #Find top and bottom blocks in viewport. We only need to paint these
    topBlock = editor.document().findBlock(editor.cursorForPosition(QPoint(0,0)).position())
    bottomright = editor.viewport().contentsRect().bottomRight()
    bottomBlock = editor.document().findBlock(editor.cursorForPosition(bottomright).position())
    number = len(editor.getBlockRects(endBlock=topBlock))+1
    boundingbox = painter.boundingRect(editor.contentsRect(), Qt.AlignLeft, str(number))
    offset = editor.verticalScrollBar().value()
    heights = [rect.topLeft().y()-offset for rect in editor.getBlockRects(topBlock, bottomBlock, inclusive=True)]
    for height in heights:
        boundingbox = painter.boundingRect(editor.contentsRect(), Qt.AlignLeft, str(number))
        linebarwidth = boundingbox.width()+4
        # Set only left margin
        frameformat = editor.document().rootFrame().frameFormat()
        if frameformat.leftMargin() != linebarwidth:
            frameformat.setLeftMargin(linebarwidth)
            editor.document().rootFrame().setFrameFormat(frameformat)
        # TODO: Find why adding 5 to the height makes it correct, ie find the right way to calculate height
        # in the first place
        painter.drawText(0, height + floor((boundingbox.height() / 2))+5, str(number))
        number += 1
    painter.setCompositionMode(painter.CompositionMode_DestinationAtop)
    painter.fillRect(QRect(0,0, boundingbox.bottomRight().x()+4, editor.contentsRect().bottomRight().y()),
                     QBrush(QColor(233, 237, 245, 240)))