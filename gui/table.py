from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from meta import CONN


class Table(QTableWidget):
    def __init__(self):
        super(Table, self).__init__()

        headers = 'code', 'first_name', 'last_name', 'company', 'vat', 'physical_address', 'postal_address'
        entities = CONN.stmt() \
            ('SELECT')(*headers) \
            ('FROM')('entity')()

        self.setColumnCount(len(headers) - 1)
        self.setRowCount(len(entities))

        self.setHorizontalHeaderLabels(headers[1:])
        self.setVerticalHeaderLabels([entity[headers[0]] for entity in entities])

        for i, entity in enumerate(entities):
            for j, cell in enumerate(headers[1:]):
                self.setItem(i, j, QTableWidgetItem(entity[cell]))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
