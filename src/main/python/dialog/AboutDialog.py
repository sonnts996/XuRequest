from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from src.main.python.modules.module import *


class AboutDialog(QDialog):
    def __init__(self, file):
        super().__init__()
        self.setStyleSheet(open(get_stylesheet()).read())
        self.setWindowTitle("XuRequest")
        self.setWindowIcon(QIcon(get_icon_base(get_window_icon())))
        browser = QWebEngineView()
        path = os.path.join(get_relative(), file)
        print(path)
        local_url = QUrl.fromLocalFile(path)
        browser.load(local_url)
        browser.show()
        box = QVBoxLayout()
        box.addWidget(browser)
        self.setLayout(box)
