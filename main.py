
from mysql import connector
from decimal import Decimal
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


def replace_none(value, alternate):
    return alternate if value is None else value


def connect(username, password, hostname):
    return connector.connect(user=username,
                             password=password,
                             host=hostname)


def run_query(connection, query_str):
    def normalize(x):
        if isinstance(x, Decimal):
            return float(x)
        return x
    cursor = connection.cursor()
    cursor.execute(query_str)
    c_names, q_result = cursor.column_names, cursor.fetchall()
    result_set = [{k: normalize(q_row[j]) for j, k in enumerate(c_names)} for q_row in q_result]
    return result_set


def default_report(title, result_set, **flags):
    report = ['{}\n{:^30} {:^3} {:^10} {:^10} {:^30} \n'.format(title, 'Description', 'Qty', 'Cost', 'Sales', 'Client')]
    hl = '-' * 89 + '\n'
    report.append(hl)

    flags = dict(**flags)
    row_str = '|{:<30}|{:^3}|{:>10}|{:>10}|{:>30}|\n'

    total_cost, total_sales, total_qty = 0, 0, 0
    for entry in result_set:
        state = sum([entry[k] in flags[k].split(', ') for k in flags.keys()]) == len(flags) if flags else True
        if state:
            cost_price = entry['cost_price'] * entry['qty']
            sales_price = entry['sales_price'] * entry['qty']

            f_name, l_name, company = entry['first_name'], entry['last_name'], entry['company']
            if company is None:
                name = '{} {}'.format(replace_none(f_name, ''), replace_none(l_name, ''))
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
                         type='domain',
                         supplier='is0001'))


def internet_solutions_mobile():
    print(default_report(title='IS Mobile Reconciliation',
                         result_set=results,
                         type='mobile',
                         supplier='is0001'))


def internet_solution_adsl():
    print(default_report(title='IS Per Account Reconciliation',
                         result_set=results,
                         type='peracc, uncapped',
                         supplier='is0001'))

    print(default_report(title='IS Per GB Reconciliation',
                         result_set=results,
                         type='pergb',
                         supplier='is0001'))


def axxess():
    print(default_report(title='Axxess Reconciliation',
                         result_set=results,
                         supplier='axx001'))

# axxess()

# internet_solution_adsl()

# internet_solutions_domain()

# internet_solutions_mobile()

cur = conn.cursor()


def client_totals():
    subs = run_query(conn,
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

    report = "Client Totals\n"
    report += " {:^30} {:^10} {:^10} \n".format("Client", "Cost", "Sales")
    hl = "-" * 54 + "\n"
    report += hl

    total_cost, total_sales, total_qty = 0, 0, 0
    for sub in subs:
            total_cost += replace_none(sub['sum(cost_price*subscription.qty)'], 0)
            total_sales += replace_none(sub['sum(sales_price*subscription.qty)'], 0)
            total_qty += replace_none(sub['sum(subscription.qty)'], 0)
            if sub['company'] is None:
                name = '{} {}'.format(replace_none(sub['first_name'], ''), replace_none(sub['last_name']))
            else:
                name = sub['company']
            report += "|{:<30}|{:>10}|{:>10}|\n".format(name,
                                                        sub['sum(cost_price*subscription.qty)'],
                                                        sub['sum(sales_price*subscription.qty)'])
    report += hl
    report += " {:<30} {:>10} {:>10}\n".format("Total", total_cost, total_sales)
    print(report)


def client_invoice(client, me):
    report = "\n\n\n"

    sub = run_query(conn,
                    "SELECT \n"
                    "   me.code,\n"
                    "   first_name,\n"
                    "   last_name,\n"
                    "   company,\n"
                    "   vat,\n"
                    "   physical_address,\n"
                    "   postal_address\n"
                    "FROM ecn.me\n"
                    "WHERE ecn.me.code = '" + me + "';"
                    )[0]

    if sub['company'] is None:
        name = '{} {}'.format(replace_none(sub['first_name'], ''), replace_none(sub['last_name'], ''))
    else:
        name = sub['company']
    date = datetime.datetime.now()
    address = replace_none(sub['physical_address'], replace_none(sub['postal_address'], ''))
    address = (['', '', ''] if address == '' else address.split(', '))

    header_line = "{:<30}     {:^15}     {:>25}\n"
    report += (header_line * 5 + "\n\n").format(
        name, "", "",
        address[0], "", "Code: " + sub['code'],
        address[1], "", "",
        address[2], "", "",
                        "VAT: " + replace_none(sub['vat'], ''), "", "")

    sub = run_query(conn,
                    "SELECT \n"
                    "   client.code,\n"
                    "   first_name,\n"
                    "   last_name,\n"
                    "   company,\n"
                    "   vat,\n"
                    "   physical_address,\n"
                    "   postal_address\n"
                    "FROM ecn.client\n"
                    "where ecn.client.code = '" + client + "';"
                    )[0]
    if sub['company'] is None:
        name = replace_none(sub['first_name'], '') + ' ' + replace_none(sub['last_name'], '')
    else:
        name = sub['company']
    date = datetime.datetime.now()
    address = replace_none(sub['physical_address'], replace_none(sub['postal_address'], ''))
    address = ['', '', ''] if address == '' else address.split(', ')

    report += (header_line * 5 + "\n\n").format(
                name,       "", "",
                address[0], "", "Code: " + sub['code'],
                address[1], "", "",
                address[2], "", "",
                "VAT: " + replace_none(sub['vat'], ''), "", "")
    report += "\n\n"

    subs = run_query(conn,
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

    hl = "+" + "-" * 78 + "+\n"
    report += hl
    report += "|{:^10}|{:^30}|{:^3}|{:^10}|{:^10}|{:^10}|\n".format("Code", "Service", "Qty", "Unit", "VAT", "Subtotal")
    report += hl

    total_exvat, total_vat, total_sales = 0, 0, 0
    for sub in subs:
            total_exvat += sub['qty'] * sub['sales_price']
            total_vat += sub['qty'] * sub['sales_price'] * 0.14
            total_sales += sub['qty'] * sub['sales_price'] * 1.14
            cur.execute("INSERT INTO ecn.sales_invoice (number, date, client, service) VALUES ('0d49b1fd9f', '2017-6-30', 'gbg001', 'dsl4');")
            report += "|{:<10}|{:<30}|{:>3}|{:>10}|{:>10}|{:>10}|\n"\
                .format(sub['code'],
                        sub['description'],
                        sub['qty'],
                        round(sub['sales_price'], 2),
                        round(sub['sales_price'] * 0.14, 2),
                        round(sub['qty'] * sub['sales_price'] * 1.14, 2))
    report += hl
    report += "|{:<40}  {:>3}|{:>10}|{:>10}|{:>10}|\n"\
        .format("Totals", "", round(total_exvat, 2), round(total_vat, 2), round(total_sales, 2))
    report += hl + "\n\n"

    lines = report.split('\n')[2:-2]
    report = '\n'.join(['{:^{}}'.format(line, page[0]) for line in lines]) + "\n" * (page[1] - len(lines) % page[1])
    return report, total_sales


def service_totals(supplier):
    subs = run_query(conn,
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

    report = "Service Totals by Supplier\n"
    report += " {:^30} {:^3} {:^10} {:^10} \n".format("Client", "Qty", "Cost", "Sales")
    hl = "-" * 58 + "\n"
    report += hl

    total_cost = 0
    total_sales = 0
    total_qty = 0
    for sub in subs:
        if sub['supplier'] == supplier:
            total_cost += replace_none(sub['sum(sales_price*subscription.qty)'], 0)
            total_sales += replace_none(sub['sum(sales_price*subscription.qty)'], 0)
            total_qty += replace_none(sub['sum(subscription.qty)'], 0)
            if sub['company'] is None:
                name = '{} {}'.format(replace_none(sub['first_name'], ''), replace_none(sub['last_name'], ''))
            else:
                name = sub['company']
            report += "|{:<30}|{:^3}|{:>10}|{:>10}|\n".format(sub['description'],
                                                              sub['sum(subscription.qty)'],
                                                              sub['sum(sales_price*subscription.qty)'],
                                                              sub['sum(sales_price*subscription.qty)'])
    report += hl
    report += " {:<30} {:^3} {:>10} {:>10}\n".format("Total", total_qty, total_cost, total_sales)
    print(report)


def monthly_accounts_per_client(PRINT_ZEROES=False):
    report = []
    subs = run_query(conn,
                     "SELECT\
                        client.code\
                     FROM ecn.client;")
    for sub in subs:
        invoice = client_invoice(sub['code'], "ecn001")
        if invoice[1] > 0 or PRINT_ZEROES:
            report.append(invoice[0])
    return report

# service_totals('axx001')

# invoices = monthly_accounts_per_client()
# for invoice in invoices:
#     print(invoice)
