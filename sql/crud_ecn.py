import mysql.connector


def connect(user, password, database, host='127.0.0.1'):
    return mysql.connector.connect(user=user, password=password, host=host)


def new_database(name='ecn'):
    conn = connect('root', 'Hunt!ngSpr!ngbuck123', 'ecn')
    cur = conn.cursor()
    cur.execute("USE `ecn`;")
    cur.execute("SHOW TABLES;")

    row = cur.fetchone()

    while row is not None:
        print(row)
        row = cur.fetchone()