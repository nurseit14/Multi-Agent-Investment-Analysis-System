import time
import pandas as pd
import yfinance as yf

from .config import settings


def safe_download(ticker: str):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty:
            raise ValueError("Empty dataframe")
        return df
    except Exception as e:
        print(f"⚠️ Using fallback data for {ticker}: {e}")
        dates = pd.date_range(end=pd.Timestamp.today(), periods=180)
        prices = pd.Series(range(180)) + 100
        return pd.DataFrame({"Adj Close": prices.values}, index=dates)


def build_multimodal_sample(tickers):
    result = {}

    for t in tickers:
        time.sleep(3)
        df = safe_download(t)

        result[t] = {
            "prices": df,
            "news": [f"Demo news about {t}. No external API used."],
            "images": [f"Image placeholder for {t}"]
        }

    return result