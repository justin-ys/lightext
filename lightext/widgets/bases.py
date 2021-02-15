from PyQt5.QtWidgets import QTextEdit

import lightext.pluginmanager as manager

class LightextEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self._paintaddons = manager.get_editor_paint_addons()

    def save(self, location):
        with open(location, "w") as f:
            f.write(self.toPlainText())
        self.path = location

    def open(self, location):
        with open(location, "r") as f:
            self.setPlainText(f.read())
        self.path = location

    def paintEvent(self, ev):
        for action in self._paintaddons:
            action(self)
        super().paintEvent(ev)