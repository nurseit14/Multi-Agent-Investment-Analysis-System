from __future__ import annotations

import asyncio
from typing import List

from .crew_setup import build_crew, parallel_data_collection, prepare_docs
from .report_exporter import save_markdown_report  # если есть; иначе можно удалить импорт


TICKERS: List[str] = ["AAPL", "MSFT", "TSLA"]


async def run_pipeline(tickers: List[str]) -> None:
    print("📡 Collecting multimodal data...")
    samples = await parallel_data_collection(tickers)

    print("📚 Preparing RAG resources...")
    docs = prepare_docs(samples)
    print(f"Prepared {len(docs)} documents for RAG/Knowledge Graph.")

    print("🤖 Creating multi-agent crew...")
    crew = build_crew(tickers)

    print("🚀 Running full multi-agent analysis pipeline...")
    result = crew.kickoff()  # синхронный запуск

    # result обычно = финальный output последней задачи (evaluation_task или report_task)
    if isinstance(result, str):
        final_report_md = result
    else:
        # на всякий случай приводим к строке
        final_report_md = str(result)

    # Сохраняем отчёт (если у тебя есть такая функция)
    try:
        output_path = save_markdown_report(final_report_md, "final_investment_report.md")
        print(f"✅ Final report saved to: {output_path}")
    except Exception:
        # если нет report_exporter или он другой — просто выведем
        print("📄 Final report:\n")
        print(final_report_md)


if __name__ == "__main__":
    asyncio.run(run_pipeline(TICKERS))