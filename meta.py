
import datetime

from connection import Connection, o, AS_PYE
from defaults import U_NAME, P_WORD, H_NAME, DB_NAME, PAGE, VAT_RATE, normalise_alias, replace_none


CONN = Connection(username=U_NAME,
                  password=P_WORD,
                  hostname=H_NAME,
                  db_name=DB_NAME)


def journal_entry(date, journal_description, *ledgers, total=None):
    check, balance = 0, 0
    for value, description, account in ledgers:
        if value > 0:
            check += value
        balance += value
    is_balanced = (balance == 0) if total is None else (check == total and balance == 0)

    if is_balanced:
        enter_journal = 'INSERT INTO {}.journal (date, description, value)'.format(DB_NAME)
        CONN.query(enter_journal, (date, journal_description, check))

        enter_ledger = 'INSERT INTO {}.account_line_item (journal, value, description, account)'.format(DB_NAME)
        CONN.query(enter_ledger, ledgers, (0, -1))
    return is_balanced


def ledger(value, description, account):
    return value, description, account


def client_invoice(client, me):
    last_invoice_nr = CONN.query('SELECT code FROM {}.tax_invoice ORDER BY code DESC LIMIT 1;'.format(DB_NAME)).row(0)
    curr_invoice_nr = 0 if last_invoice_nr is None else last_invoice_nr['id']

    report = ['\n\n']

    # <editor-fold desc="HEADER: Supplier Letterhead">
    row = CONN.query("SELECT\n"
                     "    entity.code,\n"
                     "    first_name,\n"
                     "    last_name,\n"
                     "    company,\n"
                     "    vat,\n"
                     "    physical_address,\n"
                     "    postal_address\n"
                     "FROM ecn.entity\n"
                     "WHERE ecn.entity.code = '{}';".format(me)).row(0)

    header_line = '{:<30}     {:^15}     {:>25}\n'

    date = datetime.datetime.now()

    name = normalise_alias(row['first_name'], row['last_name'], row['company'])
    address = replace_none(row['physical_address'], replace_none(row['postal_address'], ''))
    street, town, zip_code = address.split(', ') if address else ('', '', '')

    report.append((header_line * 5 + "\n\n").format(name, "", "",
                                                    street, "", 'Code: {}'.format(row['code']),
                                                    town, "", "",
                                                    zip_code, "", "",
                                                    "VAT: " + replace_none(row['vat'], ''), '', ''))
    #</editor-fold>
    # <editor-fold desc="HEADER: Salutation">
    row = CONN.query("SELECT\n"
                     "    entity.code,\n"
                     "    first_name,\n"
                     "    last_name,\n"
                     "    company,\n"
                     "    vat,\n"
                     "    physical_address,\n"
                     "    postal_address\n"
                     "FROM ecn.entity\n"
                     "WHERE ecn.entity.code = '{}';".format(client)).row(0)

    name = normalise_alias(row['first_name'], row['last_name'], row['company'])
    address = replace_none(row['physical_address'], replace_none(row['postal_address'], ''))
    street, town, zip_code = address.split(', ') if address else ('', '', '')

    report.append((header_line * 5 + "\n\n").format(name, "", "",
                                                    street, "", 'Code: {}'.format(row['code']),
                                                    town, "", "",
                                                    zip_code, "", "",
                                                    "VAT: " + replace_none(row['vat'], ''), '', ''))
    report.append('\n')
    #</editor-fold>
    # <editor-fold desc="BODY  : Invoice Line Items">
    result = CONN.query("SELECT\n"
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
                        "AND ecn.entity.code = '{}';".format(client))

    hl = "+" + "-" * 78 + '+'
    report.append(hl)
    report.append("|{:^10}|{:^30}|{:^3}|{:^10}|{:^10}|{:^10}|".format("Code", "Service", "Qty", "Unit", "VAT", "Subtotal"))
    report.append(hl)

    # rename these accordingly
    accounts = CONN.select('id, name', 'account')

    ledger_a = accounts.filter(o(owner=client, name='Supplier Control').x(AS_PYE))['id']
    ledger_b = accounts.filter(o(owner=me, name='Customer Control').x(AS_PYE))['id']
    ledger_c = accounts.filter(o(owner=client, name='VAT Control').x(AS_PYE))['id']
    ledger_d = accounts.filter(o(owner=me, name='VAT Control').x(AS_PYE))['id']

    row_str = '|{:<10}|{:<30}|{:>3}|{:>10}|{:>10}|{:>10}|'
    total_exvat, total_vat, total_sales = 0, 0, 0
    ledgers = []
    for row in result.rows():
        ledgers.append(ledger(row['sales_price'],
                              row['description'],
                              ledger_a))
        ledgers.append(ledger(row['sales_price'] * -1,
                              row['description'],
                              ledger_b))
        ledgers.append(ledger(row['sales_price'] * VAT_RATE,
                              row['description'],
                              ledger_c))
        ledgers.append(ledger(row['sales_price'] * -VAT_RATE,
                              row['description'],
                              ledger_d))

        total_exvat += row['qty'] * row['sales_price']
        total_vat += row['qty'] * row['sales_price'] * 0.14
        total_sales += row['qty'] * row['sales_price'] * 1.14

        report.append(row_str.format(row['code'],
                                     row['description'],
                                     row['qty'],
                                     round(row['sales_price'], 2),
                                     round(row['sales_price'] * VAT_RATE, 2),
                                     round(row['qty'] * row['sales_price'] * (1 + VAT_RATE), 2)))
    if len(ledgers) > 0:
        journal = journal_entry(date, 'Tax Invoice Nr.{}'.format(curr_invoice_nr), *ledgers)
        if journal is not None:
            CONN.query('INSERT INTO {}.tax_invoice (code, reseller, client, journal)'.format(DB_NAME),
                       (curr_invoice_nr, me, client), (3, -2))

            # call the update functions when applicable
            # CONN.update()
            # CONN.commit()

    report.append(hl)
    report.append("|{:<40}  {:>3}|{:>10}|{:>10}|{:>10}|".format(
        "Totals", "", round(total_exvat, 2), round(total_vat, 2), round(total_sales, 2)))
    report.append(hl)
    # </editor-fold>

    # Center the report on the page
    report = '\n'.join(['{:^{}}'.format(line, PAGE[0]) for line in report]) + "\n" * (PAGE[1] - len(report) % PAGE[1])
    return report, total_sales


def monthly_accounts_per_client(PRINT_ZEROES=False):
    report = []
    result = CONN.query("SELECT\n"
                        "   entity.code\n"
                        "FROM ecn.entity;")
    for row in result.rows():
        invoice = client_invoice(row['code'], "ecn001")
        if invoice[1] > 0 or PRINT_ZEROES:
            report.append(invoice[0])
    return report

if __name__ == '__main__':
    pass
