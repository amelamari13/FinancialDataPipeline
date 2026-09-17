from data_analysis.analysis import analyze_stock_performance, find_correlations
from data_analysis.visualization import plot_data
from data_ingestion.web_scraping import *
from pipeline_tasks import STOCK_SYMBOLS, extract_step, transform_step, load_step


def main():
    print("Retrieving financial data\n")
    extracted_symbols = extract_step(STOCK_SYMBOLS)

    if not extracted_symbols:
        print("Error : could not retrieve data for any symbol")
        return

    print(f"Extracted data for: {extracted_symbols}\n")

    print("Cleaning and transforming data\n")
    staging_paths = transform_step(extracted_symbols)

    print("Storing in database and saving to files\n")
    summary = load_step(staging_paths)
    print(f"Rows loaded: {summary['rows_loaded']} for symbols {summary['symbols']}\n")

    if summary['rows_loaded'] == 0:
        return

    print("Data analysis (first symbol only, as an example)\n")
    import pandas as pd
    example_symbol = summary['symbols'][0]
    example_df = pd.read_parquet(staging_paths[example_symbol])
    print(analyze_stock_performance(example_df))
    print(find_correlations(example_df))

    print("Data visualization (first symbol only, as an example)\n")
    plot_data(example_df)


if __name__ == "__main__":
    main()
