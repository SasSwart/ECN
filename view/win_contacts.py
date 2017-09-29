import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel


class Contacts(QWidget):
    def __init__(self):
        super(Contacts, self).__init__()

        level1 = QVBoxLayout()
        self.setLayout(level1)

        header = QWidget()
        level1.addWidget(header)
        level2 = QGridLayout()
        header.setLayout(level2)
        name = QLabel('Name:')
        tel = QLabel('Tel:')
        cell = QLabel('Cell:')
        level2.addWidget(name, 0, 0)
        level2.addWidget(tel, 0, 1)
        level2.addWidget(cell, 0, 2)
        company = QLabel('Company:')
        email = QLabel('Email:')
        level2.addWidget(company, 1, 0)
        level2.addWidget(email, 1, 2)

        addresses = QWidget()
        level1.addWidget(addresses)
        level2 = QHBoxLayout()
        addresses.setLayout(level2)

        footer = QWidget()
        level1.addWidget(footer)
        level2 = QHBoxLayout()
        footer.setLayout(level2)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Contacts()
    main.showMaximized()
    sys.exit(app.exec())
