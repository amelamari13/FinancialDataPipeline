from data_ingestion.extract_financial_data import extract_data_yahoo
from data_ingestion.web_scraping import *


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


if __name__ == "__main__":
    main()
