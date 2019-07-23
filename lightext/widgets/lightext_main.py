from PyQt5.QtWidgets import (QWidget, QLabel)

class MainWindow(QWidget):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        text = QLabel(self)
        text.setText("Test")
        self.show()
