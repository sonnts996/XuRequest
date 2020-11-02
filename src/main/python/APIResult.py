from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox, QSplitter, QMessageBox, QLineEdit

from src.main.python import Application
from src.main.python.json_viewer import JSONApplication
from src.main.python.json_viewer.JSONEditor import JSONEditor
from src.main.python.model.APIData import APIData
from src.main.python.model.APIResponse import APIResponse
from src.main.python.modules.module import *
from src.main.python.request import httprequest


class APIResult(QSplitter):
    save_done = pyqtSignal()
    tab_id = ""

    def __init__(self, parent: Application, tab_id: str, data):
        super().__init__()
        self.new_result = JSONApplication.JSONApplication(1)
        self.w_console = JSONEditor()
        self.w_status_code = QLabel()
        self.w_url = QLineEdit()
        self.viewer = None

        self.api_data = APIData()
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
            self.new_result.close()

    def tab_action(self, tab_id, action, exc=False):
        if tab_id == self.tab_id:
            if action == "format":
                self.new_result.sync_api()
            elif action == "format_object":
                self.new_result.format_api()

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

        self.new_result.load(self.api_data.parseReponse().content())

        w_gr_result = QGroupBox()
        w_gr_result.setTitle("result")
        w_gr_result.setLayout(QVBoxLayout())
        w_gr_result.layout().addWidget(self.new_result)

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
        if is_save_only:
            res = self.api_data.parseReponse()
            res.setContent(self.new_result.current_viewer().text())
            rs.setResponse(res)

        self.api_data = rs
        self.new_result.load(rs.parseReponse().content())

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
        try:
            formatted_json = json.dumps(rs.data, sort_keys=True, indent=4)
            fout = open(path, "w", encoding="utf-8")
            fout.write(formatted_json)
            fout.close()
            print("save output to: " + path)
            self.console("save output to", path)
            self.save_done.emit()
        except Exception as ex:
            msg = QMessageBox()
            msg.setStyleSheet(open(get_stylesheet()).read())
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Save file Error.")
            msg.setInformativeText("Something error when save file!")
            msg.setWindowTitle("Save Error!!!")
            detail = str(ex)
            msg.setDetailedText(detail)
            msg.addButton('Cancel', QMessageBox.NoRole)
            msg.exec_()


    def print_status(self, r: int):
        return httprequest.print_response(r) + ": " + str(r)
