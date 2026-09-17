import os

import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)

# Path to the CSV produced by main.py (data_storage/save_data.py -> save_data_to_csv).
# Override with the STOCK_DATA_CSV environment variable if the file lives elsewhere.
DEFAULT_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'stock_data.csv')
CSV_PATH = os.environ.get('STOCK_DATA_CSV', DEFAULT_CSV_PATH)


def load_stock_data(csv_path=CSV_PATH):
    """Load the pipeline's output CSV into a list of dicts, ready to be served.

    Returns an empty list if the file does not exist yet (pipeline not run).
    """
    if not os.path.exists(csv_path):
        return []

    df = pd.read_csv(csv_path)
    return df.to_dict(orient='records')


stock_data = load_stock_data()


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500


@app.route('/prices', methods=['GET'])
def get_all_prices():
    if not stock_data:
        return jsonify({'message': 'No data available. Run the pipeline (main.py) first.'}), 503

    return jsonify(stock_data), 200


@app.route('/prices/<string:symbol>', methods=['GET'])
def get_prices_for_symbol(symbol):
    if not symbol.strip():
        return jsonify({'message': 'Symbol must not be empty'}), 400

    if not stock_data:
        return jsonify({'message': 'No data available. Run the pipeline (main.py) first.'}), 503

    filtered_data = [
        entry for entry in stock_data
        if str(entry.get('Symbol', '')).lower() == symbol.lower()
    ]

    if not filtered_data:
        return jsonify({'message': f"No data found for symbol '{symbol}'"}), 404

    return jsonify(filtered_data), 200


if __name__ == '__main__':
    app.run(debug=True)
