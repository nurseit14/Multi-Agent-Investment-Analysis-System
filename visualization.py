from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .config import settings


def generate_price_plot(ticker: str, df: pd.DataFrame) -> str:
    """
    Сохраняет простой график цен для multimodal данных.
    """
    if "Adj Close" not in df.columns:
        return ""

    plt.figure()
    df["Adj Close"].plot()
    plt.title(f"{ticker} Adjusted Close Price")
    plt.xlabel("Date")
    plt.ylabel("Price")

    img_path = settings.DATA_DIR / f"{ticker}_price.png"
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()
    return str(img_path)