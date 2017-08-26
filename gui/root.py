from PyQt5.QtWidgets import QMainWindow

from gui.table import Table


class Root(QMainWindow):
    def __init__(self):
        super(Root, self).__init__()
        self.setCentralWidget(Table())
