from PyQt5.QtWidgets import (QTextEdit, QWidget, QTabWidget, QFileDialog, QVBoxLayout, QPushButton)
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QIcon, QSize
from ntpath import basename
from functools import partial
from lightext import config



class TabWindow(QWidget):
    class __closeWidget__(QPushButton):
        #TODO: Get hovering working in QLabel, or something. QPushButton is ugly
        def __init__(self):
            self.bank = config.ResourceBank()
            super().__init__()
            img = self.bank.load_resource("close")
            self.setIcon(QIcon(img))
            self.setFixedSize(QSize(16,16))
            #self.setStyleSheet("border: none;")


    def __init__(self):
        super(TabWindow, self).__init__()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        self.setLayout(vbox)

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


    def new(self):
        index = self.tabs.addTab(TextEditor(), "New file")
        close = self.__closeWidget__()
        close.clicked.connect(partial(self.__closeTab__, index))
        self.tabs.tabBar().setTabButton(index, self.tabs.tabBar().RightSide, close)
        return self.tabs.widget(index)

    def __closeTab__(self, index, success):
        return self.tabs.removeTab(index)




class TextEditor(QTextEdit):

    def __init__(self):
        super(TextEditor, self).__init__()
        self.path = None

    def save(self, location):
        with open(location, "w") as f:
            f.write(self.toPlainText())

        self.path = location

    def open(self, location):
        with open(location, "r") as f:
            self.setPlainText(f.read())

        self.path = location

