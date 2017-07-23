
import decimal

from conditional import multi_replace, AS_SQL, AS_PYE
from factory import factory
from datetime import datetime
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


def _result(conn, column_names, values, type_norm):
    return _ResultSet(conn,
                      [list(map(type_norm, row)) for row in values],
                      {name: index for index, name in enumerate(column_names)})


"""
class _PreparedStatement(ControlledFactory):
    def __init__(self, conn):
        super(_PreparedStatement, self).__init__({
            'SELECT':   self._select,
            'FROM':     self._from,
            'WHERE':    self._where,
            'GROUP_BY': self._group_by,
            'ORDER_BY': self._order_by,
            'END':      self._end})
        self.conn = conn
        self.stmt = []

        self['SELECT'] = 'SELECT | FROM'
        self['FROM'] = 'WHERE | GROUP_BY | ORDER_BY | END'
        self['WHERE'] = 'GROUP_BY | ORDER_BY | END'
        self['GROUP_BY'] = 'ORDER_BY | END'
        self['ORDER_BY'] = 'END'
        self['END'] = 'END'

    def _select(self, *attributes):
        clause = 'SELECT columns'
        self.stmt.append(clause.replace('columns', '{}').format(', '.join(attributes)))
        return self

    def _from(self, *tables):
        clause = 'FROM table_names'
        f_str = '{}.{}'.format(self.conn.db_name, '{}')
        self.stmt.append(clause.replace('table_names', '({})').format(', '.join(f_str.format(x) for x in tables)))
        return self

    def _where(self, condition):
        clause = 'WHERE condition'
        self.stmt.append(clause.replace('condition', '{}').format(condition.x(AS_SQL)))
        return self

    def _group_by(self, direction, *attributes):
        clause = 'GROUP BY (column1, column2, ...) ASC|DESC'
        self.stmt.append(_multi_replace(clause, {'(column1, column2, ...)': '({})',
                                                 'ASC|DESC': '{}'}).format(', '.join(attributes), direction))
        return self

    def _order_by(self, direction, *attributes):
        clause = 'ORDER BY (column1, column2, ...) ASC|DESC'
        self.stmt.append(_multi_replace(clause, {'(column1, column2, ...)': '({})',
                                                 'ASC|DESC': '{}'}).format(', '.join(attributes), direction))
        return self

    def _end(self, execute=True):
        stmt = ' '.join(self.stmt) + ';'
        self.stmt.clear()
        self.reset()
        if execute:
            return self.conn.query(stmt)
        return stmt
"""


class _PreparedStatement(object):
    def __init__(self, conn):
        self._conn = conn
        self._bin = None
        self._build()

    def _build(self):
        def select_(*attributes):
            clause = 'SELECT columns'
            return clause.replace('columns', '{}').format(', '.join(attributes))

        def from_(*tables):
            clause = 'FROM table_names'
            f_str = '{}.{}'.format(self._conn.db_name, '{}')
            return clause.replace('table_names', '({})').format(', '.join(f_str.format(x) for x in tables))

        def where_(condition):
            clause = 'WHERE condition'
            return clause.replace('condition', '{}').format(condition.x(AS_SQL))

        def group_by_(direction, *attributes):
            clause = 'GROUP BY (column1, column2, ...) ASC|DESC'
            return multi_replace(clause, {'(column1, column2, ...)': '({})',
                                          'ASC|DESC': '{}'}).format(', '.join(attributes), direction)

        def order_by_(direction, *attributes):
            clause = 'ORDER BY (column1, column2, ...) ASC|DESC'
            return multi_replace(clause, {'(column1, column2, ...)': '({})',
                                          'ASC|DESC': '{}'}).format(', '.join(attributes), direction)

        def insert_into_(table):
            clause = 'INSERT INTO table_name'
            return clause.replace('table_name', '{}.{}').format(self._conn.db_name, table)

        def columns_(*attributes):
            clause = '(column1, column2, column3, ...)'
            return clause.replace('(column1, column2, column3, ...)', '({})').format(', '.join(attributes))

        def values_(values):
            self._bin = values
            return ''

        def end_(stack, execute=True):
            stmt = ' '.join(stack) + ';'
            if execute:
                if self._bin is None:
                    return self._conn.query(stmt)
                data = self._bin
                self._bin = None
                return self._conn.query(stmt, data)
            return stmt

        func_map = {
            'SELECT':   select_,
            'FROM':     from_,
            'WHERE':    where_,
            'GROUP_BY': group_by_,
            'ORDER_BY': order_by_,

            'INSERT_INTO': insert_into_,
            'COLUMNS':     columns_,
            'VALUES':      values_
        }
        ctrl_map = {
            'SELECT':   'FROM',
            'FROM':     'WHERE | GROUP_BY | ORDER_BY',
            'WHERE':    'GROUP_BY | ORDER_BY',
            'GROUP_BY': 'ORDER_BY',
            'ORDER_BY': 'NONE',

            'INSERT_INTO': 'COLUMNS | VALUES',
            'COLUMNS':     'VALUES',
            'VALUES':      'NONE'
        }
        self._factory = factory(func_map, ctrl_map, [], end_)

    def start(self):
        return self._factory()


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

        self._prepared_stmt = _PreparedStatement(self)

        self.to_execute = []

    def stmt(self):
        return self._prepared_stmt.start()

    # def insert(self, attributes, table, values):
    #     self.rep_query('INSERT INTO {}.{} ({})'.format(self.db_name, table, ', '.join(attributes)), values)

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
    pass
