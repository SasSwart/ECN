import mysql.connector

host = "sql0"
user = "root"
passw = "Hunt!ngSpr!ngbuck123"


def connect(user, password, host):
    # Connect to local Database
        conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
        )
        cur = conn.cursor()
        return conn, cur, None

con, cur, error = connect(user, passw, host)

cur.execute(
    "SELECT \
        service.description,\
        cost_price,\
        sales_price,\
        subscription.qty,\
        first_name, \
        last_name,\
        company,\
        client.code,\
        subscription.service,\
        service.supplier,\
        service.type\
    FROM ecn.client, ecn.subscription, ecn.service, ecn.service_type \
    where ecn.client.code = ecn.subscription.client \
    and ecn.service.type = ecn.service_type.type \
    and ecn.subscription.service = ecn.service.code;")

subsHeader = cur.column_names
subs = cur.fetchall()

def is_Domain():
    report = "IS Domain Reconciliation\n"
    report += " {:^30} {:^3} {:^10} {:^10} {:^30} \n".format("Description", "Qty", "Cost", "Sales", "Client")
    hl = "-"*89 + "\n"
    report += hl

    total_cost = 0
    total_sales = 0
    total_qty = 0
    for sub in subs:
        if (sub[-1] == 'domain')\
        and sub[-2] == 'is0001':
            total_cost += (sub[1] if sub[1] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_sales += (sub[2] if sub[2] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_qty += (sub[3] if sub[3] is not None else 0)
            if sub[6] is None:
                name = (sub[4] if sub[4] is not None else "") + " " + (sub[5] if sub[5] is not None else "")
            else:
                name = sub[6]
            report += "|{:<30}|{:^3}|{:>10}|{:>10}|{:>30}|\n".format(str(sub[0]), str(sub[3]), str(sub[1] * sub[3]), str(sub[2] * sub[3]), name)
    report += hl
    report += " {:<30} {:^3} {:>10} {:>10}\n".format("Total", str(total_qty), str(total_cost), str(total_sales))

    print(report)


def is_Mobile():
    report = "IS Mobile Reconciliation\n"
    report += " {:^30} {:^3} {:^10} {:^10} {:^30} \n".format("Description", "Qty", "Cost", "Sales", "Client")
    hl = "-"*89 + "\n"
    report += hl

    total_cost = 0
    total_sales = 0
    total_qty = 0
    for sub in subs:
        if (sub[-1] == 'mobile')\
        and sub[-2] == 'is0001':
            total_cost += (sub[1] if sub[1] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_sales += (sub[2] if sub[2] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_qty += (sub[3] if sub[3] is not None else 0)
            if sub[6] is None:
                name = (sub[4] if sub[4] is not None else "") + " " + (sub[5] if sub[5] is not None else "")
            else:
                name = sub[6]
            report += "|{:<30}|{:^3}|{:>10}|{:>10}|{:>30}|\n".format(str(sub[0]), str(sub[3]), str(sub[1] * sub[3]), str(sub[2] * sub[3]), name)
    report += hl
    report += " {:<30} {:^3} {:>10} {:>10}\n".format("Total", str(total_qty), str(total_cost), str(total_sales))

    print(report)


def is_ADSL():
    report = "IS Per Account Reconciliation\n"
    report += " {:^30} {:^3} {:^10} {:^10} {:^30} \n".format("Description", "Qty", "Cost", "Sales", "Client")
    hl = "-"*89 + "\n"
    report += hl

    total_cost = 0
    total_sales = 0
    total_qty = 0
    for sub in subs:
        if (sub[-1] == 'peracc' or sub[-1] == 'uncapped')\
        and sub[-2] == 'is0001':
            total_cost += (sub[1] if sub[1] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_sales += (sub[2] if sub[2] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_qty += (sub[3] if sub[3] is not None else 0)
            if sub[6] is None:
                name = (sub[4] if sub[4] is not None else "") + " " + (sub[5] if sub[5] is not None else "")
            else:
                name = sub[6]
            report += "|{:<30}|{:^3}|{:>10}|{:>10}|{:>30}|\n".format(str(sub[0]), str(sub[3]), str(sub[1] * sub[3]), str(sub[2] * sub[3]), name)
    report += hl
    report += " {:<30} {:^3} {:>10} {:>10}\n".format("Total", str(total_qty), str(total_cost), str(total_sales))

    print(report)

    report = "IS Per GB Reconciliation\n"
    report += " {:^30} {:^3} {:^10} {:^10} {:^30} \n".format("Description", "Qty", "Cost", "Sales", "Client")
    hl = "-" * 89 + "\n"
    report += hl

    total_cost = 0
    total_sales = 0
    total_qty = 0
    for sub in subs:
        if (sub[-1] == 'pergb') \
                and sub[-2] == 'is0001':
            total_cost += (sub[1] if sub[1] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_sales += (sub[2] if sub[2] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_qty += (sub[3] if sub[3] is not None else 0)
            name = ""
            if sub[6] is None:
                name = (sub[4] if sub[4] is not None else "") + " " + (sub[5] if sub[5] is not None else "")
            else:
                name = sub[6]
            report += "|{:<30}|{:^3}|{:>10}|{:>10}|{:>30}|\n".format(str(sub[0]), str(sub[3]), str(sub[1] * sub[3]),
                                                                     str(sub[2] * sub[3]), name)
    report += hl
    report += "{:<30} {:^3} {:>10} {:>10}\n".format("Total", str(total_qty), str(total_cost), str(total_sales))

    print(report)


def axxess():
    report = "IS Per Account Reconciliation\n"
    report += " {:^30} {:^3} {:^10} {:^10} {:^30} \n".format("Description", "Qty", "Cost", "Sales", "Client")
    hl = "-" * 89 + "\n"
    report += hl

    total_cost = 0
    total_sales = 0
    total_qty = 0
    for sub in subs:
        if sub[-2] == 'axx001':
            total_cost += (sub[1] if sub[1] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_sales += (sub[2] if sub[2] is not None else 0) * (sub[3] if sub[3] is not None else 0)
            total_qty += (sub[3] if sub[3] is not None else 0)
            if sub[6] is None:
                name = (sub[4] if sub[4] is not None else "") + " " + (sub[5] if sub[5] is not None else "")
            else:
                name = sub[6]
            report += "|{:<30}|{:^3}|{:>10}|{:>10}|{:>30}|\n".format(str(sub[0]), str(sub[3]), str(sub[1] * sub[3]),
                                                                     str(sub[2] * sub[3]), name)
    report += hl
    report += " {:<30} {:^3} {:>10} {:>10}\n".format("Total", str(total_qty), str(total_cost), str(total_sales))

    print(report)

axxess()

#is_ADSL()

#is_Domain()

#is_Mobile()