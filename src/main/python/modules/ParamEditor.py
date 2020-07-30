import json

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QTabWidget, QTreeView, QMenu, QAction, QInputDialog

from src.main.python.modules.JSONEditor import JSONEditor
from src.main.python.modules.module import color_json, get_stylesheet, get_icon_link


class ParamEditor(QTabWidget):
    jsonData = {}
    isParseError = False
    error = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.json_edit = JSONEditor()
        self.table_edit = QTreeView()
        self.model = QStandardItemModel()
        self.table_edit.setAlternatingRowColors(True)

        self.table_edit.setModel(self.model)

        self.addTab(self.table_edit, "UI")
        self.addTab(self.json_edit, "JSON")

        self.table_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_edit.customContextMenuRequested.connect(self.open_menu)
        self.model.itemChanged.connect(self.data_change)
        self.currentChanged.connect(self.tab_selected)

    def set_json_data(self, param):
        self.jsonData = param
        self.update()

    def update(self):
        self.load_param_2_table(self.jsonData)
        self.load_param_2_json_editor(self.jsonData)

    def load_param_2_table(self, param):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['key', 'value'])
        header = self.table_edit.header()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.create_param_ui(self.model.invisibleRootItem(), param, 0, "", [])
        self.table_edit.expandAll()

    def create_param_ui(self, parent, obj, level, parent_name="", item_link=None):
        if item_link is None:
            item_link = []
        if isinstance(obj, list):
            for i in range(len(obj)):
                if isinstance(obj[i], dict) or isinstance(obj[i], list):
                    item = QStandardItem(str(i) + ": ")
                    item.setEditable(False)
                    data = {"key": ":" + str(i), "parent": parent_name, 'level': level, 'link': item_link}
                    item.setData(data)
                    parent.appendRow([item])
                    link = item_link.copy()
                    link.append(":" + str(i))
                    self.create_param_ui(item, obj[i], level, parent_name, link)
                else:
                    item = QStandardItem(str(i) + ": ")
                    item.setEditable(False)
                    value = QStandardItem(str(obj[i]))
                    value.setEditable(True)
                    link = item_link.copy()
                    link.append(":" + str(i))
                    data = {"key": ":" + str(i), "parent": parent_name, 'level': level, 'link': link}
                    item.setData(data)
                    value.setData(data)
                    parent.appendRow([item, value])
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict) or isinstance(value, list):
                    item = QStandardItem(key)
                    item.setEditable(False)
                    data = {"key": key, "parent": parent_name, 'level': level, "link": item_link}
                    item.setData(data)
                    parent.appendRow([item])
                    link = item_link.copy()
                    link.append(key)
                    self.create_param_ui(item, value, level + 1, key, link)
                else:
                    self.add_object(parent, obj[key], level, key, item_link)
        else:
            self.add_object(parent, obj, level, parent_name, item_link)

    def add_object(self, parent, obj, level, parent_name="", item_link=None):
        if item_link is None:
            item_link = []
        item = QStandardItem(parent_name)
        item.setEditable(False)
        value = QStandardItem(str(obj))
        value.setEditable(True)
        data = {"key": parent_name, "parent": "", 'level': level, 'link': item_link}
        item.setData(data)
        value.setData(data)
        parent.appendRow([item, value])

    def load_param_2_json_editor(self, param):
        self.json_edit.setDocument(color_json(param))

    def sync(self):
        if self.currentIndex() == 0:
            self.load_param_2_json_editor(self.jsonData)
        elif self.currentIndex() == 1:
            self.try_sync_table()

    def try_sync_table(self):
        self.isParseError = False
        str_param = self.json_edit.toPlainText()
        try:
            if str_param == "" or str_param.isspace():
                self.jsonData = {}
            else:
                self.jsonData = json.loads(str_param)
            self.load_param_2_json_editor(self.jsonData)
            self.isParseError = False
        except Exception as ex:
            print(ex)
            self.error.emit("JSON Param", str(ex))
            self.isParseError = True
        finally:
            if self.isParseError:
                self.load_param_2_json_editor(str_param)
            else:
                self.load_param_2_json_editor(self.jsonData)
            self.load_param_2_table(self.jsonData)
        return self.isParseError

    def data_change(self, item: QStandardItem):
        data = item.data()
        if data is not None and "link" in data:
            item_link = data['link']
            link = item_link.copy()
            link.append(data['key'])
            self.update_data(self.jsonData, link, item.text(), 0, len(link))

    def update_data(self, obj, link, new, index, end):
        i = link[index]
        if i.startswith(":"):
            i = int(i.replace(":", ""))
        if index == end - 1:
            obj[i] = new
        else:
            self.update_data(obj[i], link, new, index + 1, end)

    def tab_selected(self, arg=None):
        if arg is not None:
            if arg == 0:
                self.try_sync_table()
            else:
                if not self.isParseError:
                    self.load_param_2_json_editor(self.jsonData)

    def open_menu(self, position):
        indexes = self.table_edit.selectedIndexes()
        level = 0
        data_link = []
        link = []
        item = None
        if len(indexes) > 0:
            index = indexes[0]
            item = self.model.itemFromIndex(index)
            data = item.data()
            if data is not None:
                link = data['link']
                data_link = link.copy()
                data_link.append(data['key'])
                level = 1

        menu = QMenu()
        menu.setStyleSheet(open(get_stylesheet()).read())

        delete_action = QAction(QIcon(get_icon_link('delete_forever.svg')), '&Delete key', self)
        delete_action.setStatusTip('Delete')

        new_action = QAction(QIcon(get_icon_link('create_new_folder.svg')), '&Add key', self)
        new_action.setStatusTip('Add key')

        menu.addAction(new_action)
        if level == 1:
            menu.addAction(delete_action)

        action = menu.exec_(self.table_edit.viewport().mapToGlobal(position))

        if action == delete_action:
            if data_link is not None and data_link != []:
                self.remove_data(self.jsonData, data_link, 0, len(data_link))
                self.update()
        elif action == new_action:
            if self.is_list(self.jsonData, link, 0, len(link)):
                data_new = self.get_data(self.jsonData, data_link, 0, len(data_link))
                self.duplicate_data(self.jsonData, link, data_new.copy(), 0, len(link))
                self.update()
            elif self.is_list(self.jsonData, data_link, 0, len(data_link)):
                data_new = self.get_data(self.jsonData, data_link, 0, len(data_link))
                self.add_data(self.jsonData, data_link, data_new.copy(), 0, len(data_link))
                self.update()
            else:
                input_name = QInputDialog()
                input_name.setStyleSheet(open(get_stylesheet()).read())
                text, ok = input_name.getText(self, 'New field', 'Field key:')
                if ok:
                    if data_link:
                        self.add_data(self.jsonData, data_link, text, 0, len(data_link))
                    else:
                        self.jsonData[text] = ""
                    self.update()

    def remove_data(self, obj, link, index, end):
        if index <= end - 1:
            i = link[index]
            if i.startswith(":"):
                i = int(i.replace(":", ""))
            if index == end - 1:
                del obj[i]
            else:
                self.remove_data(obj[i], link, index + 1, end)

    def is_list(self, obj, link, index, end):
        if index <= end - 1:
            i = link[index]
            if i.startswith(":"):
                i = int(i.replace(":", ""))
            if index == end - 1:
                return isinstance(obj[i], list)
            else:
                return self.is_list(obj[i], link, index + 1, end)
        else:
            return False

    def get_data(self, obj, link, index, end):
        if index <= end - 1:
            i = link[index]
            if i.startswith(":"):
                i = int(i.replace(":", ""))
            if index == end - 1:
                return obj[i]
            else:
                return self.get_data(obj[i], link, index + 1, end)
        else:
            return ""

    def add_data(self, obj, link, new, index, end):
        if index <= end - 1:
            i = link[index]
            if i.startswith(":"):
                i = int(i.replace(":", ""))
            if index == end - 1:
                if isinstance(obj[i], list):
                    if len(obj[i]) > 1:
                        obj[i].append(obj[i][0])
                    else:
                        obj[new] = ""
                elif isinstance(obj[i], dict) or str(obj[i]) == "":
                    obj[i] = {}
                    obj[i][new] = ""
                else:
                    obj[new] = ""
            else:
                self.add_data(obj[i], link, new, index + 1, end)

    def duplicate_data(self, obj, link, new, index, end):
        if index <= end - 1:
            i = link[index]
            if i.startswith(":"):
                i = int(i.replace(":", ""))
            if index == end - 1:
                if isinstance(obj[i], list):
                    obj[i].append(new)
            else:
                self.duplicate_data(obj[i], link, new, index + 1, end)
