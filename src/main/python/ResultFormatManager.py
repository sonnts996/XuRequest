from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QDialog, QTableView, QPushButton, QHBoxLayout, QVBoxLayout, QWidget

from src.main.python.modules.module import get_stylesheet, get_icon_base


class ResultFormatManager(QDialog):
    apply_done = pyqtSignal(list)
    apply_cancel = pyqtSignal()

    def __init__(self, name: str, data: list):
        super().__init__()
        self.setStyleSheet(open(get_stylesheet()).read())
        self.setWindowTitle(name)
        self.setWindowIcon(QIcon(get_icon_base("main_window_icon.png")))
        # self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setAttribute(Qt.WA_QuitOnClose)
        self.data_json = data
        self.data_json.append("")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Object name'])
        self.model.itemChanged.connect(self.data_change)
        self.table.setModel(self.model)
        self.table.verticalHeader().hide()
        self.table.setAlternatingRowColors(True)
        self.import_data(self.data_json)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        apply = QPushButton()
        apply.setText("Apply")
        apply.pressed.connect(self.apply)
        cancel = QPushButton()
        cancel.setText("Cancel")
        cancel.pressed.connect(self.cancel)

        bar = QHBoxLayout()
        bar.addStretch()
        bar.addWidget(cancel, alignment=Qt.AlignRight)
        bar.addWidget(apply, alignment=Qt.AlignRight)
        bar.setContentsMargins(0, 4, 4, 4)

        widget = QWidget()
        widget.setObjectName("Layout")
        widget.setLayout(bar)

        layout.addWidget(self.table)
        layout.addWidget(widget)

        self.layout().setContentsMargins(4, 4, 4, 4)

    def import_data(self, data_list):
        row = self.model.invisibleRootItem()
        for data in data_list:
            item1 = QStandardItem()
            item1.setText(data)
            item1.setData(data)
            item1.setEditable(True)
            row.appendRow(item1)

    def cancel(self):
        self.apply_cancel.emit()
        self.destroy()

    def data_change(self, arg: QStandardItem):
        data = arg.data()
        text = arg.text()

        if text != "":
            index = self.data_json.index(data)
            self.data_json.insert(index, text)
        if (data != "" and text != "") or text == "":
            self.data_json.remove(data)

        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Object name'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.import_data(self.data_json)

    def apply(self):
        for a in self.data_json:
            if a == "":
                del a

        self.apply_done.emit(self.data_json)
        self.destroy()
