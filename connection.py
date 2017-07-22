from datetime import datetime
import decimal

from conditional import o, _multi_replace, AS_SQL, AS_PYE
from operator import itemgetter
from mysql import connector

from defaults import *


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


def _result(conn, column_names, values, type_norm):
    return _ResultSet(conn,
                      [list(map(type_norm, row)) for row in values],
                      {name: index for index, name in enumerate(column_names)})


class _PreparedStatement(object):
    def __init__(self, conn):
        self.conn = conn
        self.keymap = {
            'SELECT': 0,
            'FROM': 1,
            'WHERE': 2,
            'GROUP_BY': 3,
            'ORDER_BY': 4
        }
        self.statement = [
            'SELECT columns',
            'FROM table_names',
            'WHERE condition',
            'GROUP BY (column1, column2, ...) ASC|DESC',
            'ORDER BY (column1, column2, ...) ASC|DESC'
        ]

    def _get(self, clause):
        return self.statement[self.keymap.get(clause, None)]

    def _set(self, clause, set_to):
        self.statement[self.keymap.get(clause, None)] = set_to

    def select(self, *attributes):
        self._set('SELECT', self._get('SELECT').replace('columns', '{}').format(', '.join(attributes)))
        return self._from

    def _from(self, *tables):
        def_str = '{}.{}'.format(self.conn.db_name, '{}')
        self._set('FROM', self._get('FROM').replace('table_names', '({})').format(', '.join(def_str.format(x) for x in tables)))
        return self._where

    def _where(self, *head):
        if not head:
            return self._x('WHERE')
        if head[0] is None:
            self._set('WHERE', '')
            return self._group_by
        self._set('WHERE', self._get('WHERE').replace('condition', '{}').format(head[0].x(AS_SQL)))
        return self._group_by

    def _group_by(self, *head):
        if not head:
            return self._x('GROUP_BY')
        if head[0] is None:
            self._set('GROUP_BY', '')
            return self._order_by
        groups, direction = head
        self._set('GROUP_BY', _multi_replace(self._get('GROUP_BY'),
                                             {'(column1, column2, ...)': '({})',
                                              'ASC|DESC':                 '{}'}).format(', '.join(groups),
                                                                                        direction))
        return self._order_by

    def _order_by(self, *head):
        if head:
            attributes, direction = head
            self._set('ORDER_BY', _multi_replace(self._get('ORDER_BY'),
                                                 {'(column1, column2, ...)': '({})',
                                                  'ASC|DESC':                 '{}'}).format(', '.join(attributes),
                                                                                            direction))
        return self._x(None)

    def _x(self, clause, execute=True):
        index = self.keymap.get(clause, len(self.keymap) + 1)
        self.statement[index:] = [''] * (len(self.keymap) - index)
        query_str = ' '.join(x for x in self.statement if x) + ';'
        return self.conn.query(query_str) if execute else query_str


class _ResultSet(object):
    def __init__(self, conn, result, keymap):
        self.conn = conn
        self.result = result
        self.keymap = keymap

    def __len__(self):
        return len(self.result)

    def __getitem__(self, index):
        if 0 <= index < len(self):
            return {k: self.result[index][i] for k, i in self.keymap.items()}
        return None

    def __iter__(self):
        for row in self.result:
            yield {k: row[i] for k, i in self.keymap.items()}

    def filter(self, where, order=None):
        def check(**kwargs):
            return eval(where.x(AS_PYE), kwargs)
        filtered = [self.result[i] for i, row in enumerate(self) if check(**row)]
        if order is None:
            return _ResultSet(self.conn, filtered.copy(), self.keymap.copy())
        order, direction = order
        return _ResultSet(self.conn, sorted(filtered, key=itemgetter(*order), reverse=direction), self.keymap.copy())


class Connection(object):
    def __init__(self, username, password, hostname, db_name):
        self.db_name = db_name
        self.conn = connector.connect(user=username,
                                      password=password,
                                      host=hostname)
        self.cursor = self.conn.cursor()
        self.to_execute = []

    def select(self, *attributes):
        return _PreparedStatement(self).select(*attributes)
        # from_str = ', '.join('{}.{}'.format(self.db_name, table) for table in tables)
        # query_str = 'SELECT {} FROM {}'.format(', '.join(attributes), from_str)
        # if where is not None:
        #     query_str = '{} WHERE {}'.format(query_str, where)
        # if order is None:
        #     return self.query('{};'.format(query_str))
        # order, direction = order
        # return self.query('{} ORDER BY ({}) {};'.format(query_str, ', '.join(order), 'ASC' if direction else 'DESC'))

    def insert(self, attributes, table, values):
        self.rep_query('INSERT INTO {}.{} ({})'.format(self.db_name, table, ', '.join(attributes)), values)

    def commit(self):
        self.conn.commit()

    def clear(self):
        self.to_execute.clear()

    def update(self):
        row_ids = [self.rep_query(stmt, values) for stmt, values in self.to_execute]
        self.clear()
        return row_ids

    def query(self, stmt, values=None):
        def type_norm(x):
            if isinstance(x, decimal.Decimal):
                return float(x)
            if isinstance(x, datetime):
                return str(x)
            return x

        if values is None:
            self.cursor.execute(stmt)
            return _result(self, self.cursor.column_names, self.cursor.fetchall(), type_norm)
        self.to_execute.append((stmt, values))
        return None

    def rep_query(self, stmt, values):
        self.cursor.executemany('{} VALUES ({});'.format(stmt, ', '.join(['%s'] * len(values[0]))), values)
        return self.cursor.getlastrowid()

if __name__ == '__main__':
    CONN = Connection(username=U_NAME,
                      password=P_WORD,
                      hostname=H_NAME,
                      db_name=DB_NAME)

    b = CONN.select('code, name, company')('some_table')(o(x=2, y=3))(('a', 'b'), 'ASC')()
    print(b)
