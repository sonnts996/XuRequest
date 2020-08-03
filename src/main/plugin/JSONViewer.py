import os
import sys
import time
import typing

from PyQt5.QtGui import QIcon, QWindow
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWidgets import QMainWindow

from src.main.dir import current_dir
from src.main.python.modules.ParamEditor import ParamEditor
from src.main.python.modules.module import get_icon_base, get_stylesheet

os.chdir(current_dir())


class JSONViewer(QWidget):
    def __init__(self, argv: typing.List[str]):
        super().__init__()
        self.view_tab = ParamEditor()

        layout = QVBoxLayout()
        layout.addWidget(self.view_tab)

        self.setLayout(layout)


def run(argv):
    window = QMainWindow()
    window.setWindowIcon(QIcon(get_icon_base("main_window_icon.png")))
    window.setStyleSheet(open(get_stylesheet()).read())
    window.setCentralWidget(JSONViewer(argv))
    window.showMaximized()
    return window


if __name__ == '__main__':
    app = QApplication(sys.argv)
    arg = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1:]
    window = QMainWindow()
    window.setWindowIcon(QIcon(get_icon_base("main_window_icon.png")))
    window.setStyleSheet(open(get_stylesheet()).read())
    window.setCentralWidget(JSONViewer(arg))
    window.showMaximized()
    app.setQuitOnLastWindowClosed(True)
    exit_code = app.exec_()
    sys.exit(exit_code)
