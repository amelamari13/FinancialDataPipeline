import sqlite3


def connect_to_db(db_name='financial_data'):
    conn = sqlite3.connect(db_name)
    return conn


def create_tables():
    conn = connect_to_db()
    cur = conn.cursor()

    # Création de la table avec les nouvelles colonnes
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_symbol TEXT,
            transaction_date TEXT,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            adjusted_close REAL,
            vwap REAL,
            percentage_change REAL,
            volume INTEGER
        )
    ''')

    conn.commit()
    conn.close()


def insert_data(conn, df_spark, table_name):
    df_pandas = df_spark.toPandas()
    df_pandas.to_sql(table_name, conn, if_exists='append', index=False)


def get_all_transactions():
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM transactions')
    rows = cur.fetchall()

    conn.close()
    return rows

