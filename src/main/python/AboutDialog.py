from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from src.main.python.modules.module import get_relative, get_icon_base


class AboutDialog(QDialog):
    def __init__(self, file):
        super().__init__()
        # self.setStyleSheet(open('stylesheet/default.qss').read())
        self.setWindowTitle("XuRequest")
        self.setWindowIcon(QIcon(get_icon_base("main_window_icon.png")))
        browser = QWebEngineView()
        path = get_relative() + "\\" + file
        local_url = QUrl.fromLocalFile(path)
        browser.load(local_url)
        browser.show()
        box = QVBoxLayout()
        box.addWidget(browser)
        self.setLayout(box)
