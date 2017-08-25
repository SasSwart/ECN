
from defaults import normalise_alias, replace_value, literal
from conditional import o
from connection import CONN


DEFAULT_REPORT = ("SELECT\n"
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

CLIENT_TOTALS = ("SELECT\n"
                 "    service.description,\n"
                 "    sum(cost_price*subscription.qty) as total_cost,\n"
                 "    sum(sales_price*subscription.qty) as total_sales,\n"
                 "    sum(subscription.qty) as total_qty,\n"
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
                 "GROUP BY entity.code;")


def default_report(title, where, order=('name DESC', 'sales_price DESC')):
    hl = '-' * 89
    report = [title, '{:^30} {:^3} {:^10} {:^10} {:^30}'.format('Description', 'Qty', 'Cost', 'Sales', 'Client'), hl]

    row_str = '|{:<30}|{:^3}|{:>10}|{:>10}|{:>30}|'
    total_cost, total_sales, total_qty = 0, 0, 0
    for row in CONN.query(DEFAULT_REPORT).\
            merge('name', normalise_alias, 'first_name', 'last_name', 'company').refine(where).order_by(*order):
        cost_price = row['cost_price'] * row['qty']
        sales_price = row['sales_price'] * row['qty']

        total_cost += cost_price
        total_sales += sales_price
        total_qty += row['qty']

        report.append(row_str.format(row['description'], row['qty'], cost_price, sales_price, row['name']))
    report.append(hl)
    report.append(' {:<30} {:^3} {:>10} {:>10}'.format('Total', total_qty, total_cost, total_sales))
    return '\n'.join(report)


def internet_solutions_domain():
    print(default_report('IS Domain Reconciliation',
                         o(type=literal('domain'),
                           supplier=literal('is0001'))))


def internet_solutions_mobile():
    print(default_report('IS Mobile Reconciliation',
                         o(type=literal('mobile'),
                           supplier=literal('is0001'))))


def internet_solution_adsl():
    print(default_report('IS Per Account Reconciliation',
                         o(type=(literal('peracc'), literal('uncapped')),
                           supplier=literal('is0001'))))
    print()
    print(default_report('IS Per GB Reconciliation',
                         o(type=literal('pergb'),
                           supplier=literal('is0001'))))


def axxess():
    print(default_report('Axxess Reconciliation',
                         o(supplier=literal('axx001'))))


def client_totals():
    hl = "-" * 54
    report = ["Client Totals", " {:^30} {:^10} {:^10}".format("Client", "Cost", "Sales"), hl]

    total_cost, total_sales, total_qty = 0, 0, 0
    for row in CONN.query(CLIENT_TOTALS).merge('name', normalise_alias, 'first_name', 'last_name', 'company'):
        total_cost += replace_value(row['total_cost'], 0)
        total_sales += replace_value(row['total_sales'], 0)
        total_qty += replace_value(row['total_qty'], 0)

        report.append("|{:<30}|{:>10}|{:>10}|".format(row['name'], row['total_cost'], row['total_sales']))
    report.append(hl)
    report.append(" {:<30} {:>10} {:>10}".format("Total", total_cost, total_sales))
    print('\n'.join(report))


if __name__ == '__main__':
    # axxess()

    # internet_solution_adsl()

    # internet_solutions_domain()

    # internet_solutions_mobile()

    client_totals()
    pass
