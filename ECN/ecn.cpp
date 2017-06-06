#include "ecn.h"
#include "logindialog.h"
#include <QFile>
#include <QMessageBox>
#include <QInputDialog>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QString>
#include <QStringList>

ECN::ECN(QObject *parent) : QObject(parent) {
	this->errors = new QList<QString>();
	//loadLogin();
}

ECN::~ECN() {
	delete this->errors;
	this->errors = 0;
}

void ECN::rootLogin(QString &hostP, QString &password) {
	this->host = hostP;
	this->rootPassword = password;
}

void ECN::loadLogin() {
	QFile file("./login.dat");
	if (file.exists()) {
		if(!file.open(QIODevice::ReadOnly)) {
			QMessageBox::information(0, "error", file.errorString());
		}
	} else {
		QMessageBox::information(0, "Setup", "We could not find the MySQL Login details. Please help us with the following details");

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
		db = connectToDB(rootPassword, "QMYSQL", "localhost", "root");
		QSqlQuery dbs("SHOW DATABASES WHERE (lower(`Database`) LIKE 'ecnc%');");
		QSqlQuery users("SELECT `user` FROM mysql.`user` WHERE (lower(`user`) LIKE 'ecnc%'");
		QList<QString> dbList;
		QList<QString> userList;
		while (dbs.next()) {
			dbList.append(dbs.value(0).toString());
		}
		while (users.next()) {
			userList.append(users.value(0).toString());
		}
		if (dbList.length() == 0) {
			setupCDB();
		}
	}

	QTextStream in(&file);

	while(!in.atEnd()) {
		QString line = in.readLine();
		//Magic here
	}
	file.close();
}

void ECN::setupCDB() {
	//Create non-user general user
	//Store credentials in file

}

QSqlDatabase *ECN::connectToDB(QString driver, QString host, QString user, QString password) {
    QSqlDatabase * ndb = &QSqlDatabase::addDatabase(driver);
    ndb->setHostName(host);
    ndb->setUserName(user);
    ndb->setPassword(password);
    if (ndb->open()) return ndb;
	else {
		return 0;
	}
}

void ECN::getISAccounts(QNetworkReply *finished) {
    QMessageBox::information(0, "Finished", finished->readAll());
}
