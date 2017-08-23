from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit
from connection import CONN

class TableBrowser(QWidget):
    def __init__(self, conn = CONN):
        super(TableBrowser, self).__init__()
        self.CONN = conn
        l = QHBoxLayout()
        self.setLayout(l)

        self.display = QWidget()
        l.addWidget(self.display)
        self.display.setStyleSheet("QWidget {"
                                 "  border:1px solid rgb(0, 0, 0);"
                                 "}")

    def list_table(self, result_set, *fields):
        grid = QHBoxLayout()
        self.display.setLayout(grid)
        for index, field in enumerate(result_set):
            column = QWidget()
            grid.addWidget(column)
            col_layout = QVBoxLayout()
            column.setLayout(col_layout)
            col_layout.addWidget(QLabel(fields[index]))
            for i in range(20):
                col_layout.addWidget(QTextEdit())
            grid.addStretch(1)
        grid.addStretch(1)