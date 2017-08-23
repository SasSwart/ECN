
from defaults import multi_replace, multi_reformat


BACKEND_FORMAT = ('(\$)(?P<var>[a-zA-Z]+)',
                  '(\#)(?P<const>\w+)')

SQL_FORMATTER = {'var': lambda x: x,
                 'const': lambda x: '{}'.format(x) if x.isalpha() else x}
SQL_REPLACEMENTS = {'EQ': '=',
                    'NE': '!=',
                    'LT': '<',
                    'GT': '>',
                    'LE': '<=',
                    'GE': '>=',
                    'and': 'AND',
                    'or': 'OR'}

AS_SQL = (SQL_FORMATTER, SQL_REPLACEMENTS)

PYE_FORMATTER = {'var': lambda x: x,
                 'const': lambda x: '{}'.format(x) if x.isalpha() else x}
PYE_REPLACEMENTS = {'EQ': '==',
                    'NE': '!=',
                    'LT': '<',
                    'GT': '>',
                    'LE': '<=',
                    'GE': '>=',
                    'AND': 'and',
                    'OR': 'or'}

AS_PYE = (PYE_FORMATTER, PYE_REPLACEMENTS)


def o(*args, **kwargs):
    l_args, l_kwargs = len(args), len(kwargs)
    assert l_args + l_kwargs == max(l_args, l_kwargs), ('simultaneous anonymous and aliased'
                                                        'assignment not implemented')

    if kwargs:
        args = _close(' and '.join(
            _close(' or '.join(_relate(k, i) for i in v)) if isinstance(v, tuple) else _relate(k, v)
            for k, v in kwargs.items() if v is not None))
        return _ConditionalClause(args)
    return _ConditionalClause(*args)


def _close(x):
    return '({})'.format(x)


def _relate(a, b, relation='EQ'):
    return '{1} {0} {2}'.format(relation, a, '{}'.format(b) if isinstance(b, str) else b)


class _ConditionalClause(object):
    def __init__(self, *expr):
        self.expr = list(expr)

    def x(self, format_by=None):
        if format_by is None:
            return ' '.join(map(str, self.expr))
        reform, replace = format_by
        return multi_reformat(multi_replace(' '.join(map(str, self.expr)), replace), BACKEND_FORMAT, reform)

    def _is_atom(self):
        return len(self.expr) == 1

    # UNARY OPERATORS

    def __iter__(self):
        pass

    def __pos__(self):
        pass

    # BINARY OPERATORS

    def __or__(self, other):
        if isinstance(other, _ConditionalClause):
            return o(_close(' OR '.join(self.expr + other.expr)))
        return

    def __and__(self, other):
        if isinstance(other, _ConditionalClause):
            return o(_close(' AND '.join(self.expr + other.expr)))
        return

    def __mul__(self, other):
        if isinstance(other, _ConditionalClause):
            return o(_close(' AND '.join(_relate(a, b, 'EQ') for a, b in zip(self.expr, other.expr))))
        return

    def __truediv__(self, other):
        if isinstance(other, _ConditionalClause):
            return o(_close(' AND '.join(_relate(a, b, 'NE') for a, b in zip(self.expr, other.expr))))
        return

    # BINARY RELATIONS

    def __lt__(self, other):
        if isinstance(other, _ConditionalClause):
            if self._is_atom() and other._is_atom():
                return o(_relate(self.expr[0], other.expr[0], 'LT'))
        return

    def __gt__(self, other):
        if isinstance(other, _ConditionalClause):
            if self._is_atom() and other._is_atom():
                return o(_relate(self.expr[0], other.expr[0], 'GT'))
        return

    def __le__(self, other):
        if isinstance(other, _ConditionalClause):
            if self._is_atom() and other._is_atom():
                return o(_relate(self.expr[0], other.expr[0], 'LE'))
        return

    def __ge__(self, other):
        if isinstance(other, _ConditionalClause):
            if self._is_atom() and other._is_atom():
                return o(_relate(self.expr[0], other.expr[0], 'GE'))
        return

    # MISCELLANEOUS

    def __str__(self):
        return str(self.expr)


if __name__ == '__main__':
    z = o('a', 'b', 'c') * o(1, 2, 3) & o(hello='goodbye')
    print(z.x(AS_PYE))
