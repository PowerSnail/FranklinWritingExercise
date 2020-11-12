import platform
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from franklin_writing_exercise.main_window import MainWindow
from franklin_writing_exercise import resources  # SIDE EFFECT


def run():
    app = QApplication(sys.argv)
    app.setApplicationName("franklin-exercise")

    # Icon search path must be set after QApplication, before load icon
    QIcon.setFallbackSearchPaths([*QIcon.fallbackSearchPaths(), ":icons", ":icons/"])
    app.setWindowIcon(QIcon.fromTheme("franklin-exercise"))
    app.setDesktopFileName("franklin-exercise.desktop")

    if platform.system() == "Windows":
        app.setWindowIcon(QIcon(":icons/franklin-exercise.svg"))  # Work-around windows

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    run()
