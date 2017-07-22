import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QAction, QTextEdit
from meta import client_invoice


class TextDocumentTab(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('QTextEdit {'
                           '     font: 10pt "Consolas";'
                           '}')


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.tabs = []

    def initUI(self):
        self.setWindowTitle('Panacea')

        saveAsAction = QAction('&Save as', self)
        saveAsAction.setStatusTip('Save the currently active document to a file')
        saveAsAction.setShortcut('Ctrl+s')
        subscriptionReportAction = QAction('&Subscriptions', self)
        subscriptionReportAction.setStatusTip('View the subscription resale report')
        subscriptionReportAction.triggered.connect(quit)

        menu = self.menuBar()
        fileMenu = menu.addMenu('&File')
        fileMenu.addAction(saveAsAction)
        viewMenu = menu.addMenu('&View')
        viewMenu.addAction(subscriptionReportAction)

        self.tabBar = QTabWidget()
        self.setCentralWidget(self.tabBar)

        self.showMaximized()

    def addDocumentTab(self, title, text):
        doc = TextDocumentTab()
        self.tabs.append(doc)
        self.tabs[-1].setText(text)
        self.tabBar.addTab(self.tabs[-1], title)

    def removeTab(self, index):
        self.tabBar.removeTab(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Main()
    invoice = client_invoice('gbg001', 'ecn001')
    main.addDocumentTab('Tax Invoice', invoice[0])
    sys.exit(app.exec())
