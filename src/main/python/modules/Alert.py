from PyQt5.QtWidgets import QMessageBox

from src.main.python.modules.module import get_stylesheet


class Alert(QMessageBox):
    def __init__(self, title, message, detail):
        super().__init__()
        self.setStyleSheet(open(get_stylesheet()).read())
        self.setIcon(QMessageBox.Warning)
        self.setText(title)
        self.setDetailedText(detail)
        self.setInformativeText(message)
        self.setWindowTitle("Warning!!!")
        self.addButton('Close', QMessageBox.NoRole)
