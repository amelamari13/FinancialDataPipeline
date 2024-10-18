def save_data_to_parquet(df, file_path):
    pandas_df = df.toPandas()
    pandas_df.to_parquet(file_path, index=False)


def save_data_to_csv(df, file_path):
    pandas_df = df.toPandas()
    pandas_df.to_csv(file_path, index=False)