import pandas as pd
import pytest
from data_processing.data_transformation import transform_data


def test_transform_data():
    data = pd.DataFrame({
        'Open': [150, 155, 160],
        'Close': [152, 158, 162],
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03']
    })
    transformed_data = transform_data(data)

    assert 'Daily_Return' in transformed_data.columns  # Daily_Return column should exist
    assert '7_Day_Moving_Avg' in transformed_data.columns  # 7_Day_Moving_Avg should exist
    assert transformed_data.count() > 0  # Dataframe should not be empty

