import pandas as pd
import pytest
from data_processing.data_cleaning import clean_data


def test_clean_data():
    # Example will null data
    data = pd.DataFrame({
        'Open': [150, None, 155],
        'Close': [152, 153, 156]
    })
    cleaned_data = clean_data(data)
    assert cleaned_data.isnull().sum().sum() == 0  # No value should be null
    assert 'Close' in cleaned_data.columns  # 'Close' column should exist

