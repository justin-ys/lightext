from PyQt5.QtWidgets import QMessageBox

class Popup(QMessageBox):
    def __init__(self, title, text, type):
        super().__init__()
        '''

                :param title: Title of the popup
                :param text: Body of the popup
                :param type: "info", "error" or "critical", used for popup icon
                :return:
        '''
        if type == "info":
            self.setIcon(QMessageBox.Information)
        elif type == "error":
            self.setIcon(QMessageBox.Warning)
        elif type == "critical":
            self.setIcon(QMessageBox.Critical)
        else:
            self.setIcon(QMessageBox.Information)

        self.setWindowTitle(title)
        self.setText(text)