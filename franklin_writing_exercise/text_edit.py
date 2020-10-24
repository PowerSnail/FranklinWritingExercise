from PyQt5.QtWidgets import QPlainTextEdit


class TextEdit(QPlainTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
    
    def setText(self, value: str):
        old_state = self.blockSignals(True)
        self.setPlainText(value)
        self.blockSignals(old_state)