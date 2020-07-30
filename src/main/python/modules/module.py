import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QSizePolicy, QGridLayout, QLabel
from pygments import *
from pygments import lexers, formatters

from src.main.dir import current_dir

list_ = []


def get_relative(relative_path=None):
    main = current_dir()
    if relative_path is not None:
        return os.path.join(main, relative_path)
        # return relative_path
    else:
        return main
        # return ""


def get_icon_link(icon_name):
    return get_relative("icons/dark/") + icon_name


def get_icon_base(icon_name):
    return get_relative("icons/") + icon_name


def label_widget(text, widget, label_size=0, type_label=0):
    box = QGridLayout()
    label = QLabel()
    label.setText(text)
    if label_size != 0:
        label.setMinimumWidth(label_size)
        label.setMaximumWidth(label_size)

    label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
    widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

    if type_label == 0:
        box.addWidget(label, 0, 0, alignment=Qt.AlignLeft)
        box.addWidget(widget, 0, 1)
    else:
        box.addWidget(label, 0, 0, alignment=Qt.AlignLeft)
        box.addWidget(widget, 1, 0)
    return box


def get_user_folder():
    return os.path.expanduser('~')


def get_app_folder():
    data = get_user_folder() + "\\HttpRequest"

    if not os.path.exists(data):
        os.makedirs(data)

    return data


def get_data_folder():
    data = get_app_folder() + "\\data"

    if not os.path.exists(data):
        os.makedirs(data)

    return data


def get_config_folder():
    data = get_app_folder() + "\\config"

    if not os.path.exists(data):
        os.makedirs(data)

    return data


def get_last_open_file():
    data = get_config_folder() + "\\last_open.json"
    return data


def get_link_file():
    data = get_config_folder() + "\\api_link.json"
    return data


def get_stylesheet():
    return get_relative("stylesheet/xu_themes/xu_dark.css")


def color_json(obj):
    doc = QTextDocument()
    doc.setDefaultStyleSheet(open(get_relative('stylesheet/json_style.css')).read())

    if isinstance(obj, str):
        doc.setHtml(string_to_html(obj))
    else:
        doc.setHtml(json_to_html(obj))
    return doc


def json_to_html(obj):
    formatted_json = json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.HtmlFormatter())
    return colorful_json


def string_to_html(obj):
    formatted_json = obj
    try:
        js = json.loads(obj)
        formatted_json = json.dumps(js, sort_keys=True, indent=4, ensure_ascii=False)
    except Exception as ex:
        print(ex)
    finally:
        colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.HtmlFormatter())
        return colorful_json


def get_list_dir(path, remove):
    global list_
    lst = os.listdir(get_data_folder())
    for f in lst:
        if os.path.isdir(path + "\\" + f):
            save = path + "\\" + f
            save.replace(remove, "")
            list_.append(save)
            get_list_dir(path + "\\" + f, remove)


def get_list_folder(path, remove):
    sub = [x[0] for x in os.walk(path)]
    list_ = []
    for s in sub:
        new = s.replace(remove, "")
        if new != "":
            list_.append(new)
        else:
            list_.append("root")
    return list_
