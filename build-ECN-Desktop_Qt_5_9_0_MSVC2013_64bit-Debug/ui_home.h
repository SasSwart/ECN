/********************************************************************************
** Form generated from reading UI file 'home.ui'
**
** Created by: Qt User Interface Compiler version 5.9.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_HOME_H
#define UI_HOME_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_Home
{
public:
    QMenuBar *menuBar;
    QToolBar *mainToolBar;
    QWidget *centralWidget;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *Home)
    {
        if (Home->objectName().isEmpty())
            Home->setObjectName(QStringLiteral("Home"));
        Home->resize(400, 300);
        menuBar = new QMenuBar(Home);
        menuBar->setObjectName(QStringLiteral("menuBar"));
        Home->setMenuBar(menuBar);
        mainToolBar = new QToolBar(Home);
        mainToolBar->setObjectName(QStringLiteral("mainToolBar"));
        Home->addToolBar(mainToolBar);
        centralWidget = new QWidget(Home);
        centralWidget->setObjectName(QStringLiteral("centralWidget"));
        Home->setCentralWidget(centralWidget);
        statusBar = new QStatusBar(Home);
        statusBar->setObjectName(QStringLiteral("statusBar"));
        Home->setStatusBar(statusBar);

        retranslateUi(Home);

        QMetaObject::connectSlotsByName(Home);
    } // setupUi

    void retranslateUi(QMainWindow *Home)
    {
        Home->setWindowTitle(QApplication::translate("Home", "Home", Q_NULLPTR));
    } // retranslateUi

};

namespace Ui {
    class Home: public Ui_Home {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_HOME_H
