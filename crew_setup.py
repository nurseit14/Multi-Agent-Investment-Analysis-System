from __future__ import annotations

import asyncio
from typing import List, Dict, Any

from crewai import Task, Crew, Process
from langchain_core.documents import Document

from .agents import build_agents
from .data_prep import build_multimodal_sample
from .visualization import generate_price_plot
from .rag_kg import build_vector_store, build_knowledge_graph
from .evaluation import build_evaluation_chain


# =========================
# 1. ПАРАЛЛЕЛЬНЫЙ СБОР ДАННЫХ
# =========================

async def run_data_stage(ticker: str) -> Dict[str, Any]:
    """
    Асинхронно собирает мультимодальные данные для одного тикера.
    """
    try:
        sample = await build_multimodal_sample(ticker)
        img_path = generate_price_plot(ticker, sample.price_table)
        return {
            "ticker": ticker,
            "sample": sample,
            "image_path": img_path,
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


async def parallel_data_collection(tickers: List[str]) -> List[Dict[str, Any]]:
    """
    Запускает сбор данных по всем тикерам параллельно.
    """
    tasks = [run_data_stage(t) for t in tickers]
    return await asyncio.gather(*tasks)


# =========================
# 2. PREPARE DOCS ДЛЯ RAG
# =========================

def prepare_docs(samples: List[Dict[str, Any]]) -> List[Document]:
    """
    Превращаем таблицы цен, новости и текстовые описания в список Document.
    Параллельно строим векторное хранилище и граф знаний (для отчёта).
    """
    docs: List[Document] = []

    for item in samples:
        if "error" in item:
            # пропускаем тикеры, по которым не удалось собрать данные
            continue

        ticker = item["ticker"]
        sample = item["sample"]

        # 1) Последние 10 строк таблицы цен
        price_txt = sample.price_table.tail(10).to_markdown()
        docs.append(
            Document(
                page_content=f"Recent price table for {ticker}:\n{price_txt}",
                metadata={"ticker": ticker, "source": "price_table"},
            )
        )

        # 2) Новости
        for news in sample.news_texts:
            docs.append(
                Document(
                    page_content=news,
                    metadata={"ticker": ticker, "source": "news"},
                )
            )

        # 3) Описание изображения
        docs.append(
            Document(
                page_content=f"Image description for {ticker}: {sample.image_caption}",
                metadata={"ticker": ticker, "source": "image_caption"},
            )
        )

    # Строим RAG-структуры (как часть пайплайна; возвращаем docs)
    if docs:
        _vs = build_vector_store(docs)
        _kg = build_knowledge_graph(docs)
        # Мы их не обязательно используем напрямую в коде агентов,
        # но они существуют как компонент системы для отчёта по проекту.

    return docs


# =========================
# 3. СБОРКА CREW (БЕЗ ИЕРАРХИИ/MCP)
# =========================

def build_crew(tickers: List[str]) -> Crew:
    """
    Создаём Crew с несколькими агентами.
    Без hierarchical process, без manager_agent, чтобы НЕ было MCP-делегирования
    и ошибок Delegate/AskQuestion.
    """
    agents = build_agents()
    eval_chain = build_evaluation_chain()

    tickers_str = ", ".join(tickers)

    # --- ЗАДАЧИ ---

    # 1) Технический анализ
    technical_task = Task(
        description=(
            f"Perform technical analysis for tickers: {tickers_str}.\n"
            "- Используй информацию о трендах, волатильности и уровнях\n"
            "- Опиши краткосрочный и долгосрочный тренд\n"
            "- Сформируй технический вердикт по каждому тикеру"
        ),
        agent=agents["technical"],
        expected_output=(
            "JSON-like текст с полями: ticker, trend, key_levels, "
            "volatility_comment, technical_view."
        ),
    )

    # 2) Фундаментальный анализ
    fundamental_task = Task(
        description=(
            f"Perform fundamental analysis for tickers: {tickers_str}.\n"
            "- Оцени бизнес-модель, новости, отрасль\n"
            "- Выдели драйверы роста и основные риски\n"
            "- Сформируй фундаментальный вердикт и горизонт инвестиций"
        ),
        agent=agents["fundamental"],
        expected_output=(
            "Структурированный текст, по каждому тикеру: "
            "business_summary, growth_drivers, key_risks, fundamental_view."
        ),
    )

    # 3) Оценка рисков (зависит от двух предыдущих)
    risk_task = Task(
        description=(
            f"Combine technical and fundamental insights into a unified risk view for: {tickers_str}.\n"
            "- Сопоставь технические сигналы и фундаментальные факторы\n"
            "- Оцени общий риск-профиль (низкий/средний/высокий)\n"
            "- Выдели отдельные риски для каждого тикера"
        ),
        agent=agents["risk"],
        expected_output=(
            "Структурированный текст с полями: ticker, risk_level, "
            "risk_factors, upside_comment."
        ),
        depends_on=[technical_task, fundamental_task],
    )

    # 4) Финальный инвестиционный отчёт
    report_task = Task(
        description=(
            f"Write a final investment report for tickers: {tickers_str}.\n"
            "Структура отчёта:\n"
            "1. Introduction (goal, data sources, period)\n"
            "2. Market overview (very short)\n"
            "3. Company-by-company analysis (technical + fundamental)\n"
            "4. Risk assessment\n"
            "5. Final recommendations (Buy/Hold/Sell with horizon)\n"
            "Пиши в виде аккуратного Markdown-отчёта."
        ),
        agent=agents["report"],
        expected_output="Полный Markdown-отчёт.",
        depends_on=[risk_task],
    )

    # 5) Оценка качества отчёта
    evaluation_task = Task(
        description=(
            "Evaluate the quality of the final investment report.\n"
            "- Проверь глубину анализа\n"
            "- Логичность структуры\n"
            "- Отражение рисков\n"
            "- Полезность для частного инвестора\n"
            "Верни краткое заключение и список замечаний/улучшений."
        ),
        agent=agents["evaluator"],
        expected_output=(
            "JSON-like текст с полями: depth_score (1-10), "
            "consistency_score (1-10), risk_coverage_score (1-10), "
            "usefulness_score (1-10), comments."
        ),
        depends_on=[report_task],
    )

    # --- CREW ---

    crew = Crew(
        agents=[
            agents["data"],
            agents["technical"],
            agents["fundamental"],
            agents["risk"],
            agents["report"],
            agents["evaluator"],
        ],
        tasks=[
            technical_task,
            fundamental_task,
            risk_task,
            report_task,
            evaluation_task,
        ],
        process=Process.sequential,  # ❗ НЕТ hierarchical -> НЕТ MCP-делегирования
        verbose=True,
    )

    # "приклеим" eval_chain, если ты его потом используешь
    crew._eval_chain = eval_chain
    crew._tickers = tickers

    return crew