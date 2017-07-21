
import re


BACKEND_FORMAT = ('(\$)(?P<var>[a-zA-Z]+)',
                  '(\#)(?P<const>\w+)')

SQL_FORMATTER = {'var': lambda x: x,
                 'const': lambda x: '\'{}\''.format(x) if x.isalpha() else x}
SQL_REPLACEMENTS = {'EQ': '=',
                    'LT': '<',
                    'GT': '>',
                    'LE': '<=',
                    'GE': '>=',
                    'and': 'AND',
                    'or': 'OR'}

AS_SQL = (SQL_FORMATTER, SQL_REPLACEMENTS)

PYE_FORMATTER = {'var': lambda x: x,
                 'const': lambda x: '\'{}\''.format(x) if x.isalpha() else x}
PYE_REPLACEMENTS = {'EQ': '==',
                    'LT': '<',
                    'GT': '>',
                    'LE': '<=',
                    'GE': '>=',
                    'AND': 'or',
                    'OR': 'or'}

AS_PYE = (PYE_FORMATTER, PYE_REPLACEMENTS)


def o(*args, **kwargs):
    l_args, l_kwargs = len(args), len(kwargs)
    assert l_args + l_kwargs == max(l_args, l_kwargs), ('simultaneous anonymous and aliased'
                                                        'assignment not implemented')
    if kwargs:
        args = _close(' and '.join(
            _close(' or '.join(_relate(k, i) for i in v)) if isinstance(v, tuple) else _relate(k, v)
            for k, v in kwargs.items()))
        return _ConditionalStatement(args)
    return _ConditionalStatement(*args)


def _close(x):
    return '({})'.format(x)


def _multi_replace(s, replacements):
    substrs = sorted(replacements, key=len, reverse=True)
    regexp = re.compile('|'.join(map(re.escape, substrs)))
    return regexp.sub(lambda match: replacements[match.group(0)], s)


def _multi_reformat(s, patterns, formatter):
    def reformat(key, value):
        return formatter[key](value)
    regexp = re.compile('|'.join('({})'.format(p) for p in patterns))
    return regexp.sub(lambda match: reformat(*[(k, v) for k, v in match.groupdict().items() if v is not None][0]), s)


def _relate(a, b, relation='EQ'):
    return '{1} {0} {2}'.format(relation, a, '\'{}\''.format(b) if isinstance(b, str) else b)


class _ConditionalStatement(object):
    def __init__(self, *expr):
        self.expr = list(expr)

    def u(self):
        self.expr = [_close(self.x())]
        return self

    def x(self, format_by=None):
        if format_by is None:
            return ' '.join(map(str, self.expr))
        replace, reform = format_by
        return _multi_reformat(_multi_replace(' '.join(map(str, self.expr)), replace), BACKEND_FORMAT, reform)

    def is_atom(self):
        return len(self.expr) == 1

    # UNARY OPERATORS

    def __iter__(self):
        pass

    def __pos__(self):
        pass

    # BINARY OPERATORS

    def __or__(self, other):
        if isinstance(other, _ConditionalStatement):
            return o(_close(' OR '.join(self.expr + other.expr)))
        return

    def __and__(self, other):
        if isinstance(other, _ConditionalStatement):
            return o(_close(' AND '.join(self.expr + other.expr)))
        return

    # BINARY RELATIONS

    def __lt__(self, other):
        if isinstance(other, _ConditionalStatement):
            if self.is_atom() and other.is_atom():
                return o(_relate(self.expr[0], other.expr[0], 'LT'))
        return

    def __gt__(self, other):
        if isinstance(other, _ConditionalStatement):
            if self.is_atom() and other.is_atom():
                return o(_relate(self.expr[0], other.expr[0], 'GT'))
        return

    def __le__(self, other):
        if isinstance(other, _ConditionalStatement):
            if self.is_atom() and other.is_atom():
                return o(_relate(self.expr[0], other.expr[0], 'LE'))
        return

    def __ge__(self, other):
        if isinstance(other, _ConditionalStatement):
            if self.is_atom() and other.is_atom():
                return o(_relate(self.expr[0], other.expr[0], 'GE'))
        return

    def __str__(self):
        return str(self.expr)


z = o(a=(1, 2, 3), c=2, d=4)
print(z.x(format_by=(PYE_REPLACEMENTS, PYE_FORMATTER)))
