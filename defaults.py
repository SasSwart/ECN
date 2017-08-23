
import re
import hashlib

H_NAME = "192.168.0.33"
U_NAME = "root"
P_WORD = "Hunt!ngSpr!ngbuck123"

DB_NAME = 'ecn'

PAGE = (85, 58)

VAT_RATE = 0.14

QDATE_FORMAT = "yyyy-MM-dd"
DATE_FORMAT = ""


def md5(f_name):
    hash_md5 = hashlib.md5()
    hash_md5.update(str(f_name).encode('utf-8'))
    return hash_md5.hexdigest()


def replace_value(value, alternate, unwanted=None):
    return alternate if value is unwanted else value


def multi_replace(s, replacements):
    substrs = sorted(replacements, key=len, reverse=True)
    regexp = re.compile('|'.join(map(re.escape, substrs)))
    return regexp.sub(lambda match: replacements[match.group(0)], s)


def multi_reformat(s, patterns, formatter):
    def matcher(match):
        key, value = [(k, v) for k, v in match.groupdict().items() if v is not None][0]
        return formatter[key](value)
    regexp = re.compile('|'.join('({})'.format(p) for p in patterns))
    return regexp.sub(matcher, s)


def normalise_alias(f_name, l_name, company):
    if company is None:
        return '{} {}'.format(replace_value(f_name, ''), replace_value(l_name, ''))
    return company


def literal(s):
    if s[0] == '\'' or s[0] == '"':
        s = s[1:]
    if s[-1] == '\'' or s[-1] == '"':
        s = s[:-1]
    return '\'{}\''.format(s)