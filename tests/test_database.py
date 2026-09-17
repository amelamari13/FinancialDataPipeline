import pytest
import sqlite3
from pyspark.sql import SparkSession
from data_storage.database import insert_data


@pytest.fixture
def setup_database():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Create table for the test
    cursor.execute('''
        CREATE TABLE apple_stock_data (
            id INTEGER PRIMARY KEY,
            ticker TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()

    yield conn

    conn.close()


def test_insert_data(setup_database):
    conn = setup_database

    spark = SparkSession.builder \
        .appName("Test") \
        .master("local[*]") \
        .getOrCreate()

    data = [(1, 'AAPL', 150.0)]
    columns = ['id', 'ticker', 'price']
    df = spark.createDataFrame(data, schema=columns)

    insert_data(conn, df, 'apple_stock_data')

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apple_stock_data")
    retrieved_data = cursor.fetchall()

    assert len(retrieved_data) == 1
    assert retrieved_data[0] == (1, 'AAPL', 150.0)


def test_create_tables_and_get_all_stock_data_round_trip(tmp_path, monkeypatch):
    """Regression test for the bug where create_tables() built a 'transactions'
    table that insert_data() never wrote to, so get_all_stock_data() (formerly
    get_all_transactions()) always returned an empty list.
    """
    import os
    from data_storage import database

    db_path = tmp_path / "test_financial_data.db"
    monkeypatch.chdir(tmp_path)

    # connect_to_db() uses a relative path by default; make sure it points here
    monkeypatch.setattr(database, 'connect_to_db', lambda db_name='test_financial_data': sqlite3.connect(db_path))

    database.create_tables()

    spark = SparkSession.builder \
        .appName("TestCreateTables") \
        .master("local[*]") \
        .getOrCreate()

    data = [(1, 'AAPL', '2024-01-01', 170.0, 172.0, 169.0, 171.0, 1000, 0.0, 0.0, 0.5, 171.0, 0, 1)]
    columns = [
        'id', 'Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Dividends', 'Stock Splits', 'Daily_Return', '7_Day_Moving_Avg',
        'HighVolatility', 'Above_Moving_Avg',
    ]
    df = spark.createDataFrame(data, schema=columns)

    conn = database.connect_to_db()
    database.insert_data(conn, df)
    conn.close()

    rows = database.get_all_stock_data()

    assert len(rows) == 1
    assert rows[0][1] == 'AAPL'  # Symbol column
