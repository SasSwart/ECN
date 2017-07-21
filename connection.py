
import decimal

from node import o, AS_SQL, AS_PYE
from operator import itemgetter
from mysql import connector


"""
from collections import defaultdict


def replace_strs(s, replacements):
    substrs = sorted(replacements, key=len, reverse=True)
    regexp = re.compile('|'.join(map(re.escape, substrs)))
    return regexp.sub(lambda match: replacements[match.group(0)], s)


def where(as_str=False, term=None, **conds):
    def check(row):
        return eval(replace_strs(and_(term, **conds), {'=': '==', "'~": "row['", '~': "']"}))
    if term is None:
        return where(as_str, and_(**conds))
    if as_str:
        return 'WHERE {}'.format(replace_strs(and_(term, **conds), {"'~": '', '~': '', 'or': 'OR', 'and': 'AND'}))
    return check


def _join(operator, relation, *terms, **conds):
    a, b = (' {} '.format(operator)).join(terms), ' and '.join("'~{}~ {} {}".format(k, relation, v) for k, v in conds.items())
    return '{} {} {}'.format(a, operator, b) if a and b else a + b


def and_(*terms, **conds):
    return _join('and', '=', *terms, **conds)


def or_(*terms, **conds):
    return _join('or', '=', *terms, **conds)


def lt_(**conds):
    return _join('or', '<', **conds)


def nest(x):
    return '({})'.format(x)
"""


class ResultSet(object):
    def __init__(self, conn, column_names, data, type_norm):
        self.conn = conn
        self.result = [list(map(type_norm, row)) for row in data]
        self.keymap = {name: index for index, name in enumerate(column_names)}

    def row(self, index):
        if 0 <= index < len(self.result):
            return {k: v for k, v in zip(self.keymap.keys(), self.result[index])}
        return None

    def rows(self):
        for row in self.result:
            yield {name: row[index] for name, index in self.keymap.items()}

    def filter(self, where, order=None):
        # magic!
        def check(**kwargs):
            return eval(where)
        filtered = [row for row in self.rows() if check(**row)]
        if order is None:
            return filtered if len(filtered) > 1 else filtered[0]
        order, direction = order
        filtered = sorted(filtered, key=itemgetter(*order), reverse=direction)
        return filtered if len(filtered) > 1 else filtered[0]


class Connection(object):
    def __init__(self, username, password, hostname, db_name):
        self.db_name = db_name
        self.conn = connector.connect(user=username,
                                      password=password,
                                      host=hostname)
        self.cursor = self.conn.cursor()
        self.to_execute = []

    def select(self, attributes, tables, where=None, order=None):
        from_str = ', '.join('{}.{}'.format(self.db_name, table) for table in tables)
        query_str = 'SELECT {} FROM {}'.format(', '.join(attributes), self.db_name, from_str)
        if where is not None:
            query_str = '{} WHERE {}'.format(query_str, where)
        if order is None:
            return self.query('{};'.format(query_str))
        order, direction = order
        return self.query('{} ORDER BY ({}) {};'.format(query_str, ', '.join(order), 'ASC' if direction else 'DESC'))

    def insert(self, attributes, table, values):
        self.rep_query('INSERT INTO {}.{} ({})'.format(self.db_name, table, ', '.join(attributes)), values)

    def commit(self):
        self.conn.commit()

    def clear(self):
        self.to_execute.clear()

    def update(self):
        row_ids = []
        for stmt, values, dependent in self.to_execute:
            if dependent is not None:
                index, when = dependent
                values = [v.insert(index, row_ids[when]) for v in values]
            row_ids.append(self.rep_query(stmt, values))
        self.clear()
        return row_ids

    def query(self, stmt, values=None, dependent=None):
        def type_norm(x):
            if isinstance(x, decimal.Decimal):
                return float(x)
            return x

        if values is None:
            self.cursor.execute(stmt)
            return ResultSet(self, self.cursor.column_names, self.cursor.fetchall(), type_norm)
        self.to_execute.append((stmt, values, dependent))
        return None

    def rep_query(self, stmt, values):
        self.cursor.executemany('{} VALUES ({});'.format(stmt, ', '.join(['%s'] * len(values[0]))), values)
        return self.cursor.getlastrowid()
