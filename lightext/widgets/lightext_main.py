from PyQt5.QtWidgets import (QMainWindow, QAction)

from lightext.widgets.tabwindow import TabWindow
from lightext.signals import LightextSignals

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #Set up tabs
        self.resize(800,600)
        self.setWindowTitle("Lightext")

        tabbedWindow = TabWindow()
        self.setCentralWidget(tabbedWindow)

        saveAction = QAction("Save", self)
        saveAction.triggered.connect(LightextSignals.saveFile.emit)

        openAction = QAction("Open", self)
        openAction.triggered.connect(LightextSignals.openWithDialog.emit)

        newtabAction  = QAction("New", self)
        newtabAction.triggered.connect(LightextSignals.newFile.emit)

        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(LightextSignals.exit.emit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        fileMenu.addAction(newtabAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        LightextSignals.changeWindowTitle.connect(self.setWindowTitle)

        self.show()