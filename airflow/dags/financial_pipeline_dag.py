"""Airflow DAG orchestrating the financial data pipeline: extract >> transform >> load.

Each task calls a stage function from pipeline_tasks.py. Only small,
serializable values (symbol lists, a dict of file paths, a summary dict) are
passed between tasks through XCom — the actual data (raw CSVs, staging
parquet files, the final stock_data.csv/parquet) travels through the
filesystem, not through Airflow itself.
"""
import os
import sys
from datetime import datetime

from airflow.decorators import dag, task

# Make the project root importable (this file lives in airflow/dags/,
# two levels below the project root where pipeline_tasks.py lives).
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pipeline_tasks import STOCK_SYMBOLS, extract_step, transform_step, load_step  # noqa: E402


@dag(
    dag_id="financial_data_pipeline",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={"retries": 1},
)
def financial_data_pipeline():

    @task
    def extract():
        return extract_step(STOCK_SYMBOLS)

    @task
    def transform(symbols):
        return transform_step(symbols)

    @task
    def load(staging_paths):
        return load_step(staging_paths)

    load(transform(extract()))


financial_data_pipeline()
