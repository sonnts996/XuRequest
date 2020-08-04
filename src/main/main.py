import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from src.main.dir import current_dir
from src.main.plugin.viewer import JSONApplication
from src.main.python.Application import Application
from src.main.python.modules.module import get_icon_base, get_stylesheet


def show_request(argv):
    app = QApplication(sys.argv)
    window = Application(argv)
    window.setWindowIcon(QIcon(get_icon_base("main_window_icon.png")))
    window.setStyleSheet(open(get_stylesheet()).read())
    window.showMaximized()
    app.setQuitOnLastWindowClosed(True)
    exit_code = app.exec_()
    sys.exit(exit_code)


def show_json_view(argv):
    app = QApplication(sys.argv)
    window = JSONApplication.run(argv)
    window.showMaximized()
    app.setQuitOnLastWindowClosed(True)
    exit_code = app.exec_()
    sys.exit(exit_code)


os.chdir(current_dir())

if __name__ == '__main__':

    arg = ""
    if len(sys.argv) > 1:
        if sys.argv[1] == "-view":
            if len(sys.argv) > 2:
                show_json_view(sys.argv[2:])
            else:
                show_json_view([])
        else:
            arg = sys.argv[1:]
            show_request(arg)
    else:
        show_request(arg)
