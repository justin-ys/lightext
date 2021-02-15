from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPainter

from lightext.widgets.bases import LightextEditor

def paint(editor: LightextEditor):
    painter = QPainter(editor.viewport())
    painter.drawRect(QRect(100, 100, 100, 100))
    painter.drawText(110, 150, "Hello World!")