import os.path
from getpass import getpass, getuser
import mysql.connector


def connect(user, password, host):
    # Connect to local Database
        conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
        )
        cur = conn.cursor()
        return conn, cur, None


class ECN:
    def __init__(self):
        self.user, self.password, self.host, self.database = None, None, None, None
        self.conn = None
        self.cur = None
        self.error = None

        # Detect ECN Login Details
        if os.path.isfile("login.dat"):
            self.user, self.password, self.host, self.database = open("login.dat").readline().split(',')
            self.connect()
        else:
            self.error = "-1: login.dat not found"

    def setup(self, host, password):
        # Connect to local Database
        self.user = 'root'
        self.password = password
        self.host = host
        self.connect()

    def connect(self):
        self.conn, self.cur, self.error = connect(self.user, self.password, self.host)

    def new_company(self, root, user, password, database, host='127.0.0.1'):
        conn, cur = self.connect('root', root, host)

        cur.execute("SHOW DATABASES;")
        row = cur.fetchone()
        while row is not None:
            if row[0] == database:
                input(database + "")
            row = cur.fetchone()

        cur.execute("SOURCE " + os.getcwd() + "/sql/new.sql;")

        row = cur.fetchone()

        while row is not None:
            print(row)
            row = cur.fetchone()

        cur.close()
        conn.close()


def main():
    ecn = ECN()
    if ecn.error is not None:
        if int(ecn.error.split(":")[0]) == -1:
            # login data missing. Get MySQL details and initialise Database
            print("We can't find the usual details. Is this the first time you're running ECN?")
            print("Let's get everything setup")
            host = input("What is your MySQL hostname or IP?")
            print(host)
            password = input("What is your root mySQL password?")
            ecn.setup(host, password)
            if ecn.error is None:
                ecn.cur.execute("SHOW DATABASES;")
    if ecn.error is not None:
        print("We were unable to fix the problem. Please give the following message to your System Administrator:")
        print(ecn.error)


if __name__ == "__main__":
    host = "sql0"
    user = "root"
    passw = "Hunt!ngSpr!ngbuck123"

    con, cur, error = connect(user, passw, host)

    cur.execute(
        "SELECT \
	        ecn.client.code,\
            ecn.client.first_name, \
	        ecn.client.last_name, \
            ecn.client.company,\
            SUM(ecn.service.sales_price)\
        FROM ecn.client, ecn.subscription, ecn.service \
        WHERE ecn.client.code = ecn.subscription.client \
        AND ecn.subscription.service = ecn.service.code\
        GROUP BY ecn.client.code;")
    reconHeader = cur.column_names
    recon = cur.fetchall()

    cur.execute(
        "SELECT \
            service.supplier,\
            service.description,\
            cost_price,\
            sales_price,\
            first_name, \
            last_name,\
            company,\
            client.code\
        FROM ecn.client, ecn.subscription, ecn.service \
        where ecn.client.code = ecn.subscription.client \
        and ecn.subscription.service = ecn.service.code;")
    subsHeader = cur.column_names
    subs = cur.fetchall()

    report = "Axxess Reconciliation\n"
    report += " {:^30} {:^10} {:^10} {:^10} {:^30} \n".format("Description", "Cost", "Sales", "D/O Total", "Client")
    report += "-"*105 + "\n"

    total_cost = 0
    total_sales = 0
    for sub in subs:
        if sub[0] == "axx001":
            total_cost += sub[2]
            name = ""
            if sub[6] is None:
                name = (sub[4] if sub[4] is not None else "") + " " + (sub[5] if sub[5] is not None else "")
            else:
                name = sub[6]
            for client in recon:
                dototal = 0
                if client[0] == sub[-1]:
                    dototal = client[4]
                    break
            report += "|{:<30}|{:>10}|{:>10}|{:>10}|{:>30}|\n".format(str(sub[1]), str(sub[2]), str(sub[3]), str(dototal), name)
    report += "-"*105 + "\n"
    report += " {:<30} {:>10} \n".format("Total Cost (VAT Ex)", str(total_cost))

    print(report)


