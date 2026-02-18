from __future__ import annotations

from crewai import Agent, LLM


def build_local_llm() -> LLM:
    """
    Локальная LLM через Ollama + LiteLLM.
    ВАЖНО: у тебя должен быть запущен ollama с моделью mistral:
      ollama run mistral
    """
    return LLM(
        model="ollama/mistral",          # строка, а НЕ dict!
        base_url="http://localhost:11434",
        temperature=0.2,
        max_tokens=2048,
    )


def build_agents() -> dict:
    """
    Создаём всех агентов для финансового анализа.
    Без manager-агента, без MCP-делегирования.
    """
    llm = build_local_llm()

    data_agent = Agent(
        role="Data Acquisition Agent",
        goal="Summarize already collected multimodal financial data for the given tickers.",
        backstory=(
            "Ты специалист по данным. Данные уже собраны Python-кодом "
            "(цены акций, новости, изображения), твоя задача — аккуратно "
            "их интерпретировать и описать ключевые наблюдения."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    technical_agent = Agent(
        role="Technical Analyst",
        goal="Perform clear technical analysis based on price patterns and indicators.",
        backstory=(
            "Ты профессиональный технический аналитик. Ты смотришь на тренды, "
            "волатильность, уровни поддержки/сопротивления, скользящие средние и т.д."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    fundamental_agent = Agent(
        role="Fundamental Analyst",
        goal="Analyze companies' fundamentals using textual descriptions, news and RAG context.",
        backstory=(
            "Ты фундаментальный аналитик. Оцениваешь бизнес-модель, прибыльность, "
            "риски, конкурентную позицию, новости и долгосрочные факторы."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    risk_agent = Agent(
        role="Risk Analyst",
        goal="Combine technical and fundamental signals into a unified risk assessment.",
        backstory=(
            "Ты специализируешься на оценке рыночных и специфических рисков: "
            "волатильность, регуляторные риски, конкуренция, новости, макроэкономика."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    report_agent = Agent(
        role="Report Writer",
        goal="Write a concise investment report with clear structure and recommendations.",
        backstory=(
            "Ты финансовый аналитик-писатель. Умеешь превращать сложный анализ "
            "в понятный отчёт для инвестора, с чёткими выводами и рекомендациями."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    evaluator_agent = Agent(
        role="Evaluation Agent",
        goal="Critically evaluate the quality of the final report.",
        backstory=(
            "Ты независимый ревьюер. Проверяешь глубину анализа, логичность, "
            "баланс рисков и реалистичность рекомендаций."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    return {
        "data": data_agent,
        "technical": technical_agent,
        "fundamental": fundamental_agent,
        "risk": risk_agent,
        "report": report_agent,
        "evaluator": evaluator_agent,
    }