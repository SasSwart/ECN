from PyQt5.QtWidgets import QMainWindow, QWidget, QTabWidget, QAction, QTextEdit

class TextDocumentTab(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('QTextEdit {'
                           '     font: 10pt "Consolas";'
                           '}')

class ViewDialogTab(QWidget):
    def __init__(self):
        super().__init__()
        


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

        # self.showMaximized()

    def addTab(self, title, doc):
        self.tabs.append(doc)
        self.tabBar.addTab(self.tabs[-1], title)

    def removeTab(self, index):
        self.tabBar.removeTab(index)