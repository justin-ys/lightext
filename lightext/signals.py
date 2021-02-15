from PyQt5.QtCore import pyqtSignal, QObject
import sys


class _LightextSignals(QObject):
    changeWindowTitle = pyqtSignal(str)
    # Open a file in the editor of the current tab
    openFile = pyqtSignal(str)
    # Open a file with a selection dialog in the current tab
    openWithDialog = pyqtSignal()
    # Save the file of the current editor
    saveFile = pyqtSignal()
    # Open a new file
    newFile = pyqtSignal()
    # Exit the program
    exit = pyqtSignal()
    def __init__(self):
        super().__init__()

# Make a single object for bound signals, so it can be used from anywhere in the program
LightextSignals = _LightextSignals()

LightextSignals.exit.connect(sys.exit)