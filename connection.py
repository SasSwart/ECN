import decimal

from conditional import AS_SQL, AS_PYE
from factory import factory
from datetime import datetime
from operator import itemgetter, getitem, setitem
from itertools import filterfalse
from mysql import connector
from defaults import U_NAME, P_WORD, H_NAME, DB_NAME, multi_replace


def _result(conn, column_names, values, type_norm):
    return _ResultSet(conn,
                      [list(map(type_norm, row)) for row in values],
                      {name: index for index, name in enumerate(column_names)})


class _PreparedStatement(object):
    def __init__(self, conn):
        self._conn = conn
        self._bin = None
        self._build()

    def _build(self):
        def select_(*attributes):
            clause = 'SELECT columns'
            return clause.replace('columns', '{}').format(', '.join(attributes))

        def delete_(*attributes):
            clause = 'DELETE columns'
            return clause.replace('columns', '{}').format(', '.join(attributes) if attributes else '\b')

        def from_(*tables):
            clause = 'FROM table_names'
            f_str = '{}.{}'.format(self._conn.db_name, '{}')
            return clause.replace('table_names', '({})').format(', '.join(f_str.format(x) for x in tables))

        def where_(condition):
            clause = 'WHERE condition'
            return clause.replace('condition', '{}').format(condition.x(AS_SQL))

        def group_by_(*pivots):
            clause = multi_replace('GROUP BY (column1 , column2, ...) ASC|DESC',
                                   {'(column1, column2, ...)': '({})',
                                    'ASC|DESC': ''})
            return clause.format(', '.join(['{} {}'.format(attribute, direction)
                                            for attribute, direction in zip(pivots[::2], pivots[1::2])]))

        def order_by_(*pivots):
            clause = multi_replace('ORDER BY (column1 , column2, ...) ASC|DESC',
                                   {'(column1, column2, ...)': '({})',
                                    'ASC|DESC': ''})
            return clause.format(', '.join(['{} {}'.format(attribute, direction)
                                            for attribute, direction in zip(pivots[::2], pivots[1::2])]))

        def insert_into_(table):
            clause = 'INSERT INTO table_name'
            return clause.replace('table_name', '{}.{}').format(self._conn.db_name, table)

        def columns_(*attributes):
            clause = '(column1, column2, ...)'
            return clause.replace('(column1, column2, ...)', '({})').format(', '.join(attributes))

        def values_(*values):
            self._bin = values
            return ''

        def end_(stack, execute=True):
            stmt = ' '.join(stack) + ';'
            if execute:
                if self._bin is None:
                    return self._conn.query(stmt)
                data, self._bin = self._bin, None
                return self._conn.query(stmt, data)
            return stmt

        func_map = {
            'SELECT': select_,
            'DELETE': delete_,
            'FROM': from_,
            'WHERE': where_,
            'GROUP_BY': group_by_,
            'ORDER_BY': order_by_,

            'INSERT_INTO': insert_into_,
            'COLUMNS': columns_,
            'VALUES': values_
        }
        ctrl_map = {
            'SELECT': 'FROM',
            'DELETE': 'FROM',
            'FROM': 'WHERE | GROUP_BY | ORDER_BY | NONE',
            'WHERE': 'GROUP_BY | ORDER_BY | NONE',
            'GROUP_BY': 'ORDER_BY | NONE',
            'ORDER_BY': 'NONE',

            'INSERT_INTO': 'COLUMNS',
            'COLUMNS': 'VALUES',
            'VALUES': 'NONE'
        }

        self._factory = factory(func_map, ctrl_map, [], end_)

    def start(self):
        return self._factory


class _ResultSet(object):
    def __init__(self, conn, result, keymap):
        self._conn = conn
        self._result = result

        self._keymap = keymap
        self._mapped = [{k: row[i] for k, i in self._keymap.items()} for row in self._result]

    def __len__(self):
        return len(self._result)

    def __getitem__(self, index):
        return self._mapped[index]

    def __iter__(self):
        for row in self._mapped:
            yield row

    def merge(self, name, blender, *attributes):
        splits = sorted([pair for pair in self._keymap.items() if pair[0] not in attributes], key=itemgetter(1))
        merges = [[row[k] for k, v in splits] + [blender(*(row[k] for k in attributes))] for row in self]
        splits.append((name, len(splits)))
        return _ResultSet(self._conn, merges, {name: new_i for new_i, (name, old_i) in enumerate(splits)})

    def refine(self, where):
        def check(**kwargs):
            return eval(where.x(AS_PYE), kwargs)
        filtered = [self._result[i][:] for i in range(len(self)) if check(**self._mapped[i])]
        return _ResultSet(self._conn, filtered, self._keymap.copy())

    def order_by(self, *attributes):
        def as_order(pair):
            a, b = pair.split(' ')
            return a, b == 'ASC'
        pairs, sort_pass = [as_order(pair) for pair in attributes], self._result[:]
        asc = [self._keymap[name] for name, direction in filter(itemgetter(1), pairs)]
        desc = [self._keymap[name] for name, direction in filterfalse(itemgetter(1), pairs)]
        if asc:
            sort_pass.sort(key=itemgetter(*asc), reverse=False)
        if desc:
            sort_pass.sort(key=itemgetter(*desc), reverse=True)
        return _ResultSet(self._conn, sort_pass, self._keymap.copy())

    def get_headers(self):
        return self._keymap.keys()


class Connection(object):
    def __init__(self, username, password, hostname, db_name):
        self.db_name = db_name
        self._conn = connector.connect(user=username, password=password, host=hostname)
        self._cursor = self._conn.cursor()
        self._prepared_stmt = _PreparedStatement(self)
        self._to_execute = []

    def stmt(self):
        return self._prepared_stmt.start()

    def commit(self):
        self._conn.commit()

    def clear(self):
        self._to_execute.clear()

    def update(self):
        row_ids = [self.rep_query(stmt, values) for stmt, values in self._to_execute]
        self.clear()
        return row_ids

    def query(self, stmt, values=None):
        def type_norm(x):
            # if x is None:
            #     return str(None)
            if isinstance(x, decimal.Decimal):
                return float(x)
            if isinstance(x, datetime):
                return str(x)
            return x
        if values is None:
            self._cursor.execute(stmt)
            return _result(self, self._cursor.column_names, self._cursor.fetchall(), type_norm)
        self._to_execute.append((stmt, [values]))
        return None

    def rep_query(self, stmt, values):
        self._cursor.executemany('{} VALUES ({});'.format(stmt, ', '.join(['%s'] * len(values[0]))), values)
        return self._cursor.getlastrowid()


CONN = Connection(username=U_NAME,
                  password=P_WORD,
                  hostname=H_NAME,
                  db_name=DB_NAME)

if __name__ == '__main__':
    for r in CONN.stmt()\
                ('SELECT')('*')\
                ('FROM')('subscription')\
                ().merge('_', ('{}_' * 3).format, 'client', 'code', 'service'):
        print(r)
