# chains.py

from __future__ import annotations
from typing import List

from pydantic import BaseModel, Field

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel

from .config import settings
from .rag_kg import dynamic_retriever


# ============================
# Схемы выходных структур
# ============================

class TechnicalAnalysis(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    trend_summary: str
    key_indicators: List[str]
    rating: str  # "bullish" | "bearish" | "neutral"


class FundamentalAnalysis(BaseModel):
    ticker: str
    business_summary: str
    strengths: List[str]
    weaknesses: List[str]
    valuation_view: str


class RiskAssessment(BaseModel):
    ticker: str
    risk_factors: List[str]
    overall_risk_level: str  # "low" | "medium" | "high"
    comments: str


# =======================================
# Вспомогательный конструктор промптов
# =======================================

def _build_prompt(template: str) -> PromptTemplate:
    return PromptTemplate.from_template(template)


# =======================================
# Цепочка технического анализа
# =======================================

def build_technical_chain(llm: BaseLanguageModel):
    prompt = _build_prompt(
        "You are a technical analyst.\n"
        "Given recent price behaviour and basic stats for {ticker}, "
        "produce a concise technical view.\n\n"
        "Context:\n{context}\n\n"
        "Answer in English."
    )

    class Chain:
        def invoke(self, inputs):
            text = prompt.format(**inputs)
            result = llm.invoke(text)
            return result.content

    return Chain()


# =======================================
# Цепочка фундаментального анализа (RAG)
# =======================================

def build_fundamental_chain(llm: BaseLanguageModel):
    prompt = _build_prompt(
        "You are a fundamental equity analyst.\n\n"
        "Use the context below to summarize the business and fundamentals of {ticker}.\n"
        "Context:\n{context}\n\n"
        "Give strengths, weaknesses and a short valuation comment."
    )

    class Chain:
        def invoke(self, inputs):
            text = prompt.format(**inputs)
            result = llm.invoke(text)
            return result.content

    return Chain()


# =======================================
# Цепочка оценки рисков
# =======================================

def build_risk_chain(llm: BaseLanguageModel):
    prompt = _build_prompt(
        "You are a risk manager.\n\n"
        "Given the technical and fundamental analysis for {ticker} and extra context:\n"
        "{context}\n\n"
        "List key risks and rate overall risk as low/medium/high."
    )

    class Chain:
        def invoke(self, inputs):
            text = prompt.format(**inputs)
            result = llm.invoke(text)
            return result.content

    return Chain()


# =======================================
# Генерация финального отчёта
# =======================================

def build_report_chain(llm: BaseLanguageModel):
    prompt = _build_prompt(
        "# Investment report for {ticker}\n\n"
        "Technical view:\n{tech}\n\n"
        "Fundamental view:\n{fund}\n\n"
        "Risk assessment:\n{risk}\n\n"
        "Write a final recommendation (BUY/HOLD/SELL) with justification."
    )

    class Chain:
        def invoke(self, inputs):
            text = prompt.format(**inputs)
            result = llm.invoke(text)
            return result.content

    return Chain()


# =======================================
# Вспомогательный доступ к RAG
# =======================================

def retrieve_context_for_question(ticker: str, qtype: str) -> str:
    retriever = dynamic_retriever(qtype)
    docs = retriever.similarity_search(ticker, k=6)
    return "\n\n".join(d.page_content for d in docs)