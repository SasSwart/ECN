import decimal

from conditional import AS_SQL, AS_PYE
from factory import Factory
from datetime import datetime
from operator import itemgetter
from itertools import filterfalse
from mysql import connector
from collections import defaultdict
from defaults import U_NAME, P_WORD, H_NAME, DB_NAME, multi_replace


class _SQLAssembler(Factory):
    def __init__(self, conn):
        super(_SQLAssembler, self).__init__(';')
        self.conn = conn
        self.bin = []

    def halt(self, execute=False):
        stmt = ' '.join(self.loci) + ';'
        if execute:
            if self.bin is None:
                return self.conn.query(stmt)
            else:
                data, self.bin = self.bin, None
                return self.conn.query(stmt, data)
        return stmt


def _sql_assembler(conn):
    assembler = _SQLAssembler(conn)

    def _raise(x, funcs):
        if x.path[-1] not in funcs:
            raise SyntaxError('expected preceding {}, received {}'.format(' | '.join(funcs), x.path[-1]))

    @assembler(lambda x: _raise(x, ['START']), 'SELECT')
    def select_(*attributes):
        clause = 'SELECT columns'
        return clause.replace('columns', '{}').format(', '.join(attributes))

    @assembler(lambda x: _raise(x, ['START']), 'DELETE')
    def delete_(*attributes):
        clause = 'DELETE columns'
        return clause.replace('columns', '{}').format(', '.join(attributes) if attributes else '\b')

    @assembler(lambda x: _raise(x, ['SELECT', 'DELETE']), 'FROM')
    def from_(*tables):
        clause, table_name_format = 'FROM table_names', '{}.{}'.format(conn.db_name, '{}')
        return clause.replace('table_names', '({})').format(', '.join(table_name_format.format(x) for x in tables))

    @assembler(lambda x: _raise(x, ['FROM']), 'WHERE')
    def where_(condition):
        clause = 'WHERE condition'
        return clause.replace('condition', '{}').format(condition.x(AS_SQL))

    @assembler(lambda x: _raise(x, ['FROM', 'WHERE']), 'GROUP_BY')
    def group_by_(*pivots):
        clause = multi_replace('GROUP BY (column1, column2, ...) ASC|DESC',
                               {'(column1, column2, ...)': '({})', 'ASC|DESC': ''})
        pairs = [(pivots[i], pivots[i + 1]) for i in range(len(pivots))]
        return clause.format(', '.join(['{} {}'.format(attribute, direction) for attribute, direction in pairs]))

    @assembler(lambda x: _raise(x, ['FROM', 'WHERE']), 'ORDER_BY')
    def order_by_(*pivots):
        clause = multi_replace('ORDER BY (column1, column2, ...) ASC|DESC',
                               {'(column1, column2, ...)': '({})', 'ASC|DESC': ''})
        pairs = [(pivots[i], pivots[i + 1]) for i in range(len(pivots))]
        return clause.format(', '.join(['{} {}'.format(attribute, direction) for attribute, direction in pairs]))

    @assembler(lambda x: _raise(x, ['START']), 'INSERT_INTO')
    def insert_into_(table):
        clause = 'INSERT INTO table_name'
        return clause.replace('table_name', '{}.{}').format(conn.db_name, table)

    @assembler(lambda x: _raise(x, ['INSERT_INTO']), 'COLUMNS')
    def columns_(*attributes):
        clause = '(column1, column2, ...)'
        return clause.replace('(column1, column2, ...)', '({})').format(', '.join(attributes))

    @assembler(lambda x: _raise(x, ['COLUMNS']), 'VALUES', False)
    def values_(*values):
        assembler.bin.extend(values)

    assembler.start()
    return assembler


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

        self._conn = connector.connect(user=username,
                                       password=password,
                                       host=hostname)
        self._cursor = self._conn.cursor()

        self._prepared_stmt = _sql_assembler(self)

        self._to_execute = defaultdict(list)

    def stmt(self):
        return self._prepared_stmt

    def commit(self):
        self._conn.commit()

    def clear(self):
        self._to_execute.clear()

    def update(self):
        row_ids = [self.rep_query(stmt, values) for stmt, values in self._to_execute.items()]
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
            return _ResultSet(self,
                              [list(map(type_norm, row)) for row in self._cursor.fetchall()],
                              {name: index for index, name in enumerate(self._cursor.column_names)})
        self._to_execute[stmt].extend(values)

    def rep_query(self, stmt, values):
        stmt = '{} VALUES ({});'.format(stmt, ', '.join(['%s'] * len(values)))
        self._cursor.executemany(stmt, values)
        return self._cursor.getlastrowid()


CONN = Connection(username=U_NAME,
                  password=P_WORD,
                  hostname=H_NAME,
                  db_name=DB_NAME)

if __name__ == '__main__':
    thing = CONN.stmt() \
        ('SELECT')('name', 'service') \
        ('FROM')('clients')

    print('path:', thing.path)
    print('loci:', thing.loci)
    print('logs:', thing.logs)
    print('dump:', thing.dump)
