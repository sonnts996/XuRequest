from PyQt5.QtCore import Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QFontMetrics, QTextCursor
from PyQt5.QtWidgets import QTextEdit, QWidget

from src.main.python.modules.module import color_json


class JSONEditor(QTextEdit):
    def __init__(self):
        super().__init__()

        self.config_tab_width()
        self.installEventFilter(self)

    def config_tab_width(self):
        tab_stop = 2
        metrics = QFontMetrics(self.font())
        self.setTabStopWidth(tab_stop * metrics.width(' '))

    def eventFilter(self, widget, event):
        if event.type() == QEvent.KeyPress and widget is self:
            key = event.key()
            if key == Qt.Key_Enter or key == Qt.Key_Return:
                cursor = self.textCursor()
                text = self.toPlainText()
                position = cursor.position()
                text_before = text[:position]
                html_before = color_json(text_before).toHtml()
                text_after = text[position:]
                html_after = color_json(text_after).toHtml()
                self.setText("")
                cursor.insertHtml(html_before)
                position = cursor.position()
                cursor.insertHtml(html_after)
                cursor.setPosition(position)
                cursor.insertText("\n")
                self.setTextCursor(cursor)
                return True
            elif key == Qt.Key_BracketLeft:
                cursor = self.textCursor()
                cursor.insertText("[]")
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                self.setTextCursor(cursor)
                return True
            elif key == Qt.Key_BraceLeft:
                cursor = self.textCursor()
                cursor.insertText("{}")
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                self.setTextCursor(cursor)
                return True
            elif key == Qt.Key_Apostrophe:
                cursor = self.textCursor()
                cursor.insertText("''")
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                self.setTextCursor(cursor)
                return True
            elif key == Qt.Key_QuoteDbl:
                cursor = self.textCursor()
                cursor.insertText("\"\"")
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                self.setTextCursor(cursor)
                return True

        return QWidget.eventFilter(self, widget, event)
