from data_analysis.analysis import analyze_stock_performance, find_correlations
from data_analysis.visualization import plot_stock_data, plot_volume_trends
from data_ingestion.extract_financial_data import extract_data_yahoo
from data_ingestion.web_scraping import *
from data_processing.data_cleaning import clean_data, convert_date_format
from data_processing.data_transformation import transform_data
from data_storage.database import connect_to_db, insert_data, get_all_transactions, create_tables
from pyspark.sql.functions import col, count, when


def main():
    print("Retrieving financial data\n")
    apple_data = extract_data_yahoo('AAPL')

    if apple_data.empty:
        print("Error : could not retrieve the data")
        return

    print(f"Extracted financial data :\n{apple_data.head()}")

    print("\nRetrieving financial news\n")
    news_url = 'https://finance.yahoo.com/quote/AAPL/news/'
    news_headlines = scrape_financial_news(news_url)
    print("Apple news :\n")
    for headline in news_headlines:
        print(f"- {headline}")

    indicators_url = 'https://finance.yahoo.com/quote/AAPL/key-statistics/'
    economic_indicators = scrape_economic_indicators(indicators_url)
    print("Economic indicators :\n")
    for indicator in economic_indicators.keys():
        print(indicator, " : ", economic_indicators[indicator])

    print("\nCleaning data\n")
    apple_data_cleaned = clean_data(apple_data)
    print(apple_data_cleaned)

    print("\nTransform data\n")
    apple_data_spark = transform_data(apple_data_cleaned)
    apple_data_spark.show(10)

    print("\nStorage in database\n")
    create_tables()
    conn = connect_to_db()
    insert_data(conn, apple_data_spark, 'apple_stock_data')
    get_all_transactions()
    conn.close()

    print("\nData analysis\n")
    apple_data_pandas = apple_data_spark.select("*").toPandas()
    print(analyze_stock_performance(apple_data_pandas))
    print(find_correlations(apple_data_pandas))

    print("\nData visualization\n")
    plot_stock_data(apple_data_pandas)
    plot_volume_trends(apple_data_pandas)


if __name__ == "__main__":
    main()
