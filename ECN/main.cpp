#include <QApplication>
#include <QObject>
#include <qtextstream.h>
#include <iostream>
#include <QMessageBox>
#include <QInputDialog>
#include "ecn.h"
#include "tempecn.h"
#include "logindialog.h"

#include <QNetworkAccessManager>

using namespace std;

/*int main(int argc, char *argv[]) {
	QApplication a(argc, argv);
    tempECN *controller = new tempECN;
	QTextStream cout(stdout, QIODevice::WriteOnly);

	/*QNetworkAccessManager *manager = new QNetworkAccessManager();
    QNetworkRequest request;
    QNetworkReply *reply = NULL;

	QSslConfiguration config = QSslConfiguration::defaultConfiguration();
    config.setProtocol(QSsl::TlsV1_2OrLater);
    request.setSslConfiguration(config);
    request.setUrl(QUrl("https://www.broadband.is/api/api.php"));
    request.setHeader(QNetworkRequest::ServerHeader, "application/json");
    manager->get(request);
    QObject::connect(manager, SIGNAL(finished(QNetworkReply*)), controller, SLOT(getISAccounts(QNetworkReply*)));

    qDebug()<<reply->readAll();

	return 0;
}*/

int main(int argc, char *argv[]) {}