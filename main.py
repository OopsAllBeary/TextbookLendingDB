import sys

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

from db import init_database

if __name__ == "__main__":

    init_database()

    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()