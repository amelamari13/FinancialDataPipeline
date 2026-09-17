import pytest
from data_ingestion.extract_financial_data import extract_data_yahoo


def test_extract_data_yahoo():
    df = extract_data_yahoo('AAPL', period='1y')
    assert not df.empty, "Data should not be empty"
