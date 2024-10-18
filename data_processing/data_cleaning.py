import pandas as pd


def clean_data(df):
    df = df.dropna()  #delete missing values
    df = df.drop_duplicates()
    df = df.reset_index()
    return df


def convert_date_format(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column], format='%Y-%m-%d')
    return df
