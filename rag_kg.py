from pathlib import Path
from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from .config import settings
from .pdf_loader import load_pdf_as_documents


PDF_PATH = "/Users/nurseiitzhuzbay/PycharmProjects/PythonProject/Publications_Article_232_29_03_12_The_phenomenal_rise_in_Apple’s.pdf"


def build_vector_store(docs: List[Document]):
    if Path(PDF_PATH).exists():
        pdf_docs = load_pdf_as_documents(PDF_PATH)
        all_docs = docs + pdf_docs
    else:
        print("⚠️ PDF not found, continuing without article")
        all_docs = docs

    embeddings = HuggingFaceEmbeddings(
        model_name=settings.HF_EMBEDDING_MODEL
    )

    vectordb = Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        persist_directory=str(settings.VECTOR_DB_DIR),
    )

    return vectordb


def build_knowledge_graph(docs: List[Document]):
    graph = {}

    for d in docs:
        ticker = d.metadata.get("ticker", "UNKNOWN")
        graph.setdefault(ticker, []).append(d.page_content)

    return graph