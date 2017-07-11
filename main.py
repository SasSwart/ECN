import mysql.connector
import datetime
import hashlib

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


def md5(fname):
    hash_md5 = hashlib.md5()
    hash_md5.update(fname)
    return hash_md5.hexdigest()

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


def save_file():
    ()


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
    report = "Axxess Reconciliation\n"
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

def client_totals():
    cur.execute(
        "SELECT \
            service.description,\
            sum(cost_price*subscription.qty),\
            sum(sales_price*subscription.qty),\
            sum(subscription.qty),\
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
        and ecn.subscription.service = ecn.service.code\
        group by client.code;")

    subsHeader = cur.column_names
    subs = cur.fetchall()

    report = "Client Totals\n"
    report += " {:^30} {:^10} {:^10} \n".format("Client", "Cost", "Sales")
    hl = "-" * 54 + "\n"
    report += hl

    total_cost = 0
    total_sales = 0
    total_qty = 0
    for sub in subs:
            total_cost += (sub[1] if sub[1] is not None else 0)
            total_sales += (sub[2] if sub[2] is not None else 0)
            total_qty += (sub[3] if sub[3] is not None else 0)
            if sub[6] is None:
                name = (sub[4] if sub[4] is not None else "") + " " + (sub[5] if sub[5] is not None else "")
            else:
                name = sub[6]
            report += "|{:<30}|{:>10}|{:>10}|\n".format(name, str(sub[1]), str(sub[2]))
    report += hl
    report += " {:<30} {:>10} {:>10}\n".format("Total", str(total_cost), str(total_sales))

    print(report)


def client_invoice(client):
    report = "\n"
    cur.execute("SELECT \n"
                "   client.code,\n"
                "   first_name,\n"
                "   last_name,\n"
                "   company,\n"
                "   vat,\n"
                "   physical_address,\n"
                "   postal_address\n"
                "FROM ecn.client\n"
                "where ecn.client.code = '"+client+"';")
    subs = cur.fetchall()
    if subs[0][3] is None:
        name = (subs[0][1] if subs[0][1] is not None else "") + " " + (subs[0][2] if subs[0][2] is not None else "")
    else:
        name =  subs[0][3]
    date = datetime.datetime.now()
    address = (subs[0][5] if subs[0][5] is not None else ((subs[0][6] if subs[0][6] is not None else "")))
    address = address.split(', ')

    report += "{:<30}     {:^15}     {:>25}\n"\
        .format(name, "Tax Invoice", str(date.year) + "-" + str(date.month) + "-" + str(date.day))
    report += "{:<30}     {:^15}     {:>25}\n"\
        .format(address[0], "Nr." + md5(str(date).encode())[:10], "Code: " + subs[0][0])
    report += "{:<30}     {:^15}     {:>25}\n"\
        .format(address[1], "", "")
    report += "{:<30}     {:^15}     {:>25}\n"\
        .format(address[2], "", "")
    report += "{:<30}     {:^15}     {:>25}\n"\
        .format("VAT: " + (subs[0][4] if subs[0][4] is not None else ""), "", "")
    report += "\n\n"

    cur.execute(
        "SELECT \
            service.code,\
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
        and ecn.subscription.service = ecn.service.code \
        and ecn.client.code = '" + client + "';")

    subsHeader = cur.column_names
    subs = cur.fetchall()

    hl = "+" + "-" * 78 + "+\n"
    report += hl
    report += "|{:^10}|{:^30}|{:^3}|{:^10}|{:^10}|{:^10}|\n".format("Code", "Service","Qty", "Unit", "VAT", "Subtotal")
    report += hl

    total_exvat = 0
    total_vat = 0
    total_sales = 0
    for sub in subs:
            total_exvat += float(sub[4]) * float(sub[3])
            total_vat += float(sub[4]) * float(sub[3]) * 0.14
            total_sales += float(sub[4])*float(sub[3])*1.14
            cur.execute("INSERT INTO ecn.sales_invoice (number, date, client, service) VALUES ('0d49b1fd9f', '2017-6-30', 'gbg001', 'dsl4');")
            report += "|{:<10}|{:<30}|{:>3}|{:>10}|{:>10}|{:>10}|\n"\
                .format(str(sub[0]), str(sub[1]), str(sub[4]), str(round(sub[3],2)), str(round(float(sub[3])*0.14, 2)), str(round(float(sub[4])*float(sub[3])*1.14,2)))
    report += hl
    report += "|{:<40}  {:>3}|{:>10}|{:>10}|{:>10}|\n"\
        .format("Totals", "", str(round(total_exvat,2)), str(round(total_vat,2)), str(round(total_sales,2)))
    report += hl

    report = "\n".join(["{:^85}".format(line) for line in report.split('\n')])
    print(report)


def service_totals(supplier):
        cur.execute(
            "SELECT \
                service.description,\
                sum(cost_price*subscription.qty),\
                sum(sales_price*subscription.qty),\
                sum(subscription.qty),\
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
            and ecn.subscription.service = ecn.service.code\
            group by subscription.service;")

        subsHeader = cur.column_names
        subs = cur.fetchall()

        report = "Service Totals by Supplier\n"
        report += " {:^30} {:^3} {:^10} {:^10} \n".format("Client", "Qty", "Cost", "Sales")
        hl = "-" * 58 + "\n"
        report += hl

        total_cost = 0
        total_sales = 0
        total_qty = 0
        for sub in subs:
            if sub[-2] == supplier:
                total_cost += (sub[1] if sub[1] is not None else 0)
                total_sales += (sub[2] if sub[2] is not None else 0)
                total_qty += (sub[3] if sub[3] is not None else 0)
                if sub[6] is None:
                    name = (sub[4] if sub[4] is not None else "") + " " + (sub[5] if sub[5] is not None else "")
                else:
                    name = sub[6]
                report += "|{:<30}|{:^3}|{:>10}|{:>10}|\n".format(str(sub[0]), str(sub[3]), str(sub[1]), str(sub[2]))
        report += hl
        report += " {:<30} {:^3} {:>10} {:>10}\n".format("Total", str(total_qty), str(total_cost), str(total_sales))

        print(report)

#axxess()

#is_ADSL()

#is_Domain()

#is_Mobile()

#service_totals("is0001")

#client_totals()

client_invoice("ort001")
