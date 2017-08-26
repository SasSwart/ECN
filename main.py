import sys

from PyQt5.QtWidgets import QApplication

from view.root import Root

# class TextDocumentTab(QTextEdit):
#     def __init__(self, text="No Text Body Provided"):
#         super().__init__()
#         self.setText(text)
#         self.setStyleSheet('QTextEdit {'
#                            '     font: 10pt "Consolas";'
#                            '}')
#
#
# class ViewTab(QWidget):
#     def __init__(self):
#         super(ViewTab, self).__init__()
#
#         self.setup = QWidget()
#         setup_layout = QVBoxLayout()
#         self.setup.setLayout(setup_layout)
#
#         config_panel = QWidget()
#         grid = QGridLayout()
#         config_panel.setLayout(grid)
#         setup_layout.addWidget(config_panel)
#
#         document_type = QComboBox()
#         document_type.addItem('Tax Invoice')
#
#         from_date = QDateEdit()
#         from_date.setDisplayFormat(QDATE_FORMAT)
#         today = QDate.currentDate()
#         start_date = QDate(today).addDays(-today.day() + 1)
#         from_date.setDate(today)
#
#         to_date = QDateEdit()
#         to_date.setDisplayFormat(QDATE_FORMAT)
#         to_date.setDate(start_date)
#
#         clients = QLineEdit()
#
#         docs = QLineEdit()
#
#         submit = QPushButton()
#         submit.setText("View")
#
#         grid.addWidget(QLabel("Document:"), 0, 0)
#         grid.addWidget(document_type, 0, 1)
#         grid.addWidget(QLabel("From:"), 1, 0)
#         grid.addWidget(from_date, 1, 1)
#         grid.addWidget(QLabel("To:"), 2, 0)
#         grid.addWidget(to_date, 2, 1)
#         grid.addWidget(QLabel("Clients:"), 3, 0)
#         grid.addWidget(clients, 3, 1)
#         grid.addWidget(QLabel("Document Nrs:"), 4, 0)
#         grid.addWidget(docs, 4, 1)
#         grid.addWidget(submit, 5, 0, 1, 2)
#
#         self.body = QWidget()
#
#         self.view_tab_layout = QHBoxLayout()
#         self.setLayout(self.view_tab_layout)
#         self.view_tab_layout.addWidget(self.setup)
#         self.view_tab_layout.addWidget(self.body, 1)
#
#         setup_layout.addWidget(QTextEdit(), 1)
#
#     def set_body(self, body, stretch):
#         self.view_tab_layout.removeWidget(self.body)
#         self.body.setParent(None)
#         self.body = body
#         self.view_tab_layout.addWidget(self.body, stretch)
#
#
#
#
# class Main(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#         self.tabs = []
#
#     def initUI(self):
#         self.setWindowTitle('Panacea')
#
#         saveAsAction = QAction('&Save as', self)
#         saveAsAction.setStatusTip('Save the currently active document to a file')
#         saveAsAction.setShortcut('Ctrl+s')
#         subscriptionReportAction = QAction('&Subscriptions', self)
#         subscriptionReportAction.setStatusTip('View the subscription resale report')
#         subscriptionReportAction.triggered.connect(quit)
#
#         menu = self.menuBar()
#         fileMenu = menu.addMenu('&File')
#         fileMenu.addAction(saveAsAction)
#         viewMenu = menu.addMenu('&View')
#         viewMenu.addAction(subscriptionReportAction)
#
#         self.tabBar = QTabWidget()
#         self.setCentralWidget(self.tabBar)
#
#     def addTab(self, title, doc):
#         self.tabs.append(doc)
#         self.tabBar.addTab(self.tabs[-1], title)
#
#     def removeTab(self, index):
#         self.tabBar.removeTab(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Root()
    main.manage_subscriptions()
    main.showMaximized()
    sys.exit(app.exec())
