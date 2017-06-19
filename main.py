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


