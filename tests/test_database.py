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
