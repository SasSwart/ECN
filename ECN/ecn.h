#ifndef ECN_H
#define ECN_H

#include <QObject>
#include <QSqlDatabase>
#include <QList>
#include <QNetworkReply>

class ECN : public QObject
{
	Q_OBJECT
public:
	explicit ECN(QObject *parent = 0);
	~ECN();
	QSqlDatabase *connectToDB(QString driver, QString host, QString user, QString password);
private:
protected:
    void loadLogin();
    void setupCDB();
    QSqlDatabase* db;
    QString rootPassword;
    QString host;
    QString name;
    QString password;
    QList<QString> *errors;
signals:

public slots:
    void rootLogin(QString& username, QString& password);
    void getISAccounts(QNetworkReply* finished);
};

#endif // ECN_H
