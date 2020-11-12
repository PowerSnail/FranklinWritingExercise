from PyQt5.QtGui import QTextBlockFormat, QTextCursor

from PyQt5.QtWidgets import QTextEdit


class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._paragraph_format = QTextBlockFormat()
        self._paragraph_format.setBottomMargin(16)

    def setText(self, value: str):
        old_state = self.blockSignals(True)
        self.setPlainText(value)
        self.blockSignals(old_state)

    def setPlainText(self, text: str):
        super().setPlainText(text)
        self._set_paragraph_format()

    def _set_paragraph_format(self):
        cursor = QTextCursor(self.document())

        while True:
            cursor.beginEditBlock()
            cursor.setBlockFormat(self._paragraph_format)
            cursor.endEditBlock()
            has_next = cursor.movePosition(QTextCursor.NextBlock)
            if not has_next:
                break
