def analyze_stock_performance(df):
    df['Daily_Return'] = df['Close'].pct_change()
    return df.describe()


def find_correlations(df):
    return df.corr()
