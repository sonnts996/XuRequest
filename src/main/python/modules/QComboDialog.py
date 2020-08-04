from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QComboBox, QListView, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit

from src.main.python.modules.module import get_stylesheet, get_icon_base


class QComboDialog(QDialog):
    select = ""
    Text = 0
    ComboBox = 1
    tpe = 0

    def __init__(self, title, text, tpe, data=None):
        super().__init__()
        if data is None:
            data = []
        self.setStyleSheet(open(get_stylesheet()).read())
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(get_icon_base("main_window_icon.png")))
        self.tpe = tpe

        text = QLabel(text)

        if tpe == self.Text:
            self.combobox = QLineEdit()
        elif tpe == self.ComboBox:
            self.combobox = QComboBox()
            lv = QListView()
            lv.setAlternatingRowColors(True)
            self.combobox.setView(lv)

            self.combobox.addItems(data)

        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")

        ok.pressed.connect(self.ok_connect)
        cancel.pressed.connect(self.cancel_connect)

        v = QVBoxLayout()
        v.addWidget(text)
        v.addWidget(self.combobox)

        h = QHBoxLayout()
        h.addWidget(ok, Qt.AlignRight)
        h.addWidget(cancel, Qt.AlignRight)

        v.addLayout(h)
        self.setLayout(v)

    def set_init_text(self, text):
        if self.tpe == self.Text:
            self.combobox.setText(text)

    def ok_connect(self):
        if self.tpe == self.Text:
            self.select = self.combobox.text()
        elif self.tpe == self.ComboBox:
            self.select = self.combobox.currentText()
        self.accept()

    def cancel_connect(self):
        self.reject()
