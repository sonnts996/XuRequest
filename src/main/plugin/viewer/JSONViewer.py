import json

from PyQt5.QtWidgets import QTabWidget

from src.main.python.modules.ParamEditor import ParamEditor


class JSONViewer(QTabWidget):
    list_data = {}

    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.on_tab_close)

    def on_tab_close(self, index: int):
        w = self.widget(index)
        for tab in self.list_data:
            if self.list_data[tab] == w:
                del self.list_data[tab]
                break
        self.removeTab(index)

    def load(self, data, tab_name):
        if isinstance(data, str):
            try:
                new = json.loads(data)
                self.add_tab(new, tab_name)
            except:
                self.add_tab(data, tab_name)
        else:
            self.add_tab(data, tab_name)

    def add_tab(self, data, tab_name):
        if tab_name not in self.list_data:
            view_tab = ParamEditor(ParamEditor.vertical_tab)
            view_tab.set_json_data(data)
            self.addTab(view_tab, tab_name)
            if tab_name != "New Tab" and tab_name != "Unknown Tab":
                self.list_data[tab_name] = view_tab
            self.setCurrentIndex(self.count() -1)
        else:
            view_tab = self.list_data[tab_name]
            view_tab.set_json_data(data)
            for i in range(self.count()):
                if self.widget(i) == view_tab:
                    self.setCurrentIndex(i)
                    break

    def tab_action(self, action):
        index = self.currentIndex()