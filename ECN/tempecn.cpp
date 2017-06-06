#include "tempecn.h"
#include "logindialog.h"
#include "QMessageBox"
#include "QNetworkReply"

tempECN::tempECN(QObject *parent)  : ECN(parent) {
	LoginDialog* loginDialog = new LoginDialog();
	QString l = "SQL Host";
	loginDialog->setUserLabel(l);
	l = "Root Password";
	loginDialog->setPasswordLabel(l);

	QObject::connect(
		loginDialog,
		SIGNAL (acceptLogin(QString&,QString&,int&)),
		this,
		SLOT (rootLogin(QString&,QString&))
	);
	loginDialog->exec();
    db = ECN::connectToDB("QMYSQL", host, name, password);
}


