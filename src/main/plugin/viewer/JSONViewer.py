import json

from PyQt5.QtWidgets import QTabWidget, QFileDialog

from src.main.python.ResultFormatManager import ResultFormatManager
from src.main.python.modules import jsonpretty
from src.main.python.modules.Alert import Alert
from src.main.python.modules.ParamEditor import ParamEditor


class JSONViewer(QTabWidget):
    tab_manager = {}

    def __init__(self):
        super().__init__()
        self.fmg = None
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.on_tab_close)
        self.setObjectName("FrameTab")

    def on_tab_close(self, index: int):
        w = self.widget(index)
        for tab in self.tab_manager:
            if self.tab_manager[tab] == w:
                del self.tab_manager[tab]
                break
        self.removeTab(index)
        if self.fmg != None:
            self.fmg.close()

    def load(self, data, tab_id, tab_name="Untitled"):
        if isinstance(data, str):
            try:
                new = json.loads(data)
                self.add_tab(new, tab_id, tab_name)
            except Exception as ex:
                print(ex)
                self.add_tab(data, tab_id, tab_name)
        else:
            self.add_tab(data, tab_id, tab_name)

    def add_tab(self, data, tab_id, tab_name):
        if tab_id not in self.tab_manager:
            view_tab = ParamEditor(ParamEditor.vertical_tab)
            view_tab.set_json_data(data)
            view_tab.error.connect(self.print_error)
            self.addTab(view_tab, tab_name)
            self.setCurrentIndex(self.count() - 1)
            self.tab_manager[tab_id] = view_tab
        else:
            view_tab = self.tab_manager[tab_id]
            view_tab.set_json_data(data)
            for i in range(self.count()):
                if self.widget(i) == view_tab:
                    self.setCurrentIndex(i)
                    break

    def tab_action(self, action):
        index = self.currentIndex()
        w = self.widget(index)
        if action == "sync":
            w.sync()
        elif action == "save":
            name = QFileDialog.getSaveFileName(self, 'Save File')
            file = open(name, 'w')
            text = w.text()
            file.write(text)
            file.close()
        elif action == "format":
            self.fmg = ResultFormatManager(self.tabText(index), w.format_data)
            self.fmg.setModal(False)
            self.fmg.setGeometry(int(self.x() + self.width() / 2 - 300), int(self.y() + self.height() / 2 - 200), 520,
                                 360)
            self.fmg.apply_done.connect(self.format_manager_done)
            self.fmg.apply_cancel.connect(self.format_manager_cancel)
            self.fmg.setVisible(True)
            self.fmg.raise_()
            self.fmg.show()

    def format_manager_done(self, data: list):
        index = self.currentIndex()
        w = self.widget(index)
        self.format_result(w, data)
        w.set_format_data(data)
        self.fmg = None

    def format_manager_cancel(self):
        self.fmg = None

    def format_result(self, widget, data):
        result = widget.jsonData
        if not data:
            widget.sync()
        else:
            if isinstance(result, dict) or isinstance(result, list):
                new = jsonpretty.extract(result, data)
                widget.set_json_data(new)
            else:
                widget.sync()

    def print_error(self, o1, o2):
        alert = Alert(o1, o2)
        alert.exec_()
