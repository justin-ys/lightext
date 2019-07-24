from PyQt5.QtWidgets import (QMainWindow, QAction)
from lightext.widgets.editor import TabWindow

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()

        self.resize(800,600)
        self.setWindowTitle("Lightext")

        editor = TabWindow()
        self.setCentralWidget(editor)

        saveAction = QAction("Save", self)
        saveAction.triggered.connect(editor.save)

        openAction = QAction("Open", self)
        openAction.triggered.connect(editor.open)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        fileMenu.addAction(saveAction)
        fileMenu.addAction(openAction)



        self.show()
