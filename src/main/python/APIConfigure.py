from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItemModel, QCursor
from PyQt5.QtWidgets import QWidget, QTextEdit, QHBoxLayout, QPushButton, QSplitter, QLineEdit, QComboBox, \
    QVBoxLayout, QGroupBox, QApplication, QListView

from src.main.python import Application
from src.main.python.model.APIConfig import APIConfig
from src.main.python.model.APIData import APIData
from src.main.python.model.APILink import APILink
from src.main.python.model.APIResponse import APIResponse
from src.main.python.model.APISave import APISave
from src.main.python.model.MyFile import MyFile
from src.main.python.request import httprequest
from src.main.python.json_viewer.ParamEditor import ParamEditor
from src.main.python.modules.module import *


class APIConfigure(QSplitter):
    console = pyqtSignal(str, str)
    result = pyqtSignal(APIData, bool, bool)
    tab_id = ""

    def get_list_view(self):
        lv = QListView()
        lv.setAlternatingRowColors(True)
        return lv

    def __init__(self, parent: Application, tab_id: str, data):
        super().__init__()
        self.w_widget_tab = ParamEditor()
        self.model = QStandardItemModel()
        self.w_description = QTextEdit()
        self.file_name = QLineEdit()
        self.folder = QComboBox()
        self.w_api_param = QComboBox()
        self.w_api_link = QComboBox()
        self.w_api_type = QComboBox()
        self.w_api = QLineEdit()

        self.tab_id = tab_id
        self.level = 0
        self.api_data = APIData()

        self.api_json = []
        self.list_folder = []

        self.file_data = MyFile()
        if data is not None:
            try:
                api_data = json.loads(open(data, encoding="utf-8").read())
                self.api_data.construct(api_data)

                self.file_data.setParent(os.path.dirname(data))
                self.file_data.setName(os.path.basename(data))
                self.file_data.setDir(os.path.isdir(data))
                self.file_data.setParentName(os.path.basename(os.path.dirname(data)))

                folder_path = os.path.dirname(data)
                folder_data = MyFile()
                folder_data.setParent(os.path.dirname(folder_path))
                folder_data.setName(os.path.basename(folder_path))
                folder_data.setDir(os.path.isdir(folder_path))
                folder_data.setParentName(os.path.basename(os.path.dirname(folder_path)))

                save = self.api_data.parseSave()
                save.setFolder(folder_data)
                save.setName(os.path.basename(data))
                self.api_data.setSave(save)
            except Exception as ex:
                self.console.emit("Load data 1:", str(ex))
                print(ex)

        self.setOrientation(Qt.Vertical)
        self.component()

        parent.api_data_change.connect(self.load_api)
        parent.tab_action.connect(self.tab_action)
        parent.on_dir_change.connect(self.refresh_dir)

    def component(self):
        self.w_widget_tab.set_json_data(self.api_data.parseConfig().param())
        self.w_widget_tab.error.connect(self.console_push)

        w_run = QPushButton()
        w_run.setIcon(QIcon(get_icon_link('play_arrow.svg')))
        w_run.setText("Run")
        w_run.setToolTip("Run API call (Ctrl+R)")
        w_run.pressed.connect(self.run_api_without_save)

        w_run_save = QPushButton()
        w_run_save.setIcon(QIcon(get_icon_link('play_circle_outline.svg')))
        w_run_save.setText("Run && Save")
        w_run_save.setToolTip("Run and Save API call (Ctrl++Shift+R)")
        w_run_save.pressed.connect(self.run_api_save)

        w_sync = QPushButton()
        w_sync.setText("Sync")
        w_sync.setIcon(QIcon(get_icon_link('refresh.svg')))
        w_sync.setToolTip("Sync param (Ctrl+Shift+C)")
        w_sync.pressed.connect(self.sync_param)

        l_action = QHBoxLayout()
        l_action.addWidget(w_run, alignment=Qt.AlignLeft)
        l_action.addWidget(w_run_save, alignment=Qt.AlignLeft)
        l_action.addStretch()
        l_action.addWidget(w_sync, alignment=Qt.AlignRight)

        w_group2 = QWidget()
        w_group2.setObjectName('Layout')
        w_group2.setLayout(l_action)
        w_group2.setMaximumHeight(50)

        self.addWidget(self.header())
        self.addWidget(self.w_widget_tab)
        self.addWidget(w_group2)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 2)
        self.setStretchFactor(2, 1)
        self.setStretchFactor(3, 1)

    def console_push(self, a, b):
        self.console.emit(a, b)

    def header(self):
        self.w_api.setText(self.api_data.parseConfig().api())

        self.w_api_link.setView(self.get_list_view())

        self.w_api.textChanged.connect(self.api_text_change)
        self.w_api_type.setView(self.get_list_view())
        self.w_api_type.addItem("POST")
        self.w_api_type.addItem("GET")

        if self.api_data.parseConfig().protocol() == 'POST':
            self.w_api_type.setCurrentIndex(0)
        elif self.api_data.parseConfig().protocol() == 'GET':
            self.w_api_type.setCurrentIndex(1)

        self.load_api()

        self.w_api_param.setView(self.get_list_view())
        self.w_api_param.addItem("Param")
        self.w_api_param.addItem("JSON")

        if self.api_data.parseConfig().type() == 'Param':
            self.w_api_param.setCurrentIndex(0)
        elif self.api_data.parseConfig().type() == 'JSON':
            self.w_api_param.setCurrentIndex(1)

        self.folder.setView(self.get_list_view())
        self.refresh_dir()

        self.file_name.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        if self.file_data is not None:
            self.file_name.setText(self.file_data.name())

        save_label = QLabel()
        save_label.setText("Save: ")

        save_box = QHBoxLayout()
        save_box.addWidget(save_label)
        save_box.addWidget(self.folder)

        out_save_box = QVBoxLayout()
        out_save_box.addLayout(label_widget("Save: ", self.folder, 120))
        out_save_box.addWidget(self.file_name)

        self.w_description.setMinimumHeight(50)
        self.w_description.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.w_description.setText(self.api_data.parseSave().description())

        api_layout = QHBoxLayout()
        api_layout.addWidget(self.w_api_type)
        api_layout.addWidget(self.w_api)

        l_box = QVBoxLayout()
        l_box.addLayout(api_layout)
        # l_box.addLayout(label_widget("Protocol: ", self.w_api_type, 120))
        l_box.addLayout(label_widget("API Link: ", self.w_api_link, 120))
        l_box.addLayout(label_widget("Parameter type: ", self.w_api_param, 120))
        l_box.addLayout(out_save_box)
        l_box.addLayout(label_widget("Description: ", self.w_description, 0, 1))

        gr_header = QGroupBox()
        gr_header.setLayout(l_box)
        gr_header.setTitle("API")
        gr_header.setMaximumHeight(300)
        return gr_header

    def refresh_dir(self):
        self.list_folder = []
        file = MyFile()
        file.setParent(get_data_folder())
        file.setName("root")
        file.setDir(True)
        self.list_folder.append(file)
        self.load_folder(get_data_folder())
        self.folder.clear()

        folder = self.api_data.parseSave().parseFolder()
        if folder.name() == 'root':
            for data in self.list_folder:
                name = os.path.join(data.parent(), data.name())
                name = name.replace(get_data_folder(), "")
                if name == os.sep + "root":
                    name = "<root>"
                self.folder.addItem(name, data)
            self.folder.setCurrentIndex(0)
        else:
            index = 0
            count = 0
            for data in self.list_folder:
                name = os.path.join(data.parent(), data.name())
                name = name.replace(get_data_folder(), "")
                if name == os.sep + "root":
                    name = "<root>"
                self.folder.addItem(name, data)
                if folder.parent() == data.parent() and folder.name() == data.name():
                    index = count
                count += 1
            self.folder.setCurrentIndex(index)

    def tab_action(self, tab_id, action, exc=False):
        if tab_id == self.tab_id:
            if action == "run":
                self.run_api_without_save()
            elif action == "run_save":
                self.run_api_save()
            elif action == "sync":
                self.sync_param()
            elif action == "save":
                self.save_data()
        elif tab_id == "all":
            if action == "save":
                self.save_data()

    def sync_param(self):
        self.w_widget_tab.sync()

    def load_api(self):
        self.api_json = []
        d = APILink()
        d.setURL("")
        d.setName("<empty>")
        self.api_json.append(d)
        if os.path.isfile(get_link_file()):
            f = open(get_link_file(), "r", encoding="utf-8")
            data = f.read()
            f.close()

            try:
                api_json = json.loads(data)
                for api in api_json:
                    data = APILink()
                    data.construct(api)
                    self.api_json.append(data)
            except Exception as ex:
                print(ex)
                self.console.emit("Get API Link: ", str(ex))
        self.w_api_link.clear()
        selection = 0
        link = self.api_data.parseConfig().parseLink()
        count = 0
        for data in self.api_json:
            self.w_api_link.addItem(data.name(), data)
            if data.url() == link.url() or (link.name() == "<empty>" and data.name() == "<empty>"):
                selection = count
            count += 1
        self.w_api_link.setCurrentIndex(selection)

    def load_folder(self, parent_dir):
        lst = os.listdir(path=parent_dir)
        for f in lst:
            path = os.path.join(parent_dir, f)
            file = MyFile()
            if os.path.isdir(path):
                file.setParent(parent_dir)
                file.setName(f)
                file.setDir(True)
                self.load_folder(path)
                self.list_folder.append(file)

    def api_text_change(self):
        text = self.w_api.text()
        if (self.file_name.text() in text or text in self.file_name.text()) and abs(
                len(text) - len(self.file_name.text())) <= 1:
            self.file_name.setText(self.w_api.text())
        elif self.file_name.text() == "":
            self.file_name.setText(self.w_api.text())

    def run_api(self, is_save: bool):
        api = self.w_api.text()
        if api != "":
            data = self.get_config(api)
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            response = APIResponse()
            if data.protocol() == "GET":
                response = httprequest.get(data.parseLink().url(), api, data.param())
            elif data.protocol() == "POST":
                if data.type() == 'JSON':
                    response = httprequest.post(data.parseLink().url(), api, data.param())
                elif data.type() == 'Param':
                    response = httprequest.post_param(data.parseLink().url(), api, data.param())
            QApplication.restoreOverrideCursor()
            save = APISave()
            save.setName(self.file_name.text())
            save.setFolder(self.list_folder[self.folder.currentIndex()])
            save.setDescription(self.w_description.toPlainText())

            self.api_data.setConfig(data)
            self.api_data.setResponse(response)
            self.api_data.setSave(save)

            if is_save:
                if self.file_name.text().isspace() or self.file_name.text() == "":
                    self.console.emit("Save API:", "No save name")
                else:
                    self.result.emit(self.api_data, is_save, False)
            else:
                self.result.emit(self.api_data, is_save, False)
        else:
            self.console.emit("Run API:", "No API")

    def save_data(self):
        api = self.w_api.text()
        if api != "":

            data = self.get_config(api)

            self.api_data.setConfig(data)
            save = APISave()
            save.setName(self.file_name.text())
            save.setFolder(self.list_folder[self.folder.currentIndex()])
            save.setDescription(self.w_description.toPlainText())

            self.api_data.setSave(save)

            if self.file_name.text().isspace() or self.file_name.text() == "":
                self.console.emit("Save API:", "No save name")
            else:
                self.result.emit(self.api_data, True, True)
        else:
            self.console.emit("Save API:", "No API")

    def get_config(self, api: str):
        protocol = self.w_api_type.currentText()
        link = self.api_json[self.w_api_link.currentIndex()]
        type_api = self.w_api_param.currentText()
        param = self.w_widget_tab.jsonData

        data = APIConfig()
        data.setAPI(api)
        data.setProtocol(protocol)
        data.setType(type_api)
        data.setLink(link)
        data.setParam(param)
        return data

    def run_api_save(self):
        self.run_api(True)

    def run_api_without_save(self):
        self.run_api(False)
