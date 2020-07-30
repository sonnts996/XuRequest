import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from src.main.dir import current_dir
from src.main.python.Application import Application
from src.main.python.modules.module import get_icon_base, get_stylesheet

os.chdir(current_dir())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    arg = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1:]
    window = Application(arg)
    window.setWindowIcon(QIcon(get_icon_base("main_window_icon.png")))
    window.setStyleSheet(open(get_stylesheet()).read())
    window.showMaximized()
    app.setQuitOnLastWindowClosed(True)
    exit_code = app.exec_()
    sys.exit(exit_code)
