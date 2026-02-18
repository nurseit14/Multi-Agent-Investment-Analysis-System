# MCP_servers.py

"""
Примеры MCP-серверов для:
1) market_data_server  – исторические цены, простые технические фичи
2) news_server         – новости (текстовые заглушки)

Запуск (пример):
    python -m Final_Project.MCP_servers market
    python -m Final_Project.MCP_servers news

В этом варианте код минималистичный: он нужен в основном для отчёта и демонстрации.
"""

import asyncio
import sys
from typing import List

from mcp.server.fastmcp import FastMCPServer
import yfinance as yf


# ============================
# Market data MCP server
# ============================

market_app = FastMCPServer("market_data_server")


@market_app.tool()
async def get_prices(ticker: str) -> dict:
    """
    Вернуть последние котировки для тикера.
    """
    df = yf.download(ticker, period="1mo", interval="1d")
    if df.empty:
        return {"ticker": ticker, "prices": []}
    records = df.reset_index()[["Date", "Close"]].tail(10).to_dict(orient="records")
    return {"ticker": ticker, "prices": records}


# ============================
# News MCP server (заглушка)
# ============================

news_app = FastMCPServer("news_server")


@news_app.tool()
async def get_news(ticker: str) -> dict:
    """
    Вернёт фиктивные новости для тикера (для примера MCP).
    """
    sample = [
        {
            "title": f"{ticker}: sample news headline",
            "summary": f"Short synthetic summary for {ticker}. Used to demonstrate MCP integration.",
        }
    ]
    return {"ticker": ticker, "articles": sample}


# ============================
# main
# ============================

async def main():
    if len(sys.argv) < 2:
        print("Usage: python -m Final_Project.MCP_servers [market|news]")
        sys.exit(1)

    server_type = sys.argv[1].lower()
    if server_type == "market":
        await market_app.run(transport="stdio")
    elif server_type == "news":
        await news_app.run(transport="stdio")
    else:
        print("Unknown server type:", server_type)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())