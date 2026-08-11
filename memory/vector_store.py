"""
Memory Module — FAISS Vector Store
Stores and retrieves financial reports, news summaries, and
analysis history using LangChain + FAISS embeddings with graceful fallback.
"""

import os
from typing import List, Optional

try:
    from langchain_community.vectorstores import FAISS
    HAS_FAISS = True
except ImportError:
    FAISS = None
    HAS_FAISS = False

from langchain_core.documents import Document
from config.settings import EMBEDDING_MODEL, VECTOR_STORE_PATH


def get_embeddings():
    """Return the configured embedding model."""
    from config.settings import GOOGLE_API_KEY, LLM_PROVIDER, OPENAI_API_KEY
    if LLM_PROVIDER == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
    else:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)


def save_report_to_memory(ticker: str, report: str, metadata: dict = None) -> bool:
    if not HAS_FAISS:
        print("[Memory] ⚠️ FAISS vector store optional package not installed.")
        return False
    try:
        embeddings = get_embeddings()
        meta = {"ticker": ticker, "type": "investment_report", **(metadata or {})}
        doc = Document(page_content=report, metadata=meta)

        if os.path.exists(VECTOR_STORE_PATH):
            db = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
            db.add_documents([doc])
        else:
            db = FAISS.from_documents([doc], embeddings)

        db.save_local(VECTOR_STORE_PATH)
        print(f"[Memory] ✅ Report for {ticker} saved to vector store.")
        return True

    except Exception as e:
        print(f"[Memory] ⚠️ Could not save to vector store: {e}")
        return False


def search_similar_reports(query: str, k: int = 3) -> List[Document]:
    if not HAS_FAISS:
        return []
    try:
        if not os.path.exists(VECTOR_STORE_PATH):
            return []
        embeddings = get_embeddings()
        db = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        results = db.similarity_search(query, k=k)
        return results
    except Exception as e:
        print(f"[Memory] ⚠️ Search failed: {e}")
        return []


def get_past_reports_for_ticker(ticker: str, k: int = 5) -> List[Document]:
    return search_similar_reports(f"{ticker} investment report analysis", k=k)


def clear_memory():
    import shutil
    if os.path.exists(VECTOR_STORE_PATH):
        shutil.rmtree(VECTOR_STORE_PATH)
        print("[Memory] ✅ Vector store cleared.")
    else:
        print("[Memory] No vector store found.")
