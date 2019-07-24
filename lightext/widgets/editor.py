from PyQt5.QtWidgets import (QTextEdit, QWidget, QTabWidget, QFileDialog, QVBoxLayout)

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
            path, _ = QFileDialog.getSaveFileName(self, "Save as...", "", "Plaintext (.txt)")
            if path:
                tab.save(path)

        else:
            tab.save(tab.path)

class TextEditor(QTextEdit):

    def __init__(self):
        super(TextEditor, self).__init__()
        self.path = None

    def save(self, location):
        with open(location, "w") as f:
            f.write(self.toPlainText())

        self.path = location
