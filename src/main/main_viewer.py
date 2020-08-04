import sys

from PyQt5.QtWidgets import QApplication

from src.main.python.json_viewer import JSONApplication
from src.main.python.modules.module import *


def show_json_view(argv):
    app = QApplication(sys.argv)
    window = JSONApplication.run(argv)
    window.load({})
    window.showMaximized()
    app.setQuitOnLastWindowClosed(True)
    exit_code = app.exec_()
    sys.exit(exit_code)


os.chdir(current_dir())

if __name__ == '__main__':

    arg = ""
    if len(sys.argv) > 1:
        show_json_view(sys.argv[1:])
    else:
        show_json_view(arg)
