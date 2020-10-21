from PyQt5.QtWidgets import QMainWindow
from . import ui_main_window


class MainWindow(QMainWindow, ui_main_window.Ui_MainWindow):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    
        