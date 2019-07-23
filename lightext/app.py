import sys
from lightext.widgets.lightext_main import MainWindow
from PyQt5.Qt import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())