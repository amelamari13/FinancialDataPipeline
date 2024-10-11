import matplotlib.pyplot as plt


def plot_stock_data(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['Close'], marker='o', linestyle='-')
    plt.title('Stock Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True)
    plt.show()


def plot_volume_trends(df):
    plt.figure(figsize=(10, 5))
    plt.bar(df.index, df['Volume'], color='skyblue')
    plt.title('Transaction volume trends')
    plt.xlabel('Date')
    plt.ylabel('Volume')
    plt.grid(True)
    plt.show()