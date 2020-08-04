import os
import uuid

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from src.main.python.json_viewer import JSONApplication
from src.main.python.APILinkManager import APILinkManager
from src.main.python.dialog.AboutDialog import AboutDialog
from src.main.python.FileTreeView import FileTreeView
from src.main.python.WorkSpaceTab import WorkSpaceTab
from src.main.python.modules.module import *


class Application(QMainWindow):
    api_data_change = pyqtSignal()
    tab_close = pyqtSignal(str)
    tab_action = pyqtSignal(str, str, bool)
    tab_manage = []
    app_close = pyqtSignal(str)
    on_dir_change = pyqtSignal()

    def __init__(self, arg):
        super().__init__()

        self.json_view = None
        self.setWindowTitle("Xu Request")
        self.menu()

        self.l_tab_widget = QTabWidget()
        self.l_tab_widget.setTabsClosable(True)
        for a in arg:
            if os.path.isfile(a):
                self.l_tab_widget.addTab(self.add_tab(a), os.path.basename(a))
        if self.l_tab_widget.count() == 0:
            self.l_tab_widget.addTab(self.add_tab(None), "New request")
        self.l_tab_widget.tabCloseRequested.connect(self.on_tab_close)

        l_file_tree_view = FileTreeView(self)
        l_file_tree_view.on_menu_select.connect(self.on_tree_view_action)
        l_file_tree_view.on_dir_change.connect(lambda: self.on_dir_change.emit())

        q_splitter = QSplitter()
        q_splitter.addWidget(l_file_tree_view)
        q_splitter.addWidget(self.l_tab_widget)

        q_splitter.setStretchFactor(0, 1)
        q_splitter.setStretchFactor(1, 2)
        q_splitter.setContentsMargins(10, 10, 10, 10)

        self.setCentralWidget(q_splitter)

    def closeEvent(self, a0: QtGui.QCloseEvent):
        self.app_close.emit('app')

    def add_tab(self, data_path):
        tab_id = str(uuid.uuid4())
        # if data_path is not None:
        #     tab_id = os.path.basename(data_path)
        w = WorkSpaceTab(self, tab_id, data_path)
        data_new = {"name": str(w), "id": tab_id}
        self.tab_manage.append(data_new)
        return w

    def on_tab_close(self, index: int):
        w = self.l_tab_widget.widget(index)
        for tab in self.tab_manage:
            if tab['name'] == str(w):
                tab_id = tab['id']
                self.tab_close.emit(tab_id)
                self.l_tab_widget.removeTab(index)
                self.tab_manage.remove(tab)
                return 1

        self.l_tab_widget.removeTab(index)
        return 0

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

        save_all_action = QAction(QIcon(get_icon_link('save.svg')), '&Save_all', self)
        save_all_action.setShortcut('Ctrl+Shift+S')
        save_all_action.setStatusTip('Save all API')
        save_all_action.triggered.connect(self.save_all_api)

        exit_action = QAction(QIcon(get_icon_link('exit_to_app.svg')), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.exit)

        file_menu = main_menu.addMenu('&File')
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_all_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        api_link_action = QAction(QIcon(get_icon_link('link.svg')), '&API link manager', self)
        api_link_action.setShortcut('Ctrl+L')
        api_link_action.setStatusTip('API link manager')
        api_link_action.triggered.connect(self.api_link_manager)

        pref_menu = main_menu.addMenu('&Preferences')
        pref_menu.addAction(api_link_action)

        run_action = QAction(QIcon(get_icon_link('play_arrow.svg')), '&Run', self)
        run_action.setShortcut('Ctrl+R')
        run_action.setStatusTip('Run API call')
        run_action.triggered.connect(self.run_api)

        run_save_action = QAction(QIcon(get_icon_link('play_circle_outline.svg')), '&Run && Save', self)
        run_save_action.setShortcut('Ctrl+Shift+R')
        run_save_action.setStatusTip('Run and Save API call')
        run_save_action.triggered.connect(self.run_save_api)

        clear_action = QAction(QIcon(get_icon_link('refresh.svg')), '&Sync', self)
        clear_action.setShortcut('Ctrl+Shift+C')
        clear_action.setStatusTip('Sync param')
        clear_action.triggered.connect(self.sync_api)

        format_action = QAction(QIcon(get_icon_link('star.svg')), '&Format', self)
        format_action.setShortcut('Ctrl+B')
        format_action.setStatusTip('Format result')
        format_action.triggered.connect(self.format_api)

        format_object_action = QAction(QIcon(get_icon_link('star_orange.svg')), '&Format with object', self)
        format_object_action.setShortcut('Ctrl+B')
        format_object_action.setStatusTip('Format result object as JSON')
        format_object_action.triggered.connect(self.format_api_object)

        run_menu = main_menu.addMenu('&Run')
        run_menu.addAction(run_action)
        run_menu.addAction(run_save_action)
        run_menu.addSeparator()
        run_menu.addAction(clear_action)
        run_menu.addAction(format_action)
        run_menu.addAction(format_object_action)

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

        json_action = QAction(QIcon(get_icon_link('json.svg')), '&JSON Viewer', self)
        json_action.setShortcut('Ctrl+V')
        json_action.setStatusTip('Application information')
        json_action.triggered.connect(self.json_viewer)

        plugin_menu = main_menu.addMenu('&Plugin')
        plugin_menu.addAction(json_action)

        about_action = QAction(QIcon(get_icon_link('live_help.svg')), '&About', self)
        about_action.setShortcut('')
        about_action.setStatusTip('Application information')
        about_action.triggered.connect(self.about_show)

        help_menu = main_menu.addMenu('&Help')
        help_menu.addAction(about_action)

        self.setMenuBar(main_menu)

    def new_call(self):
        self.l_tab_widget.addTab(self.add_tab(None), "New request")
        self.l_tab_widget.setCurrentIndex(self.l_tab_widget.count() - 1)

    def api_link_manager(self):
        api_link = APILinkManager()
        api_link.setGeometry(int(self.x() + self.width() / 2 - 300), int(self.y() + self.height() / 2 - 200), 520, 360)
        if api_link.exec():
            self.api_data_change.emit()

    def change_tab_name(self, name: str):
        self.l_tab_widget.setTabText(self.l_tab_widget.currentIndex(), name)

    def on_tree_view_action(self, action: str, data_path):
        if action == "open":
            is_opened = False
            for i in range(self.l_tab_widget.count()):
                if self.l_tab_widget.tabText(i) == os.path.basename(data_path):
                    self.l_tab_widget.setCurrentIndex(i)
                    is_opened = True
                    return is_opened
            if not is_opened:
                self.l_tab_widget.addTab(self.add_tab(data_path), os.path.basename(data_path))
                self.l_tab_widget.setCurrentIndex(self.l_tab_widget.count() - 1)
                return is_opened

    def get_tab_id(self, index):
        w = self.l_tab_widget.widget(index)
        for tab in self.tab_manage:
            if tab['name'] == str(w):
                return tab['id']
        return ""

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
            self.l_tab_widget.addTab(self.add_tab(name[0]), os.path.basename(name[0]))
            self.l_tab_widget.setCurrentIndex(self.l_tab_widget.count() - 1)

    def run_api(self):
        index = self.l_tab_widget.currentIndex()
        if index >= 0:
            tab_id = self.get_tab_id(index)
            self.tab_action.emit(tab_id, "run", False)

    def run_save_api(self):
        index = self.l_tab_widget.currentIndex()
        if index >= 0:
            tab_id = self.get_tab_id(index)
            self.tab_action.emit(tab_id, "run_save", False)

    def sync_api(self):
        index = self.l_tab_widget.currentIndex()
        if index >= 0:
            tab_id = self.get_tab_id(index)
            self.tab_action.emit(tab_id, "sync", False)

    def format_api(self):
        index = self.l_tab_widget.currentIndex()
        if index >= 0:
            tab_id = self.get_tab_id(index)
            self.tab_action.emit(tab_id, "format", False)

    def format_api_object(self):
        index = self.l_tab_widget.currentIndex()
        if index >= 0:
            tab_id = self.get_tab_id(index)
            self.tab_action.emit(tab_id, "format_object", False)

    def save_api(self):
        index = self.l_tab_widget.currentIndex()
        if index >= 0:
            tab_id = self.get_tab_id(index)
            self.tab_action.emit(tab_id, "save", False)

    def save_all_api(self):
        index = self.l_tab_widget.currentIndex()
        if index >= 0:
            self.tab_action.emit("all", "save", False)

    def exit(self):
        self.close()

    def close_tab(self):
        self.on_tab_close(self.l_tab_widget.currentIndex())

    def close_all_tab(self):
        while self.l_tab_widget.count() > 0:
            self.on_tab_close(0)

    def close_other_tab(self):
        keep = self.l_tab_widget.widget(self.l_tab_widget.currentIndex())
        index = 0
        while self.l_tab_widget.count() > 1:
            tab = self.l_tab_widget.widget(index)
            if tab != keep:
                self.on_tab_close(index)
            else:
                index = 1

    def about_show(self):
        msg = AboutDialog("html/about.html")
        msg.setGeometry(int(self.x() + self.width() / 2 - 300), int(self.y() + self.height() / 2 - 200), 520, 360)
        msg.exec_()

    def json_viewer(self):
        if self.json_view is None:
            self.json_view = JSONApplication.run()
            self.json_view.load({})
            self.json_view.showMaximized()
        else:
            self.json_view.showMaximized()
