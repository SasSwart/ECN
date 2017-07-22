
import hashlib


H_NAME = "192.168.0.33"
U_NAME = "root"
P_WORD = "Hunt!ngSpr!ngbuck123"

DB_NAME = 'ecn'

PAGE = (85, 58)

VAT_RATE = 0.14


def md5(f_name):
    hash_md5 = hashlib.md5()
    hash_md5.update(str(f_name).encode('utf-8'))
    return hash_md5.hexdigest()


def replace_value(value, alternate, unwanted=None):
    return alternate if value is unwanted else value


def normalise_alias(f_name, l_name, company):
    if company is None:
        return '{} {}'.format(replace_value(f_name, ''), replace_value(l_name, ''))
    return company
