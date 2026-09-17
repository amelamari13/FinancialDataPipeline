"""Pipeline stages, kept independent of any orchestrator.

Each function does one ETL stage (extract / transform / load) and hands off
to the next one through files on disk rather than in-memory objects, so that
Airflow tasks can pass simple, XCom-serializable values (paths, symbol lists)
between them instead of large Spark or pandas objects.
"""
import os

import pandas as pd
from pyspark.sql.functions import lit

from data_ingestion.extract_financial_data import extract_data_yahoo
from data_processing.data_cleaning import clean_data
from data_processing.data_transformation import transform_data
from data_storage.database import connect_to_db, create_tables, insert_data
from data_storage.save_data import save_data_to_csv, save_data_to_parquet

STOCK_SYMBOLS = ['AAPL', 'GOOGL', 'AMZN']
RAW_DIR = 'data/raw'
STAGING_DIR = 'data/staging'


def extract_step(symbols=None):
    """Download raw price history for each symbol and save it to data/raw/.

    Returns the list of symbols that were successfully extracted.
    """
    symbols = symbols or STOCK_SYMBOLS
    os.makedirs(RAW_DIR, exist_ok=True)

    extracted_symbols = []
    for symbol in symbols:
        raw_df = extract_data_yahoo(symbol)

        if raw_df.empty:
            print(f"No data for {symbol}, skipping")
            continue

        raw_df.to_csv(os.path.join(RAW_DIR, f"{symbol}.csv"))
        extracted_symbols.append(symbol)

    return extracted_symbols


def transform_step(symbols):
    """Clean and transform each symbol's raw data, save it to data/staging/.

    Returns a dict mapping each symbol to its staging parquet file path.
    """
    os.makedirs(STAGING_DIR, exist_ok=True)

    staging_paths = {}
    for symbol in symbols:
        raw_path = os.path.join(RAW_DIR, f"{symbol}.csv")
        raw_df = pd.read_csv(raw_path)

        cleaned_df = clean_data(raw_df)
        spark_df = transform_data(cleaned_df)
        spark_df = spark_df.withColumn("Symbol", lit(symbol))

        staging_path = os.path.join(STAGING_DIR, f"{symbol}.parquet")
        spark_df.toPandas().to_parquet(staging_path, index=False)
        staging_paths[symbol] = staging_path

    return staging_paths


def load_step(staging_paths):
    """Load each symbol's staged data into the database, and save the
    combined result as stock_data.csv / stock_data.parquet at the project root.

    Returns a small summary dict (not the data itself) so it stays
    XCom-friendly.
    """
    create_tables()
    conn = connect_to_db()

    combined_frames = []
    for symbol, path in staging_paths.items():
        df = pd.read_parquet(path)
        insert_data(conn, df, 'stock_data')
        combined_frames.append(df)

    conn.close()

    if not combined_frames:
        return {"rows_loaded": 0, "symbols": []}

    combined_df = pd.concat(combined_frames, ignore_index=True)
    save_data_to_csv(combined_df, 'stock_data.csv')
    save_data_to_parquet(combined_df, 'stock_data.parquet')

    return {"rows_loaded": len(combined_df), "symbols": list(staging_paths.keys())}
