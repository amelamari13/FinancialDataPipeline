import yfinance as yf
import requests


def extract_data_yahoo(symbol, period='1y'):
    """Extract financial data of an action"""
    stock = yf.Ticker(symbol)
    data = stock.history(period=period)
    return data

