import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
end = datetime.today()
start = end - timedelta(days=3*365)

for t in tickers:
    df = yf.download(t, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
    df.to_csv(f"{t}.csv")
