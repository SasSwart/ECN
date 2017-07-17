import mysql.connector
import datetime
import hashlib

h_name = "192.168.0.33"
u_name = "root"
p_word = "Hunt!ngSpr!ngbuck123"

page = (85, 58)


def md5(f_name):
    hash_md5 = hashlib.md5()
    hash_md5.update(f_name)
    return hash_md5.hexdigest()


def save_file():
    pass


def connect(username, password, hostname):
    return mysql.connector.connect(user=username,
                                   password=password,
                                   host=hostname)


def run_query(connection, query_str):
    cur = connection.cursor()
    cur.execute(query_str)
    c_names, q_result = cur.column_names, cur.fetchall()
    result_set = [{k: q_result[i][j] for j, k in enumerate(c_names)} for i in range(len(q_result))]
    return result_set


def default_report(title, result_set, flags={}):
    report = ['{}\n{:^30} {:^3} {:^10} {:^10} {:^30} \n'.format(title, 'Description', 'Qty', 'Cost', 'Sales', 'Client')]
    hl = '-' * 89 + '\n'
    report.append(hl)

    total_cost, total_sales, total_qty = 0, 0, 0
    row_str = '|{:<30}|{:^3}|{:>10}|{:>10}|{:>30}|\n'
    for entry in result_set:
        state = sum([entry[k] in flags[k].split(', ') for k in flags.keys()]) == len(flags) if flags else True
        if state:
            cost_price = entry['cost_price'] * entry['qty']
            sales_price = entry['sales_price'] * entry['qty']

            f_name, l_name, company = entry['first_name'], entry['last_name'], entry['company']
            if company is None:
                name = '{} {}'.format('_' if f_name is None else f_name, '_' if l_name is None else l_name)
            else:
                name = company

            total_cost += cost_price
            total_sales += sales_price
            total_qty += entry['qty']

            report.append(row_str.format(entry['description'], entry['qty'], cost_price, sales_price, name))
    report.append(hl)
    report.append(' {:<30} {:^3} {:>10} {:>10}\n'.format('Total', total_qty, total_cost, total_sales))
    return ''.join(report)

conn = connect(username=u_name,
               password=p_word,
               hostname=h_name)

q_str = \
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
    WHERE ecn.client.code = ecn.subscription.client \
    AND ecn.service.type = ecn.service_type.type \
    AND ecn.subscription.service = ecn.service.code;"

results = run_query(conn, q_str)


def internet_solutions_domain():
    print(default_report(title='IS Domain Reconciliation',
                         result_set=results,
                         flags={'type': 'domain',
                                'supplier': 'is0001'}))


def internet_solutions_mobile():
    print(default_report(title='IS Mobile Reconciliation',
                         result_set=results,
                         flags={'type': 'mobile',
                                'supplier': 'is0001'}))


def internet_solution_adsl():
    print(default_report(title='IS Per Account Reconciliation',
                         result_set=results,
                         flags={'type': 'peracc, uncapped',
                                'supplier': 'is0001'}))

    print(default_report(title='IS Per GB Reconciliation',
                         result_set=results,
                         flags={'type': 'pergb',
                                'supplier': 'is0001'}))


def axxess():
    print(default_report(title='Axxess Reconciliation',
                         result_set=results,
                         flags={'supplier': 'axx001'}))

cur = conn.cursor()


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

    subs_header = cur.column_names
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


def client_invoice(client, me):
    report = "\n\n\n"
    cur.execute("SELECT \n"
                "   me.code,\n"
                "   first_name,\n"
                "   last_name,\n"
                "   company,\n"
                "   vat,\n"
                "   physical_address,\n"
                "   postal_address\n"
                "FROM ecn.me\n"
                "where ecn.me.code = '" + me + "';")
    subs = cur.fetchall()
    if subs[0][3] is None:
        name = (subs[0][1] if subs[0][1] is not None else "") + " " + (subs[0][2] if subs[0][2] is not None else "")
    else:
        name = subs[0][3]
    date = datetime.datetime.now()
    address = (subs[0][5] if subs[0][5] is not None else (subs[0][6] if subs[0][6] is not None else ""))
    address = (['', '', ''] if address == '' else address.split(', '))

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

    cur.execute("SELECT \n"
                "   client.code,\n"
                "   first_name,\n"
                "   last_name,\n"
                "   company,\n"
                "   vat,\n"
                "   physical_address,\n"
                "   postal_address\n"
                "FROM ecn.client\n"
                "where ecn.client.code = '" + client + "';")
    subs = cur.fetchall()
    if subs[0][3] is None:
        name = (subs[0][1] if subs[0][1] is not None else "") + " " + (subs[0][2] if subs[0][2] is not None else "")
    else:
        name = subs[0][3]
    date = datetime.datetime.now()
    address = (subs[0][5] if subs[0][5] is not None else (subs[0][6] if subs[0][6] is not None else ""))
    address = (['', '', ''] if address == '' else address.split(', '))

    report += "{:<30}     {:^15}     {:>25}\n" \
        .format(name, "", "")
    report += "{:<30}     {:^15}     {:>25}\n" \
        .format(address[0], "", "Code: " + subs[0][0])
    report += "{:<30}     {:^15}     {:>25}\n" \
        .format(address[1], "", "")
    report += "{:<30}     {:^15}     {:>25}\n" \
        .format(address[2], "", "")
    report += "{:<30}     {:^15}     {:>25}\n" \
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
    report += "|{:^10}|{:^30}|{:^3}|{:^10}|{:^10}|{:^10}|\n".format("Code", "Service", "Qty", "Unit", "VAT", "Subtotal")
    report += hl

    total_exvat = 0
    total_vat = 0
    total_sales = 0
    for sub in subs:
            total_exvat += float(sub[4]) * float(sub[3])
            total_vat += float(sub[4]) * float(sub[3]) * 0.14
            total_sales += float(sub[4]) * float(sub[3]) * 1.14
            cur.execute("INSERT INTO ecn.sales_invoice (number, date, client, service) VALUES ('0d49b1fd9f', '2017-6-30', 'gbg001', 'dsl4');")
            report += "|{:<10}|{:<30}|{:>3}|{:>10}|{:>10}|{:>10}|\n"\
                .format(str(sub[0]), str(sub[1]), str(sub[4]), str(round(sub[3],2)), str(round(float(sub[3])*0.14, 2)), str(round(float(sub[4])*float(sub[3])*1.14,2)))
    report += hl
    report += "|{:<40}  {:>3}|{:>10}|{:>10}|{:>10}|\n"\
        .format("Totals", "", str(round(total_exvat,2)), str(round(total_vat,2)), str(round(total_sales,2)))
    report += hl + "\n\n"

    lines = report.split('\n')[2:-2]
    report = "\n".join([str("{:^"+str(page[0])+"}").format(line) for line in lines]) + "\n"*(page[1]-len(lines)%page[1])
    return report, total_sales


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


def monthly_accounts_per_client(PRINT_ZEROES=False):
    report = []
    cur.execute(
        "SELECT\
            client.code\
        FROM ecn.client;")
    subs = cur.fetchall()

    for sub in subs:
        invoice = client_invoice(sub[0], "ecn001")
        if invoice[1] > 0 or PRINT_ZEROES:
            report.append(invoice[0])
    return report

# axxess()

# internet_solution_adsl()

# internet_solutions_domain()

# internet_solutions_mobile()

# service_totals("is0001")

# client_totals()


invoices = monthly_accounts_per_client()
for invoice in invoices:
    print(invoice)
