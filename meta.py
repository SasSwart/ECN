
import datetime
import hashlib

from connection import Connection
from conditional import o
from defaults import U_NAME, P_WORD, H_NAME, DB_NAME, PAGE, VAT_RATE, normalise_alias, replace_value, literal


CONN = Connection(username=U_NAME,
                  password=P_WORD,
                  hostname=H_NAME,
                  db_name=DB_NAME)


def document_id():
    hash_md5 = hashlib.md5()
    hash_md5.update(str(datetime.datetime.now()).encode('utf-8'))
    return hash_md5.hexdigest()[:10]


def journal_entry(date, journal_description, *ledgers, total=None):
    journal, pair = document_id(), [0, 0]

    def pack(accumulator, a, b, c, d):
        x, y = accumulator
        accumulator[:] = x + (b if b > 0 else 0), y + b
        return a, b, c, d

    ledgers = [pack(pair, journal, value, description, account) for value, description, account in ledgers]

    check, balance = pair
    is_balanced = balance == 0 if total is None else (check == total and balance == 0)

    if is_balanced:
        CONN.stmt()\
            ('INSERT_INTO')('journal')\
            ('COLUMNS')('id', 'date', 'description', 'value')\
            ('VALUES')(journal, date, journal_description, check)()

        for l in ledgers:
            CONN.stmt()\
                ('INSERT_INTO')('account_line_item')\
                ('COLUMNS')('journal', 'value', 'description', 'account')\
                ('VALUES')(*l)()
    return journal


def ledger(value, description, account):
    return value, description, account


def create_invoice(client, me):
    curr_invoice_nr, date = document_id(), datetime.datetime.now()

    result = CONN.stmt()\
        ('SELECT')('service.code',         'service.description',
                   'cost_price',           'sales_price',
                   'subscription.qty',     'first_name',
                   'last_name',            'company',
                   'entity.code',          'subscription.service',
                   'service.supplier',     'service.type')\
        ('FROM')('entity',  'subscription',
                 'service', 'service_type')\
        ('WHERE')(o('entity.code', 'service.type', 'subscription.service', 'entity.code') *
                  o('subscription.client', 'service_type.type', 'service.code', '{}'.format(literal(client))))()

    accounts = CONN.stmt()('SELECT')('id', 'name', 'owner')('FROM')('account')()

    ledger_a = accounts.filter(o(owner=literal(client), name='\'Supplier Control\''))[0]['id']
    ledger_b = accounts.filter(o(owner=literal(me), name='\'Customer Control\''))[0]['id']
    ledger_c = accounts.filter(o(owner=literal(client), name='\'VAT Control\''))[0]['id']
    ledger_d = accounts.filter(o(owner=literal(me), name='\'VAT Control\''))[0]['id']

    ledgers = []
    for row in result:
        ledgers.append(ledger(row['sales_price'],
                              row['description'],
                              ledger_a))
        ledgers.append(ledger(row['sales_price'] * -1,
                              row['description'],
                              ledger_b))
        ledgers.append(ledger(row['sales_price'] * VAT_RATE,
                              "VAT on " + row['description'],
                              ledger_c))
        ledgers.append(ledger(row['sales_price'] * -VAT_RATE,
                              "VAT on " + row['description'],
                              ledger_d))

    if len(ledgers) > 0:
        journal = journal_entry(str(date), 'Tax Invoice Nr.{}'.format(curr_invoice_nr), *ledgers)
        if journal is not None:
            CONN.stmt()\
                ('INSERT_INTO')('tax_invoice')\
                ('COLUMNS')('code', 'reseller', 'client', 'journal')\
                ('VALUES')(curr_invoice_nr, me, client, journal)()

            CONN.update()
            CONN.commit()
            return True
    return False


def fetch_invoice(invoice_nr):
    tax_invoice = CONN.stmt()\
        ('SELECT')('*')\
        ('FROM')('tax_invoice')\
        ('WHERE')(o(code='b5d8ca3d85'))()

    reseller = CONN.stmt()\
        ('SELECT')('code', 'first_name', 'last_name', 'company', 'vat', 'physical_address', 'postal_address')\
        ('FROM')('entity')\
        ('WHERE')(o(code=tax_invoice[0]['reseller']))()

    client = CONN.stmt()\
        ('SELECT')('code', 'first_name', 'last_name', 'company', 'vat', 'physical_address', 'postal_address')\
        ('FROM')('entity')\
        ('WHERE')(o(code=tax_invoice[0]['client']))()

    journal = CONN.stmt()\
        ('SELECT')('id', 'date', 'description')\
        ('FROM')('journal')\
        ('WHERE')(o(id=tax_invoice[0]['journal']))()

    lines = CONN.stmt()\
        ('SELECT')('journal', 'description', 'qty', 'value')\
        ('FROM')('account_line_item')\
        ('WHERE')((o('value') > o(0)) & o(journal=journal[0]['id']))\
        ('ORDER_BY')('description', 'DESC', 'value', 'DESC')()

    print(print_invoice(reseller, client, journal, lines))


def print_invoice(reseller, client, journal, lines):
    reseller = reseller[0]
    client = client[0]
    journal = journal[0]

    r_code = reseller['code']
    r_name = normalise_alias(reseller['first_name'], reseller['last_name'], reseller['company'])
    r_address = replace_value(reseller['physical_address'], replace_value(reseller['postal_address'], ''))
    r_vat = reseller['vat']

    r_street, r_town, r_zip_code = r_address.split(', ') if r_address else ('', '', '')

    c_code = client['code']
    c_name = normalise_alias(client['first_name'], client['last_name'], client['company'])
    c_address = replace_value(client['physical_address'], replace_value(client['postal_address'], ''))
    c_vat = client['vat']

    c_street, c_town, c_zip_code = c_address.split(', ') if c_address else ('', '', '')

    j_date = journal['date']
    j_description = journal['description']

    header_line = '{:<30}     {:^25}     {:>25}\n'
    hl = "+" + "-" * 78 + '+' + '\n'
    report = []
    report.append(((header_line * 5 + "\n\n") * 2).format(r_name, j_description, 'Code: {}'.format(r_code),
                                                          r_street, str(j_date)[0:10], "",
                                                          r_town, "", "",
                                                          r_zip_code, "", "",
                                                          "VAT: " + replace_value(r_vat, ''), '', '',
                                                          c_name, "", 'Code: {}'.format(c_code),
                                                          c_street, "", "",
                                                          c_town, "", "",
                                                          c_zip_code, "", "",
                                                          "VAT: " + replace_value(c_vat, ''), '', ''))
    # Table Header
    report.append(hl)
    report.append(
        "|{:^10}|{:^30}|{:^3}|{:^10}|{:^10}|{:^10}|\n".format("Code", "Service", "Qty", "Unit", "VAT", "Subtotal"))
    report.append(hl)

    total_exvat, total_vat, total_sales = 0, 0, 0
    row_str = '|{:<10}|{:<30}|{:>3}|{:>10}|{:>10}|{:>10}|\n'
    for line in [(lines[i], lines[i+1]) for i in range(0,len(lines),2)]:
        total_exvat += line[0]['qty'] * line[0]['value']
        total_vat += line[1]['qty'] * line[1]['value']
        total_sales += line[0]['qty'] * (line[0]['value']+line[1]['value'])

        report.append(row_str.format(line[0]['journal'],
                                     line[0]['description'],
                                     line[0]['qty'],
                                     round(line[0]['value'], 2),
                                     round(line[1]['value'], 2),
                                     round(line[0]['qty'] * (line[0]['value'] + line[1]['value']), 2)))

    report.append(hl)
    report.append("|{:<40}  {:>3}|{:>10}|{:>10}|{:>10}|\n".format(
        "Totals", "", round(total_exvat, 2), round(total_vat, 2), round(total_sales, 2)))
    report.append(hl)
    return ''.join(report)


def client_invoice(client, me):
    curr_invoice_nr = document_id()
    report = []

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
                     "WHERE ecn.entity.code = '{}';".format(me))[0]

    header_line = '{:<30}     {:^15}     {:>25}\n'

    date = datetime.datetime.now()
    name = normalise_alias(row['first_name'], row['last_name'], row['company'])
    address = replace_value(row['physical_address'], replace_value(row['postal_address'], ''))

    street, town, zip_code = address.split(', ') if address else ('', '', '')

    report.append((header_line * 5 + "\n\n").format(name, "", "",
                                                    street, "", 'Code: {}'.format(row['code']),
                                                    town, "", "",
                                                    zip_code, "", "",
                                                    "VAT: " + replace_value(row['vat'], ''), '', ''))
    # </editor-fold>
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
                     "WHERE ecn.entity.code = '{}';".format(client))[0]

    name = normalise_alias(row['first_name'], row['last_name'], row['company'])
    address = replace_value(row['physical_address'], replace_value(row['postal_address'], ''))
    street, town, zip_code = address.split(', ') if address else ('', '', '')

    report.append((header_line * 5 + "\n\n").format(name, "", "",
                                                    street, "", 'Code: {}'.format(row['code']),
                                                    town, "", "",
                                                    zip_code, "", "",
                                                    "VAT: " + replace_value(row['vat'], ''), '', ''))
    report.append('\n')
    # </editor-fold>
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
    report.append(
        "|{:^10}|{:^30}|{:^3}|{:^10}|{:^10}|{:^10}|".format("Code", "Service", "Qty", "Unit", "VAT", "Subtotal"))
    report.append(hl)

    # rename these accordingly
    accounts = CONN.stmt()('SELECT')('id', 'name', 'owner')('FROM')('account')()

    ledger_a = accounts.filter(o(owner=client, name='Supplier Control'))[0]['id']
    ledger_b = accounts.filter(o(owner=me, name='Customer Control'))[0]['id']
    ledger_c = accounts.filter(o(owner=client, name='VAT Control'))[0]['id']
    ledger_d = accounts.filter(o(owner=me, name='VAT Control'))[0]['id']

    row_str = '|{:<10}|{:<30}|{:>3}|{:>10}|{:>10}|{:>10}|'
    total_exvat, total_vat, total_sales = 0, 0, 0
    ledgers = []
    for row in result:
        ledgers.append(ledger(row['sales_price'],
                              row['description'],
                              ledger_a))
        ledgers.append(ledger(row['sales_price'] * -1,
                              row['description'],
                              ledger_b))
        ledgers.append(ledger(row['sales_price'] * VAT_RATE,
                              "VAT on " + row['description'],
                              ledger_c))
        ledgers.append(ledger(row['sales_price'] * -VAT_RATE,
                              "VAT on " + row['description'],
                              ledger_d))

        total_exvat += row['qty'] * row['sales_price']
        total_vat += row['qty'] * row['sales_price'] * VAT_RATE
        total_sales += row['qty'] * row['sales_price'] * (1 + VAT_RATE)

        report.append(row_str.format(row['code'],
                                     row['description'],
                                     row['qty'],
                                     round(row['sales_price'], 2),
                                     round(row['sales_price'] * VAT_RATE, 2),
                                     round(row['qty'] * row['sales_price'] * (1 + VAT_RATE), 2)))
    if len(ledgers) > 0:
        journal = journal_entry(str(date), 'Tax Invoice Nr.{}'.format(curr_invoice_nr), *ledgers)
        if journal is not None:
            CONN.query('INSERT INTO {}.tax_invoice (code, reseller, client, journal)'.format(DB_NAME),
                       (curr_invoice_nr, me, client, journal))

            # call the update functions when applicable
            CONN.update()
            CONN.commit()

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
    result = CONN.stmt()('SELECT')('code')('FROM')('entity')()
    for row in result.rows():
        invoice = client_invoice(row['code'], "ecn001")
        if invoice[1] > 0 or PRINT_ZEROES:
            report.append(invoice[0])
    return report


if __name__ == '__main__':
    print(create_invoice('gbg001', 'ecn001'))
