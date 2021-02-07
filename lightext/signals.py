from PyQt5.QtCore import pyqtSignal, QObject

class _LightextSignals(QObject):
    changeWindowTitle = pyqtSignal(str)

    def __init__(self):
        super().__init__()

LightextSignals = _LightextSignals()