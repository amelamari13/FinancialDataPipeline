import matplotlib.pyplot as plt


def plot_data(df):
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    plot_stock_data(axs[0, 0], df)
    plot_volume_trends(axs[0, 1], df)
    plot_volatility(axs[1, 0], df)
    plot_correlation(axs[1, 1], df)

    # Hide last figure
    #axs[1, 1].axis('off')

    plt.tight_layout()
    plt.show()


def plot_stock_data(ax, df):
    ax.plot(df.index, df['Close'], marker='o', linestyle='-')
    ax.set_title('Stock Price Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.grid(True)


def plot_volume_trends(ax, df):
    ax.bar(df.index, df['Volume'], color='skyblue')
    ax.set_title('Transaction Volume Trends')
    ax.set_xlabel('Date')
    ax.set_ylabel('Volume')
    ax.grid(True)


def plot_volatility(ax, df):
    ax.hist(df['Daily_Return'], bins=30, alpha=0.7, color='blue')
    ax.set_title('Daily Returns')
    ax.set_xlabel('Daily Returns (%)')
    ax.set_ylabel('Frequency')
    ax.grid(axis='y', alpha=0.75)


def plot_correlation(ax, df):
    ax.scatter(df['Volume'], df['Close'], alpha=0.5)
    ax.set_title('Correlation between Volume and Stock Price')
    ax.set_xlabel('Volume')
    ax.set_ylabel('Stock Price')
    ax.grid(True)