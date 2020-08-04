import asyncio
import json
import os
import shutil
import threading
from shutil import copyfile

import watchdog.events
import watchdog.observers
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QSizePolicy, QTreeView, QMenu, \
    QAction, QMessageBox
from send2trash import send2trash

from src.main.python import Application
from src.main.python.model.APIData import APIData
from src.main.python.model.MyFile import MyFile
from src.main.python.modules.Alert import Alert
from src.main.python.modules.ProcessRunnable import ProcessRunnable
from src.main.python.modules.QComboDialog import QComboDialog
from src.main.python.modules.module import get_icon_link, get_data_folder, get_list_folder
from src.main.python.modules.module import get_stylesheet
from src.main.python.modules.watchdog_data import watch_winform


class FileTreeView(QWidget):
    on_menu_select = pyqtSignal(str, str)
    on_dir_change = pyqtSignal()

    def __init__(self, parent: Application):
        super().__init__()
        self.stopped = threading.Event()
        self.tree = QTreeView()
        self.handle = self.Handler(self)
        self.list_file = []
        self.get_data_file()
        self.model = QtGui.QStandardItemModel()
        self.item_construct = {}

        v_box = QVBoxLayout()
        v_box.addWidget(self.finder())
        v_box.addWidget(self.tree_view())
        self.setLayout(v_box)
        self.watch_dog()
        parent.app_close.connect(self.exit_push)

        self.tree.setAlternatingRowColors(True)

    def exit_push(self):
        self.stopped.set()

    def finder(self):
        w_find = QLineEdit()
        w_find.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        w_find.textChanged.connect(self.sort_list)
        w_find.setPlaceholderText("Search file..")

        return w_find

    def sort_list(self, text):
        list_sort = []
        if text == "":
            self.show_tree(self.list_file)
        else:
            for data in self.list_file:
                if text.lower() in data.name().lower():
                    list_sort.append(data)
            self.show_tree(list_sort)

    def watch_dog(self):
        watch = ProcessRunnable(target=watch_winform, args=(get_data_folder(), self.handle, self.stopped))
        watch.start()

    class Handler(watchdog.events.PatternMatchingEventHandler):

        def __init__(self, parent):
            super().__init__()
            self.parent = parent

        def on_created(self, event):
            print("Watchdog received created event", event.src_path, sep=" : ")
            asyncio.run(self.parent.file_change('create', event.src_path, event.is_directory))

        def on_modified(self, event):
            print("Watchdog received modified event", event.src_path, sep=" : ")
            asyncio.run(self.parent.file_change('modify', event.src_path, event.is_directory))

        def on_moved(self, event):
            print("Watchdog received move event", event.src_path, event.dest_path, sep=" : ")
            asyncio.run(self.parent.file_change('move', event.src_path, event.is_directory, event.dest_path))

        def on_deleted(self, event):
            print("Watchdog received delete event", event.src_path, sep=" : ")
            asyncio.run(self.parent.file_change('delete', event.src_path, event.is_directory))

    async def file_change(self, tpe, old, is_directory, new=""):
        if tpe == "move":
            self.import_single(self.model.invisibleRootItem(), new)
            self.remove_single(old)
        elif tpe == "delete":
            self.remove_single(old)
        elif tpe == "create":
            self.import_single(self.model.invisibleRootItem(), old)

        if is_directory:
            self.on_dir_change.emit()

    def get_data_file(self):
        self.list_file = []
        self.create_list(get_data_folder())

    def create_list(self, dir):
        lst = os.listdir(path=dir)
        for f in lst:
            path = os.path.join(dir, f)
            file = MyFile()
            if os.path.isdir(path):
                file.setParentName(os.path.basename(dir))
                file.setParent(dir)
                file.setName(f)
                file.setDir(True)
                self.list_file.append(file)
                self.create_list(path)
            else:
                file.setParentName(os.path.basename(dir))
                file.setParent(dir)
                file.setName(f)
                file.setDir(False)
                self.list_file.append(file)

    def tree_view(self):
        self.tree.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_menu)
        self.tree.doubleClicked.connect(self.open_event)
        # self.model.itemChanged.connect(self.data_change)
        self.tree.setModel(self.model)
        self.show_tree(self.list_file)
        return self.tree

    def show_tree(self, list_file):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['List API'])
        self.tree.header().setDefaultSectionSize(180)
        parent = self.model.invisibleRootItem()
        self.item_construct = {}
        self.import_data(parent, list_file)
        self.tree.expandAll()

    def import_data_by_path(self, parent, path: list, index):
        if index < len(path):
            full = os.sep.join(path[:index + 1])
            if full in self.item_construct:
                item = self.item_construct[full]
            else:
                item = QStandardItem(path[index])
                if os.path.isfile(os.path.join(get_data_folder(), full)):
                    item.setToolTip(self.read_description(os.path.join(get_data_folder(), full)))
                item.setEditable(False)
                if not os.path.isdir(os.path.join(get_data_folder(), full)):
                    item.setIcon(QIcon(get_icon_link("text_snippet.svg")))
                else:
                    item.setIcon(QIcon(get_icon_link("folder_yellow.svg")))

                item.setData(full)
                parent.appendRow(item)
                self.item_construct[full] = item

            self.import_data_by_path(item, path, index + 1)

    def read_description(self, path):
        try:
            data = json.loads(open(path, encoding='utf-8').read())
            json_data = APIData()
            json_data.construct(data)
            x = json_data.parseSave().description()
            if x.isspace() or x == "":
                return ".."
            else:
                return x
        except Exception as ex:
            print(ex)
            return ".."

    def import_data(self, parent, list_data):
        for i in list_data:
            self.import_single(parent, i)

    def import_single(self, parent, file_path):
        path = self.path_extract(file_path)
        self.import_data_by_path(parent, path, 0)

    def remove_single(self, file_path):
        path = self.path_extract(file_path)
        full = os.sep.join(path[:len(path)])
        if full in self.item_construct:
            item = self.item_construct[full]
            (item.parent() or self.model.invisibleRootItem()).removeRow(item.row())
            del self.item_construct[full]

    def path_extract(self, file_path):
        if isinstance(file_path, MyFile):
            path = os.path.join(file_path.parent(), file_path.name())
        else:
            path = file_path

        path = path.replace(get_data_folder(), "")
        if path.startswith(os.sep):
            path = path.replace(os.sep, "", 1)
        path = path.split(os.sep)
        return path

    def open_menu(self, position):
        indexes = self.tree.selectedIndexes()
        level = 0
        data = ""
        item = None
        if len(indexes) > 0:
            index = indexes[0]
            item = self.model.itemFromIndex(index)
            data = item.data()
            data = os.path.join(get_data_folder(), data)
            if os.path.isdir(data):
                level = 1
            else:
                level = 2

        menu = QMenu()
        menu.setStyleSheet(open(get_stylesheet()).read())

        rename_action = QAction(QIcon(get_icon_link('edit.svg')), '&Rename', self)
        rename_action.setStatusTip('Rename')

        new_action = QAction(QIcon(get_icon_link('create_new_folder.svg')), '&New Folder', self)
        new_action.setStatusTip('New Folder')

        refresh_action = QAction(QIcon(get_icon_link('refresh.svg')), '&Refresh', self)
        refresh_action.setStatusTip('Refresh')

        delete_action = QAction(QIcon(get_icon_link('delete_forever.svg')), '&Delete', self)
        delete_action.setStatusTip('Delete')

        open_action = QAction(QIcon(get_icon_link('open_in_new.svg')), '&Open', self)
        open_action.setStatusTip('Open file')

        expand_action = QAction(QIcon(), '&Expand', self)
        expand_action.setStatusTip('Expand')

        collapse_action = QAction(QIcon(), '&Collapse', self)
        collapse_action.setStatusTip('Collapse')

        duplicate_action = QAction(QIcon(get_icon_link('content_copy.svg')), '&Duplicate', self)
        duplicate_action.setStatusTip('Duplicate')

        copy_action = QAction(QIcon(get_icon_link('content_copy.svg')), '&Copy', self)
        copy_action.setStatusTip('Copy')

        move_action = QAction(QIcon(get_icon_link('zoom_out_map.svg')), '&Move', self)
        move_action.setStatusTip('Move')

        if level == 1:
            menu.addAction(rename_action)
            menu.addAction(new_action)
            menu.addSeparator()
            menu.addAction(refresh_action)
            menu.addAction(expand_action)
            menu.addAction(collapse_action)
            menu.addSeparator()
            menu.addAction(delete_action)
        elif level == 2:
            menu.addAction(open_action)
            menu.addAction(new_action)
            menu.addAction(refresh_action)
            menu.addSeparator()
            menu.addAction(rename_action)
            menu.addAction(duplicate_action)
            menu.addAction(copy_action)
            menu.addAction(move_action)
            menu.addSeparator()
            menu.addAction(delete_action)
        else:
            menu.addAction(new_action)
            menu.addAction(refresh_action)

        action = menu.exec_(self.tree.viewport().mapToGlobal(position))

        if action == open_action:
            if data != "":
                self.on_menu_select.emit("open", data)
        elif action == refresh_action:
            self.show_tree(self.list_file)
        elif action == expand_action:
            if item is not None:
                self.tree.expand(item.index())
        elif action == collapse_action:
            if item is not None:
                self.tree.collapse(item.index())
        elif action == delete_action:
            if data != "":
                msg = QMessageBox()
                msg.setStyleSheet(open(get_stylesheet()).read())
                msg.setIcon(QMessageBox.Warning)
                msg.setBaseSize(QSize(500, 300))
                msg.setText("Delete file.")
                msg.setInformativeText(
                    "Are you sure to detele " + os.path.basename(data) + "?")
                msg.setWindowTitle("Delete Warning!!!")
                msg.addButton('Delete', QMessageBox.YesRole)
                msg.addButton('Move to Trash', QMessageBox.YesRole)
                msg.addButton('Cancel', QMessageBox.NoRole)

                rs = msg.exec_()
                if rs == 0:
                    if os.path.isdir(data):
                        shutil.rmtree(data)
                    else:
                        os.remove(data)
                elif rs == 1:
                    send2trash(data)
        elif action == new_action:
            if data == "":
                data = get_data_folder()
            # input_name = QInputDialog()
            # input_name.setStyleSheet(open(get_stylesheet()).read())
            # text, ok = input_name.getText(self, 'New Folder', 'Folder name:')
            inp = QComboDialog('New Folder', 'Folder name:', QComboDialog.Text)
            ok = inp.exec_()
            if ok and inp.select:
                if os.path.isdir(data):
                    try:
                        os.mkdir(os.path.join(data, inp.select))
                    except Exception as ex:
                        alert = Alert("Error", "Create folder error", str(ex))
                        alert.exec_()
                        print(ex)
                else:
                    new = os.path.join(os.path.dirname(data), inp.select)
                    try:
                        os.mkdir(new)
                    except Exception as ex:
                        alert = Alert("Error", "Create folder error", str(ex))
                        alert.exec_()
                        print(ex)
        elif action == rename_action:
            if data != "":
                # input_name = QInputDialog()
                # input_name.setStyleSheet(open(get_stylesheet()).read())
                # text, ok = input_name.getText(self, 'Rename file', 'New name:')
                inp = QComboDialog('Rename file', 'New name:', QComboDialog.Text)
                ok = inp.exec_()
                if ok and inp.select:
                    if os.path.isdir(data):
                        new = os.path.join(os.path.dirname(data), inp.select)
                        try:
                            os.rename(data, new)
                        except Exception as ex:
                            alert = Alert("Error", "Rename folder error", str(ex))
                            alert.exec_()
                            print(ex)
                    else:
                        filename, file_extension = os.path.splitext(data)
                        new = os.path.join(os.path.dirname(data), inp.select + file_extension)
                        try:
                            os.rename(data, new)
                        except Exception as ex:
                            alert = Alert("Error", "Rename file error", str(ex))
                            alert.exec_()
                            print(ex)
        elif action == move_action:
            if data != "":
                items = get_list_folder(get_data_folder(), get_data_folder())
                #
                # item, ok = QInputDialog.getItem(self, "Select folder dialog",
                #                                 "Select the destination folder", items, 0, False)

                inp = QComboDialog("Move", "Select the destination folder", QComboDialog.ComboBox, items)
                ok = inp.exec_()

                if ok and inp.select:
                    folder = inp.select
                    if inp.select.startswith(os.sep):
                        folder = inp.select.replace(os.sep, "", 1)
                    new = os.path.join(get_data_folder(), folder, os.path.basename(data))
                    try:
                        os.rename(data, new)
                    except Exception as ex:
                        alert = Alert("Error", "Move file error", str(ex))
                        alert.exec_()
                        print(ex)
        elif action == duplicate_action:
            if data != "":
                # input_name = QInputDialog()
                # input_name.setStyleSheet(open(get_stylesheet()).read())
                # text, ok = input_name.getText(self, 'Duplicate file', 'New name:')
                inp = QComboDialog('Duplicate file', 'New name:', QComboDialog.Text)
                filename, file_extension = os.path.splitext(data)
                inp.set_init_text(filename)
                ok = inp.exec_()
                if ok and inp.select:
                    new = os.path.join(os.path.dirname(data), inp.select + file_extension)
                    try:
                        copyfile(data, new)
                    except Exception as ex:
                        alert = Alert("Error", "Duplicate file error", str(ex))
                        alert.exec_()
                        print(ex)
        elif action == copy_action:
            if data != "":
                items = get_list_folder(get_data_folder(), get_data_folder())
                inp = QComboDialog("Copy", "Select the destination folder", QComboDialog.ComboBox, items)
                ok = inp.exec_()
                # item, ok = QInputDialog.getItem(self, "Select folder dialog",
                #                                 "Select the destination folder", items, 0, False)

                if ok and inp.select:
                    folder = inp.select
                    if inp.select.startswith(os.sep):
                        folder = inp.select.replace(os.sep, "", 1)
                    new = os.path.join(get_data_folder(), folder, os.path.basename(data))
                    try:
                        copyfile(data, new)
                    except Exception as ex:
                        alert = Alert("Error", "Copy file error", str(ex))
                        alert.exec_()
                        print(ex)

    def open_event(self, index):
        item = self.model.itemFromIndex(index)
        if item is not None:
            data = item.data()
            data = os.path.join(get_data_folder(), data)
            if os.path.isdir(data):
                level = 1
            else:
                level = 2
            if data != "":
                if level == 2:
                    self.on_menu_select.emit("open", data)
                elif level == 1:
                    if not self.tree.isExpanded(item.index()):
                        self.tree.collapse(item.index())
                    else:
                        self.tree.expand(item.index())
