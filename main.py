
from mysql import connector
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


def run_query(connection, query_str, last_id=False):
    def normalise_type(x):
        return x

    cursor = connection.cursor()
    cursor.execute(query_str)

    if cursor.description is None:
        if last_id:
            return cursor.getlastrowid()
        return None
    c_names, q_result = cursor.column_names, cursor.fetchall()
    result_set = [{k: normalise_type(q_row[j]) for j, k in enumerate(c_names)} for q_row in q_result]
    return result_set


conn = connect(username=u_name,
               password=p_word,
               hostname=h_name)


def journal_entry(date, total=None, *ledgers):
    check, balance = 0, 0
    for value, account in ledgers:
        if value > 0:
            check += value
        balance += value
    is_balanced = (balance == 0) if total is None else (check == total and balance == 0)

    if is_balanced:
        enter_journal = "INSERT INTO {}.journal (date, value) VALUES ('{}', '{}');".format(db_name, date, check)
        journal = run_query(conn, enter_journal, last_id=True)
        for value, account in ledgers:
            enter_ledger = ("INSERT INTO {}.account_line_item"
                            "(journal, value, account) VALUES ('{}', '{}', '{}');".format(db_name, journal, value, account))
            run_query(conn, enter_ledger)
    return is_balanced


def default_report(title, result_set, **flags):
    hl = '-' * 89
    report = [title, '{:^30} {:^3} {:^10} {:^10} {:^30}'.format('Description', 'Qty', 'Cost', 'Sales', 'Client'), hl]

    flags, row_str = dict(**flags), '|{:<30}|{:^3}|{:>10}|{:>10}|{:>30}|'
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
    report.append(' {:<30} {:^3} {:>10} {:>10}'.format('Total', total_qty, total_cost, total_sales))
    return '\n'.join(report)

conn = connect(username=u_name,
               password=p_word,
               hostname=h_name)

results = run_query(conn, "SELECT\n"
                          "    service.description,\n"
                          "    cost_price,\n"
                          "    sales_price,\n"
                          "    subscription.qty,\n"
                          "    first_name,\n"
                          "    last_name,\n"
                          "    company,\n"
                          "    entity.code,\n"
                          "    subscription.service,\n"
                          "    service.supplier,\n"
                          "    service.type\n"
                          "FROM ecn.entity, ecn.subscription, ecn.service, ecn.service_type\n"
                          "WHERE ecn.entity.code = ecn.subscription.client\n"
                          "AND ecn.service.type = ecn.service_type.type\n"
                          "AND ecn.subscription.service = ecn.service.code;")


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
                     "SELECT\n"
                     "    service.description,\n"
                     "    sum(cost_price*subscription.qty) as total_cost,\n"
                     "    sum(sales_price*subscription.qty) as total_sales,\n"
                     "    sum(subscription.qty) as total_qty,\n"
                     "    first_name,\n"
                     "    last_name,\n"
                     "    company,\n"
                     "    client.code,\n"
                     "    subscription.service,\n"
                     "    service.supplier,\n"
                     "    service.type\n"
                     "FROM ecn.entity, ecn.subscription, ecn.service, ecn.service_type\n"
                     "WHERE ecn.entity.code = ecn.subscription.client\n"
                     "AND ecn.service.type = ecn.service_type.type\n"
                     "AND ecn.subscription.service = ecn.service.code\n"
                     "GROUP BY entity.code;")

    hl = "-" * 54
    report = ["Client Totals", " {:^30} {:^10} {:^10}".format("Client", "Cost", "Sales"), hl]

    total_cost, total_sales, total_qty = 0, 0, 0
    for sub in subs:
            total_cost += replace_none(sub['total_cost'], 0)
            total_sales += replace_none(sub['total_sales'], 0)
            total_qty += replace_none(sub['total_qty'], 0)
            if sub['company'] is None:
                name = '{} {}'.format(replace_none(sub['first_name'], ''), replace_none(sub['last_name'], ''))
            else:
                name = sub['company']
            report.append("|{:<30}|{:>10}|{:>10}|".format(name,
                                                          sub['total_cost'],
                                                          sub['total_sales']))
    report.append(hl)
    report.append(" {:<30} {:>10} {:>10}".format("Total", total_cost, total_sales))
    print('\n'.join(report))


def client_invoice(client, me):
    report = ['\n\n']
    sub = run_query(conn,
                    "SELECT\n"
                    "    entity.code,\n"
                    "    first_name,\n"
                    "    last_name,\n"
                    "    company,\n"
                    "    vat,\n"
                    "    physical_address,\n"
                    "    postal_address\n"
                    "FROM ecn.entity\n"
                    "WHERE ecn.entity.code = '" + me + "';"
                    )[0]

    if sub['company'] is None:
        name = '{} {}'.format(replace_none(sub['first_name'], ''), replace_none(sub['last_name'], ''))
    else:
        name = sub['company']
    date = datetime.datetime.now()
    address = replace_none(sub['physical_address'], replace_none(sub['postal_address'], ''))
    address = (['', '', ''] if address == '' else address.split(', '))
    header_line = "{:<30}     {:^15}     {:>25}\n"
    report.append((header_line * 5 + "\n\n").format(
                   name, "", "",
                   address[0], "", "Code: " + sub['code'],
                   address[1], "", "",
                   address[2], "", "",
                   "VAT: " + replace_none(sub['vat'], ''), "", ""))

    sub = run_query(conn,
                    "SELECT\n"
                    "    entity.code,\n"
                    "    first_name,\n"
                    "    last_name,\n"
                    "    company,\n"
                    "    vat,\n"
                    "    physical_address,\n"
                    "    postal_address\n"
                    "FROM ecn.entity\n"
                    "WHERE ecn.entity.code = '" + client + "';"
                    )[0]
    if sub['company'] is None:
        name = replace_none(sub['first_name'], '') + ' ' + replace_none(sub['last_name'], '')
    else:
        name = sub['company']
    date = datetime.datetime.now()
    address = replace_none(sub['physical_address'], replace_none(sub['postal_address'], ''))
    address = ['', '', ''] if address == '' else address.split(', ')

    report.append((header_line * 5 + "\n\n").format(
                  name,       "", "",
                  address[0], "", "Code: " + sub['code'],
                  address[1], "", "",
                  address[2], "", "",
                  "VAT: " + replace_none(sub['vat'], ''), "", ""))
    report.append('\n')

    subs = run_query(conn,
                     "SELECT\n"
                     "    service.code,\n"
                     "    service.description,\n"
                     "    cost_price,\n"
                     "    sales_price,\n"
                     "    subscription.qty,\n"
                     "    first_name,\n"
                     "    last_name,\n"
                     "    company,\n"
                     "    entity.code,\n"
                     "    subscription.service,\n"
                     "    service.supplier,\n"
                     "    service.type\n"
                     "FROM ecn.entity, ecn.subscription, ecn.service, ecn.service_type\n"
                     "WHERE ecn.entity.code = ecn.subscription.client\n"
                     "AND ecn.service.type = ecn.service_type.type\n"
                     "AND ecn.subscription.service = ecn.service.code\n"
                     "AND ecn.entity.code = '" + client + "';")

    hl = "+" + "-" * 78 + '+'
    report.append(hl)
    report.append(
        "|{:^10}|{:^30}|{:^3}|{:^10}|{:^10}|{:^10}|".format("Code", "Service", "Qty", "Unit", "VAT", "Subtotal"))
    report.append(hl)

    total_exvat, total_vat, total_sales = 0, 0, 0
    for sub in subs:
            total_exvat += sub['qty'] * sub['sales_price']
            total_vat += sub['qty'] * sub['sales_price'] * 0.14
            total_sales += sub['qty'] * sub['sales_price'] * 1.14
            # cur.execute("INSERT INTO ecn.sales_invoice (number, date, client, service) VALUES ('0d49b1fd9f', '2017-6-30', 'gbg001', 'dsl4');")
            report.append(
                "|{:<10}|{:<30}|{:>3}|{:>10}|{:>10}|{:>10}|".format(sub['code'],
                                                                    sub['description'],
                                                                    sub['qty'],
                                                                    round(sub['sales_price'], 2),
                                                                    round(sub['sales_price'] * 0.14, 2),
                                                                    round(sub['qty'] * sub['sales_price'] * 1.14, 2)))
    report.append(hl)
    report.append("|{:<40}  {:>3}|{:>10}|{:>10}|{:>10}|".format(
        "Totals", "", round(total_exvat, 2), round(total_vat, 2), round(total_sales, 2)))
    report.append(hl)
    report = '\n'.join(['{:^{}}'.format(line, page[0]) for line in report]) + "\n" * (page[1] - len(report) % page[1])
    return report, total_sales


def service_totals(supplier):
    subs = run_query(conn,
                     "SELECT\n"
                     "   service.description,\n"
                     "   sum(cost_price*subscription.qty) as total_cost,\n"
                     "   sum(sales_price*subscription.qty) as total_sales,\n"
                     "   sum(subscription.qty) as total_qty,\n"
                     "   first_name,\n"
                     "   last_name,\n"
                     "   company,\n"
                     "   entity.code,\n"
                     "   subscription.service,\n"
                     "   service.supplier,\n"
                     "   service.type\n"
                     "FROM ecn.entity, ecn.subscription, ecn.service, ecn.service_type\n"
                     "WHERE ecn.entity.code = ecn.subscription.client\n"
                     "AND ecn.service.type = ecn.service_type.type\n"
                     "AND ecn.subscription.service = ecn.service.code\n"
                     "GROUP BY subscription.service;")

    report = ["Service Totals by Supplier", " {:^30} {:^3} {:^10} {:^10} ".format("Client", "Qty", "Cost", "Sales")]
    hl = "-" * 58
    report.append(hl)

    total_cost, total_sales, total_qty = 0, 0, 0
    for sub in subs:
        if sub['supplier'] == supplier:
            total_cost += replace_none(sub['total_cost'], 0)
            total_sales += replace_none(sub['total_sales'], 0)
            total_qty += replace_none(sub['total_qty'], 0)
            if sub['company'] is None:
                name = '{} {}'.format(replace_none(sub['first_name'], ''), replace_none(sub['last_name'], ''))
            else:
                name = sub['company']
            report.append("|{:<30}|{:^3}|{:>10}|{:>10}|".format(sub['description'],
                                                                sub['total_qty'],
                                                                sub['total_cost'],
                                                                sub['total_sales']))
    report.append(hl)
    report.append(" {:<30} {:^3} {:>10} {:>10}".format("Total", total_qty, total_cost, total_sales))
    print('\n'.join(report))


def monthly_accounts_per_client(PRINT_ZEROES=False):
    report = []
    subs = run_query(conn,
                     "SELECT\n"
                     "   entity.code\n"
                     "FROM ecn.entity;")
    for sub in subs:
        invoice = client_invoice(sub['code'], "ecn001")
        if invoice[1] > 0 or PRINT_ZEROES:
            report.append(invoice[0])
    return report

# service_totals('axx001')

# axxess()

# internet_solution_adsl()

# internet_solutions_domain()

# internet_solutions_mobile()

# invoices = monthly_accounts_per_client()
# for invoice in invoices:
#     print(invoice)