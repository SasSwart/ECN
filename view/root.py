from PyQt5.QtWidgets import QMainWindow

from meta import CONN
from view.table import Table


class Root(QMainWindow):
    def __init__(self):
        super(Root, self).__init__()

        # headers = 'code', 'first_name', 'last_name', 'company', 'vat', 'physical_address', 'postal_address'
        # entities = CONN.stmt() \
        #     ('SELECT')(*headers) \
        #     ('FROM')('entity')()
        # table.populate(headers, entities)

    def manage(self, table_name, *headers):
        table = Table()
        entities = CONN.stmt() \
            ('SELECT')(*headers) \
            ('FROM')(table_name)()
        table.populate(headers, entities)
        self.setCentralWidget(table)

    def manage_entities(self):
        table_name = 'entity'
        headers = 'code', 'first_name', 'last_name', 'company', 'vat', 'physical_address', 'postal_address'
        self.manage(table_name, *headers)

    def manage_services(self):
        table_name = 'service'
        headers = 'code', 'description', 'cost_price', 'sales_price', 'supplier', 'type'
        self.manage(table_name, *headers)

    def manage_subscriptions(self):
        table_name = 'subscription'
        headers = 'code', 'client', 'service', 'description', 'qty'
        self.manage(table_name, *headers)
