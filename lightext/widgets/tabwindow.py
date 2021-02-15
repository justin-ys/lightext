from PyQt5.QtWidgets import QWidget, QTabWidget, QFileDialog, QHBoxLayout, QPushButton
from PyQt5.Qt import QIcon, QSize
from ntpath import basename
from functools import partial

from lightext import config
from lightext.signals import LightextSignals
import lightext.pluginmanager as manager


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
        LightextSignals.openFile.connect(self.open_file)
        LightextSignals.openWithDialog.connect(self.open)
        LightextSignals.saveFile.connect(self.save)
        LightextSignals.newFile.connect(self.new)

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
        path, _ = QFileDialog.getOpenFileName(self, "Open file...", "", "Plaintext (*.txt)",
                                              options=QFileDialog.DontUseNativeDialog)
        self.open_file(path)


    def open_file(self, path):
        if path:
            tab = self.new()
            self.tabs.setCurrentWidget(tab)
            tab.open(path)
            self.tabs.setTabText(self.tabs.currentIndex(), basename(path))
            self.updateWindowTitle()

    def new(self):
        editor = manager.get_editor()
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
