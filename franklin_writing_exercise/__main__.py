import sys

from PyQt5.QtWidgets import QApplication

from franklin_writing_exercise.main_window import MainWindow


def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    run()
