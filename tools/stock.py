import yfinance as yf
from langchain_core.tools import tool

import json

@tool
def get_stock_price(symbol: str):
    """Get the current stock price and currency"""
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    price = float(data["Close"].iloc[-1])
    currency = stock.info.get('currency', 'Unknown')
    return json.dumps({
        "symbol": symbol,
        "price": price,
        "currency": currency
    })