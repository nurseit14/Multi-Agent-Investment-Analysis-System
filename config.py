# config.py

import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Корень проекта = папка, где лежит Final_Project
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # === Paths ===
    DATA_DIR: Path = BASE_DIR / "data"
    VECTOR_DB_DIR: Path = BASE_DIR / "vector_store_v2"
    KG_DB_PATH: Path = BASE_DIR / "kg_graph_v2.gml"
    REPORTS_DIR: Path = BASE_DIR / "reports"

    # === LLM/Embeddings (без обязательного OPENAI_API_KEY) ===
    # Эта модель используется HuggingFaceEmbeddings
    HF_EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"

    # Строка-модель для CrewAI через LiteLLM
    # Если используется Ollama:
    CREW_LLM_MODEL: str = "ollama/mistral"
    # Для другой среды можно поменять, например: "gpt-4o-mini"

    # MCP: просто команды/описания для отчёта
    MCP_MARKET_SERVER_CMD: str = "python -m Final_Project.MCP_servers market"
    MCP_NEWS_SERVER_CMD: str = "python -m Final_Project.MCP_servers news"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Создаём нужные директории
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)