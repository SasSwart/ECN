from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class Table(QTableWidget):
    def __init__(self):
        super(Table, self).__init__()

    def populate(self, vertical_headers, result_set):
        self.setColumnCount(len(vertical_headers) - 1)
        self.setRowCount(len(result_set))

        self.setHorizontalHeaderLabels(vertical_headers[1:])
        self.setVerticalHeaderLabels([str(entity[vertical_headers[0]]) for entity in result_set])

        for i, entity in enumerate(result_set):
            for j, cell in enumerate(vertical_headers[1:]):
                self.setItem(i, j, QTableWidgetItem(str(entity[cell])))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
