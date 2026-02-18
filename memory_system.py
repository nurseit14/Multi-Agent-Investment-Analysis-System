# memory_system.py

from __future__ import annotations
from typing import List, Dict

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate

from .config import settings


# ===============================
# Короткая память (в оперативке)
# ===============================

class ShortTermMemory:
    """Простое хранение диалога в списке строк."""

    def __init__(self) -> None:
        self._buffer: List[Dict[str, str]] = []

    def save_context(self, user_msg: str, assistant_msg: str) -> None:
        self._buffer.append({"user": user_msg, "assistant": assistant_msg})

    def load(self) -> str:
        return "\n".join(
            f"User: {m['user']}\nAssistant: {m['assistant']}"
            for m in self._buffer
        )

    def clear(self) -> None:
        self._buffer = []


# =======================================
# Долгосрочная память на векторном стораже
# =======================================

class LongTermVectorMemory:
    """
    Векторное хранилище на Chroma для длинной истории,
    id — просто "mem_X".
    """

    def __init__(self) -> None:
        self._emb = HuggingFaceEmbeddings(model_name=settings.HF_EMBEDDING_MODEL)
        self._store = Chroma(
            collection_name="mas_long_term_memory_v2",
            embedding_function=self._emb,
            persist_directory=str(settings.VECTOR_DB_DIR),
        )

    def add_memory(self, text: str, metadata: Dict | None = None) -> None:
        doc = Document(page_content=text, metadata=metadata or {})
        self._store.add_documents([doc])

    def search(self, query: str, k: int = 5) -> List[Document]:
        return self._store.similarity_search(query, k=k)


# ======================
# Компрессор памяти
# ======================

class MemoryCompressor:
    """
    Упрощённый компрессор: вместо LLM делаем простое суммирование —
    берём первые N и последние N строк.
    """

    def __init__(self, keep_head: int = 6, keep_tail: int = 6) -> None:
        self.keep_head = keep_head
        self.keep_tail = keep_tail

    def compress(self, conversation_text: str) -> str:
        lines = [line for line in conversation_text.splitlines() if line.strip()]
        if len(lines) <= self.keep_head + self.keep_tail:
            return conversation_text

        head = lines[: self.keep_head]
        tail = lines[-self.keep_tail:]
        return "\n".join(head + ["\n... [compressed middle] ...\n"] + tail)


# ======================
# Общий менеджер
# ======================

class MemoryManager:
    """
    Управляет короткой и длинной памятью, автоматически
    сжимает историю при превышении порога символов.
    """

    def __init__(self) -> None:
        self.short_term = ShortTermMemory()
        self.long_term = LongTermVectorMemory()
        self.compressor = MemoryCompressor()

    def save_interaction(self, user_msg: str, assistant_msg: str) -> None:
        self.short_term.save_context(user_msg, assistant_msg)

    def maybe_compress(self, threshold_chars: int = 2000) -> None:
        history_text = self.short_term.load()
        if len(history_text) < threshold_chars:
            return
        summary = self.compressor.compress(history_text)
        self.long_term.add_memory(summary, metadata={"type": "compressed-dialog"})
        self.short_term.clear()

    def retrieve_context(self, query: str) -> str:
        docs = self.long_term.search(query, k=5)
        return "\n\n".join(d.page_content for d in docs)