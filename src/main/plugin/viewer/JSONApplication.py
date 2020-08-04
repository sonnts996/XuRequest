import os
import sys
import uuid

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMenuBar, QAction, QFileDialog
from PyQt5.QtWidgets import QMainWindow

from src.main.dir import current_dir
from src.main.plugin.viewer.JSONViewer import JSONViewer
from src.main.python.AboutDialog import AboutDialog
from src.main.python.modules.module import get_icon_base, get_stylesheet, get_icon_link, get_last_open_file, \
    get_user_folder

os.chdir(current_dir())


class JSONApplication(QMainWindow):
    tab_action = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(get_icon_base("main_window_icon.png")))
        self.setWindowTitle("JSONViewer")
        self.setStyleSheet(open(get_stylesheet()).read())
        self.menu()
        self.viewer = JSONViewer()
        self.setCentralWidget(self.viewer)

    def load(self, data, tab_id=None, tab_name="Untitled", is_path=False):
        if tab_id is None:
            tab_id = str(uuid.uuid4())
        if tab_name == "" or tab_name.isspace():
            tab_name = "Untitled"
        if is_path:
            try:
                data = open(data, encoding="utf-8").read()
            except Exception as ex:
                data = str(ex)
            self.viewer.load(data, tab_id, tab_name)
        else:
            self.viewer.load(data, tab_id, tab_name)

    def menu(self):
        main_menu = QMenuBar()

        new_action = QAction(QIcon(get_icon_link('note_add.svg')), '&New request', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('New request')
        new_action.triggered.connect(self.new_call)

        open_action = QAction(QIcon(get_icon_link('description.svg')), '&Open/Import', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open/Import document')
        open_action.triggered.connect(self.open_call)

        save_action = QAction(QIcon(get_icon_link('save.svg')), '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save API')
        save_action.triggered.connect(self.save_api)

        exit_action = QAction(QIcon(get_icon_link('exit_to_app.svg')), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.exit)

        file_menu = main_menu.addMenu('&File')
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        clear_action = QAction(QIcon(get_icon_link('refresh.svg')), '&Sync', self)
        clear_action.setShortcut('Ctrl+Shift+C')
        clear_action.setStatusTip('Sync param')
        clear_action.triggered.connect(self.sync_api)

        format_action = QAction(QIcon(get_icon_link('star.svg')), '&.. as JSON', self)
        format_action.setShortcut('Ctrl+B')
        format_action.setStatusTip('Try read object as JSON')
        format_action.triggered.connect(self.format_api)

        run_menu = main_menu.addMenu('&JSON')
        run_menu.addAction(clear_action)
        run_menu.addAction(format_action)

        close_tab_action = QAction(QIcon(get_icon_link('close.svg')), '&Close Tab', self)
        close_tab_action.setShortcut('Ctrl+W')
        close_tab_action.setStatusTip('Close Tab')
        close_tab_action.triggered.connect(self.close_tab)

        close_all_action = QAction(QIcon(get_icon_link('clear_all.svg')), '&Close All Tab', self)
        close_all_action.setShortcut('Ctrl+Shift+W')
        close_all_action.setStatusTip('Close All Tab')
        close_all_action.triggered.connect(self.close_all_tab)

        close_others_action = QAction(QIcon(get_icon_link('tab.svg')), '&Close Others Tab', self)
        close_others_action.setShortcut('Ctrl+Alt+W')
        close_others_action.setStatusTip('Close Others Tab')
        close_others_action.triggered.connect(self.close_other_tab)

        workspace_menu = main_menu.addMenu('&Workspace')
        workspace_menu.addAction(close_tab_action)
        workspace_menu.addAction(close_all_action)
        workspace_menu.addAction(close_others_action)

        about_action = QAction(QIcon(get_icon_link('live_help.svg')), '&About', self)
        about_action.setShortcut('')
        about_action.setStatusTip('Application information')
        about_action.triggered.connect(self.about_show)

        help_menu = main_menu.addMenu('&Help')
        help_menu.addAction(about_action)

        self.setMenuBar(main_menu)

    def new_call(self):
        tab_id = str(uuid.uuid4())
        self.load({}, tab_id)

    def open_call(self):
        init_dir = get_user_folder()
        try:
            fin = open(get_last_open_file(), "r", encoding="utf-8")
            last = fin.read()
            fin.close()

            if last is not None:
                if os.path.exists(last):
                    init_dir = last
        except Exception as ex:
            print(ex)

        name = QFileDialog.getOpenFileName(self, 'Open file', init_dir, "JSON files (*.json)")
        if name[0] != "":
            fout = open(get_last_open_file(), "w", encoding="utf-8")
            fout.write(os.path.dirname(name[0]))
            fout.close()
            tab_id = str(uuid.uuid4())
            self.load(name[0], tab_id, os.path.basename(name[0]), True)
            self.viewer.setCurrentIndex(self.viewer.count() - 1)

    def exit(self):
        self.close()

    def close_tab(self):
        self.viewer.on_tab_close(self.viewer.currentIndex())

    def close_all_tab(self):
        while self.viewer.count() > 0:
            self.viewer.on_tab_close(0)

    def close_other_tab(self):
        keep = self.viewer.widget(self.viewer.currentIndex())
        index = 0
        while self.viewer.count() > 1:
            tab = self.viewer.widget(index)
            if tab != keep:
                self.viewer.on_tab_close(index)
            else:
                index = 1

    def about_show(self):
        msg = AboutDialog("html/about.html")
        msg.setGeometry(int(self.x() + self.width() / 2 - 300), int(self.y() + self.height() / 2 - 200), 520, 360)
        msg.exec_()

    def sync_api(self):
        self.viewer.tab_action("sync")

    def save_api(self):
        self.viewer.tab_action("save")

    def format_api(self):
        self.viewer.tab_action("format")


def run(argv=None):
    view = JSONApplication()
    if argv is not None:
        tab_id = str(uuid.uuid4())
        if len(argv) > 1:
            for arv in argv:
                if os.path.isfile(arv):
                    view.load(arv, tab_id, os.path.basename(arv), True)
                else:
                    view.load(arv, tab_id)
    return view


if __name__ == '__main__':
    app = QApplication(sys.argv)
    arg = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1:]
    window = JSONViewer.run(arg)
    app.setQuitOnLastWindowClosed(True)
    exit_code = app.exec_()
    sys.exit(exit_code)
