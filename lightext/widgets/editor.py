from PyQt5.QtWidgets import (QTextEdit, QWidget, QTabWidget, QFileDialog, QVBoxLayout)

def filename_from_path(path):
    return path.split("/")[-1]

class TabWindow(QWidget):
    def __init__(self):
        super(TabWindow, self).__init__()

        self.tabs = QTabWidget()

        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        self.setLayout(vbox)

        editor = TextEditor()
        self.tabs.addTab(editor, "New File")

    def save(self):
        tab = self.tabs.currentWidget()

        if tab.path is None:
            path, _ = QFileDialog.getSaveFileName(self, "Save as...", "", "Plaintext (*.txt)")
            if path:
                tab.save(path)
                self.tabs.setTabText(self.tabs.currentIndex(), filename_from_path(path))

        else:
            tab.save(tab.path)

    def open(self):
        tab = self.new()
        path, _ = QFileDialog.getOpenFileName(self, caption="Open file...")
        if path:
            tab.open(path)
            self.tabs.setTabText(self.tabs.currentIndex(), filename_from_path(path))

    def new(self):
        return self.tabs.addTab(TextEditor(), "New file")

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

