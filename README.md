# FinancialDataPipeline

*Update of the 2025 project.*

End-to-end financial data pipeline: extraction (Yahoo Finance + news scraping),
cleaning (Pandas), transformation (PySpark), storage (SQLite), export
(CSV/Parquet), orchestration (Airflow), and a Flask API that serves the results.

## Project structure

```
FinancialDataPipeline/
├── data_ingestion/          # Yahoo Finance extraction + web scraping
├── data_processing/         # Cleaning (Pandas) + transformation (PySpark)
├── data_storage/            # SQLite storage + CSV/Parquet export
├── data_analysis/           # Statistical analysis + visualization
├── api/
│   └── app.py                 # Flask API serving stock_data.csv
├── airflow/
│   └── dags/
│       └── financial_pipeline_dag.py   # DAG: extract >> transform >> load
├── pipeline_tasks.py         # The 3 pipeline stages (used by both main.py AND the DAG)
├── tests/
│   ├── test_data_ingestion.py
│   ├── test_data_procesing.py
│   ├── test_data_transformation.py
│   ├── test_database.py
│   ├── test_api.py
│   └── test_dag.py
├── main.py                   # Local pipeline run (without Airflow)
└── requirements.txt
```

## Data flow

```
Yahoo Finance (yfinance)
        ↓
extract_step   → data/raw/{symbol}.csv
        ↓
transform_step → data/staging/{symbol}.parquet (Pandas cleaning + PySpark transformation)
        ↓
load_step      → SQLite (financial_data.db, table stock_data) + stock_data.csv / stock_data.parquet
        ↓
api/app.py (Flask, reads stock_data.csv)
        ↓
GET /prices, GET /prices/<symbol>
```

`extract_step`, `transform_step`, and `load_step` (in `pipeline_tasks.py`) are the
single implementation of the three stages: `main.py` calls them directly for a
local run, and the Airflow DAG also calls them, each as a task
(`extract >> transform >> load`). No logic is duplicated between the two.

The API never re-runs the pipeline on demand: it reads the latest generated
`stock_data.csv` file. To refresh the data, re-run the pipeline (locally via
`main.py`, or via Airflow), then restart the API.

## Installation

**Prerequisites:**
- Python 3.10 (the pinned dependency versions in `requirements.txt`, e.g.
  `numpy~=1.21.6`, do not have wheels for Python 3.11+).
- Java 8 or 11 for PySpark. Newer versions (17, 22...) will make PySpark fail
  with `RuntimeError: Java gateway process exited before sending its port
  number` — set `JAVA_HOME` to point to a JDK 8/11 installation if you have a
  newer Java as your system default.
- On Windows, run the project from a short path without accented characters
  (e.g. `C:\dev\FinancialDataPipeline`) — PySpark's launch scripts can fail to
  build the classpath correctly on deep or non-ASCII paths.

```bash
pip install -r requirements.txt
```

## Run the pipeline locally (without Airflow)

```bash
python main.py
```

Processes the stocks defined in `STOCK_SYMBOLS` (default: AAPL, GOOGL, AMZN).

## Run the API

```bash
python api/app.py
```

By default, the API reads `stock_data.csv` at the project root. The path is
configurable via the `STOCK_DATA_CSV` environment variable (read in
`api/app.py`).

Note: `Flask` is pinned to `~=2.2.5` (not the more recent 3.x) because
`apache-airflow~=2.10.2` depends internally on `Flask<2.3` for its own web
server; installing both in the same environment requires this version.

### Endpoints

- `GET /prices`: all available data, across all stocks.
- `GET /prices/<symbol>`: data filtered for one stock (`symbol` is case
  insensitive). 400 if empty, 404 if no data found, 503 if the pipeline has
  never been run (file missing).

## Run the tests

```bash
pytest tests/ --ignore=tests/test_dag.py -v   # business logic tests, no Airflow needed
pytest tests/test_dag.py -v                    # requires apache-airflow installed
```

`test_data_ingestion.py` requires network access to Yahoo Finance.

## Run the pipeline with Airflow

The DAG (`airflow/dags/financial_pipeline_dag.py`) was verified to import and
parse correctly, with the right task structure (`extract >> transform >>
load`), using Airflow's `DagBag` and a dedicated test
(`tests/test_dag.py`) — see [Run the tests](#run-the-tests).

Actually running it end-to-end was not completed, for two environment reasons
worth documenting rather than hiding:

- **Apache Airflow does not officially support running natively on Windows**
  (its scheduler relies on Unix-specific mechanisms). The standard workaround
  is Docker or WSL.
- Running it via Docker Compose (the official
  `apache-airflow/docker-compose.yaml`) gets further: adding this project's
  Python dependencies via `_PIP_ADDITIONAL_REQUIREMENTS` (pandas, PySpark,
  yfinance...) lets the DAG import correctly. But PySpark isn't just a Python
  package — it's a Python interface to Spark, which runs on a JVM. The base
  Airflow image has no Java installed, so PySpark can be imported but fails
  as soon as it actually tries to start a Spark session (in the `transform`
  task), the same `Java gateway process exited` error this project's local
  Windows setup hit earlier (see the Prerequisites section above). Getting a
  fully working containerized setup would mean building a custom Airflow
  image with Java installed — treated here as a known next step, not yet
  done.

In short: this project's Airflow integration was taken as far as verifying the
DAG's correctness in isolation, not as far as a live scheduled run. `main.py`
remains the reliable way to actually run the pipeline locally.

## Known limitations

- Storage uses SQLite locally (`financial_data.db`); `apache-airflow`
  orchestrates the pipeline but remains optional for simple local use
  (`main.py` works on its own).