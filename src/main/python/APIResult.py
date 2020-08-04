import json
import os

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QSplitter, QCheckBox, \
    QSizePolicy, QMessageBox, QLineEdit

from src.main.plugin.viewer import JSONApplication
from src.main.python import Application
from src.main.python.ResultFormatManager import ResultFormatManager
from src.main.python.model.APIData import APIData
from src.main.python.model.APIResponse import APIResponse
from src.main.python.modules import httprequest, jsonpretty
from src.main.python.modules.JSONEditor import JSONEditor
from src.main.python.modules.module import get_icon_link, color_json
from src.main.python.modules.module import get_stylesheet


class APIResult(QSplitter):
    save_done = pyqtSignal()
    tab_id = ""

    def __init__(self, parent: Application, tab_id: str, data):
        super().__init__()
        self.w_format_field = QLineEdit()
        self.w_format_label = QCheckBox()
        self.w_result = JSONEditor()
        self.w_console = JSONEditor()
        self.w_status_code = QLabel()
        self.w_url = QLineEdit()
        self.viewer = None

        self.format_manager = None
        self.api_data = APIData()
        self.format_backup = []
        self.tab_id = tab_id

        parent.tab_close.connect(self.handle_close)
        parent.app_close.connect(self.handle_close)
        parent.tab_action.connect(self.tab_action)
        if data is not None:
            api_data = json.loads(open(data, encoding="utf-8").read())
            self.api_data.construct(api_data)
            try:
                api_data = json.loads(open(data, encoding="utf-8").read())
                self.api_data.construct(api_data)
            except Exception as ex:
                self.console("Load data 2:", str(ex))
                print(ex)

        self.setOrientation(Qt.Vertical)
        self.component()

    def handle_close(self, tab_id="app"):
        if tab_id == self.tab_id or tab_id == "app":
            if self.format_manager is not None:
                self.format_manager.destroy()
                self.format_manager = None

    def tab_action(self, tab_id, action, exc=False):
        if tab_id == self.tab_id:
            if action == "format":
                self.format_result()
            elif action == "format_object":
                self.w_format_label.setCheckState(True)
                self.format_result()

    def component(self):
        self.w_url.setText("Url: ")
        self.w_url.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.w_url.setText(self.api_data.parseReponse().url())

        self.w_status_code.setText("0 - No API call")
        self.w_status_code.setText(self.print_status(self.api_data.parseReponse().status()))

        l_status = QHBoxLayout()
        l_status.addWidget(self.w_url)
        l_status.addWidget(self.w_status_code, alignment=Qt.AlignRight)

        self.w_console.setDocument(color_json(self.api_data.parseReponse().header()))

        w_gr_vbox_console = QVBoxLayout()
        w_gr_vbox_console.addLayout(l_status)
        w_gr_vbox_console.addWidget(self.w_console)

        w_gr_console = QGroupBox()
        w_gr_console.setTitle("Console")
        w_gr_console.setLayout(w_gr_vbox_console)

        w_format = QPushButton()
        w_format.setText("Format")
        w_format.setIcon(QIcon(get_icon_link('star.svg')))
        w_format.setToolTip("Format result (Ctrl+B)")
        w_format.pressed.connect(self.format_result)

        w_open_view = QPushButton()
        w_open_view.setIcon(QIcon(get_icon_link('open_in_new.svg')))
        w_open_view.setToolTip("JSON Viewer")
        w_open_view.pressed.connect(self.open_view)

        self.w_format_field.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.set_format_text(self.api_data.parseConfig().format())
        self.format_backup = self.api_data.parseConfig().format()

        self.w_format_field.installEventFilter(self)
        self.w_format_field.setEnabled(False)

        self.w_format_label.setText("String object: ")

        l_hbox = QHBoxLayout()
        l_hbox.addWidget(self.w_format_label, alignment=Qt.AlignLeft)
        l_hbox.addWidget(self.w_format_field)
        l_hbox.addWidget(w_format, alignment=Qt.AlignRight)
        l_hbox.addWidget(w_open_view, alignment=Qt.AlignRight)

        w_gr_vbox_result = QVBoxLayout()
        w_gr_vbox_result.addLayout(l_hbox)

        self.w_result.setDocument(color_json(self.api_data.parseReponse().content()))

        w_gr_vbox_result.addWidget(self.w_result)

        w_gr_result = QGroupBox()
        w_gr_result.setTitle("Result")
        w_gr_result.setLayout(w_gr_vbox_result)

        self.addWidget(w_gr_console)
        self.addWidget(w_gr_result)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 2)

    def console(self, src="", arg=None):
        if arg is not None:
            print(src, arg, sep=": ")
            s = src + ": " + arg + "\n"
            new = color_json(self.w_console.toPlainText() + "\n" + s)
            self.w_console.setDocument(new)

    def result(self, rs: APIData, is_save: bool, is_save_only=True):
        cfg = rs.parseConfig()
        cfg.setFormat(self.format_backup)
        rs.setConfig(cfg)
        if is_save_only:
            res = self.api_data.parseReponse()
            res.setContent(self.w_result.toPlainText())
            rs.setResponse(res)

        self.api_data = rs
        self.format_result()

        status = self.print_status(rs.parseReponse().status())
        self.w_status_code.setText(status)

        self.w_url.setText(rs.parseReponse().url())

        cons = color_json(dict(rs.parseReponse().header()))
        self.w_console.setDocument(cons)

        if is_save:
            if rs.parseReponse().status() >= 400:
                self.show_ask_save_dialog(self.print_status(rs.parseReponse().status()), rs)
            else:
                self.save(rs)

    def open_view(self):
        data = self.w_result.toPlainText()
        if self.viewer is None:
            self.viewer = JSONApplication.run()
            self.viewer.load(data, self.tab_id, self.api_data.parseConfig().api())
            self.viewer.showMaximized()
        else:
            self.viewer.load(data, self.tab_id, self.api_data.parseConfig().api())
            self.viewer.showMaximized()

    def show_ask_save_dialog(self, res: str, rs: APIData):
        msg = QMessageBox()
        msg.setStyleSheet(open(get_stylesheet()).read())
        msg.setIcon(QMessageBox.Warning)

        msg.setText("API call fail!!!")
        msg.setInformativeText(res)
        msg.setWindowTitle("API call fail. Do you want to save this response?")
        msg.addButton('Force save', QMessageBox.YesRole)
        msg.addButton('Save Config', QMessageBox.YesRole)
        msg.addButton('Cancel', QMessageBox.NoRole)

        chosen = msg.exec_()
        if chosen == 0:
            self.save(rs)
        elif chosen == 1:
            rs.setResponse(APIResponse())
            self.save(rs, False)

    def save(self, rs: APIData, is_replace=True):
        path = rs.parseSave().name()
        if not path.lower().endswith(".json"):
            path = path + ".json"
        folder_name = rs.parseSave().parseFolder().name()
        if folder_name == "root":
            path = os.path.join(rs.parseSave().parseFolder().parent(), path)
        else:
            path = os.path.join(rs.parseSave().parseFolder().parent(), folder_name, path)

        if os.path.isfile(path):
            f = open(path, "r", encoding="utf-8")
            js = json.loads(f.read())
            json_object = APIData()
            json_object.construct(js)
            f.close()
            if not is_replace:
                rs.setResponse(json_object.parseReponse())

            api = json_object.parseConfig().api()
            if api != rs.parseConfig().api():
                self.show_dialog(path, rs, rs.parseConfig().api(), json_object.parseConfig().api())
                return -1

        self.save_data(path, rs)

    def show_dialog(self, path, rs, your_api, their_api):
        msg = QMessageBox()
        msg.setStyleSheet(open(get_stylesheet()).read())
        msg.setIcon(QMessageBox.Information)

        msg.setText("The file already exists.")
        msg.setInformativeText(
            "The file already exists and the difference is found in the api section. Are you sure to continue saving?")
        msg.setWindowTitle("Save Warning!!!")
        detail = "Your API: " + your_api + '\n' + "Their API: " + their_api
        msg.setDetailedText(detail)
        msg.addButton('Save', QMessageBox.YesRole)
        msg.addButton('Auto Fix', QMessageBox.YesRole)
        msg.addButton('Cancel', QMessageBox.NoRole)

        retval = msg.exec_()
        if retval == 0:
            self.save_data(path, rs)
        elif retval == 1:
            path = path.replace(".json", "")
            path = path + "_" + your_api + ".json"
            self.save_data(path, rs)

    def save_data(self, path: str, rs: APIData):
        formatted_json = json.dumps(rs.data, sort_keys=True, indent=4)
        fout = open(path, "w", encoding="utf-8")
        fout.write(formatted_json)
        fout.close()
        print("save output to: " + path)
        self.console("save output to", path)
        self.save_done.emit()

    def print_status(self, r: int):
        return httprequest.print_response(r) + ": " + str(r)

    def format_result(self):
        result = self.api_data.parseReponse().content()
        if not self.w_format_label.isChecked():
            self.w_result.setDocument(color_json(result))
        else:
            if not self.format_backup:
                self.w_result.setDocument(color_json(result))
            else:
                if isinstance(result, dict) or isinstance(result, list):
                    self.exe_format_result(result, self.format_backup)
                else:
                    self.w_result.setDocument(color_json(result))

    def exe_format_result(self, rs, ftm: list):
        new = jsonpretty.extract(rs, ftm)
        self.w_result.setDocument(color_json(new))

    def open_format_manager(self):
        name = self.api_data.parseSave().name()
        if name == "":
            name = name + " - Format Result"
        else:
            name = "New Request - Format Result"

        if self.format_manager is not None:
            self.format_manager.destroy()
            self.format_manager = None

        self.format_manager = ResultFormatManager(name, self.format_backup)
        self.format_manager.setModal(False)
        self.format_manager.setGeometry(int(self.x() + self.width() / 2 - 300), int(self.y() + self.height() / 2 - 200),
                                        520, 360)
        self.format_manager.apply_done.connect(self.format_manager_done)
        self.format_manager.apply_cancel.connect(self.format_manager_cancel)
        self.format_manager.setVisible(True)
        self.format_manager.show()

    def format_manager_done(self, data: list):
        self.format_backup = data.copy()
        self.set_format_text(data)
        self.format_manager = None

    def set_format_text(self, data: list):
        s = ""
        for d in data:
            s += "," + d
        if len(s) > 1:
            s = s[1:]
        self.w_format_field.setText(s)

    def format_manager_cancel(self):
        self.format_manager = None

    def eventFilter(self, widget, event):
        if widget == self.w_format_field and event.type() == QEvent.MouseButtonPress:
            self.open_format_manager()
            return True
        return False
