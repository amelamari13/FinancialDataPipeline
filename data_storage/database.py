import sqlite3

STOCK_DATA_TABLE = 'stock_data'


def connect_to_db(db_name='financial_data.db'):
    conn = sqlite3.connect(db_name)
    return conn


def create_tables():
    """Create the table that insert_data() actually writes to.

    Bug fix: this used to create an unused 'transactions' table with a
    schema that never matched the data actually inserted by main.py
    (which goes into a table created on the fly by pandas.to_sql). This
    table now matches the real columns produced by the pipeline
    (see data_processing/data_transformation.py), plus the Symbol column
    added in main.py for multi-stock support.
    """
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS {STOCK_DATA_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Symbol TEXT,
            Date TEXT,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Volume INTEGER,
            Dividends REAL,
            "Stock Splits" REAL,
            Daily_Return REAL,
            "7_Day_Moving_Avg" REAL,
            HighVolatility INTEGER,
            Above_Moving_Avg INTEGER
        )
    ''')

    conn.commit()
    conn.close()


def insert_data(conn, df, table_name=STOCK_DATA_TABLE):
    """Accept either a pandas DataFrame or a Spark DataFrame."""
    df_pandas = df.toPandas() if hasattr(df, 'toPandas') else df
    df_pandas.to_sql(table_name, conn, if_exists='append', index=False)


def get_all_stock_data(table_name=STOCK_DATA_TABLE, limit=10):
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(f'SELECT * FROM {table_name} LIMIT ?', (limit,))
    rows = cur.fetchall()

    conn.close()
    return rows
