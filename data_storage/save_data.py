def _to_pandas(df):
    """Accept either a pandas DataFrame or a Spark DataFrame."""
    return df.toPandas() if hasattr(df, 'toPandas') else df


def save_data_to_parquet(df, file_path):
    pandas_df = _to_pandas(df)
    pandas_df.to_parquet(file_path, index=False)


def save_data_to_csv(df, file_path):
    pandas_df = _to_pandas(df)
    pandas_df.to_csv(file_path, index=False)
