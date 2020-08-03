from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter

from src.main.python import Application
from src.main.python.APIConfigure import APIConfigure
from src.main.python.APIResult import APIResult
from src.main.python.model.APIData import APIData


class WorkSpaceTab(QSplitter):

    def __init__(self, parent: Application, tab_id: str, data_path):
        super().__init__()

        self.p = parent
        self.setOrientation(Qt.Horizontal)

        self.result = APIResult(parent, tab_id, data_path)

        configure = APIConfigure(parent, tab_id, data_path)
        configure.console.connect(self.console)
        configure.result.connect(self.result_api)

        self.addWidget(configure)
        self.addWidget(self.result)

        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 2)
        self.setContentsMargins(6, 6, 6, 6)

    def console(self, src="tab", arg=None):
        self.result.console(src, arg)

    def result_api(self, rs: APIData, is_save: bool, is_save_only=False):
        self.result.result(rs, is_save, is_save_only)
        if is_save:
            self.p.change_tab_name(rs.parseSave().name())
        else:
            self.p.change_tab_name(rs.parseConfig().api())
