"""
FAISS Vector Store Indexer for TravelResolve AI.
Provides configurable embeddings (OpenAIEmbeddings or DeterministicLocalEmbeddings),
builds a local FAISS index from policy chunks, and persists it to disk.
"""

import os
import re
import math
import hashlib
from pathlib import Path
from typing import List, Optional
import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS

from app.config import settings, VECTORSTORE_DIR
from app.rag.documents import load_policy_documents, chunk_policy_documents

FAISS_INDEX_PATH = VECTORSTORE_DIR / "faiss_index"


class DeterministicLocalEmbeddings(Embeddings):
    """
    A fast, deterministic local embedding generator implementing LangChain's Embeddings interface.
    Generates unit-normalized dense vectors (dimension 256) via character/word n-gram hashing.
    Enables full local FAISS vector search without requiring paid API tokens or heavyweight downloads.
    """

    def __init__(self, dimension: int = 256):
        self.dimension = dimension

    def _embed_text(self, text: str) -> List[float]:
        vec = np.zeros(self.dimension, dtype=np.float32)
        clean = (text or "").lower()
        tokens = re.findall(r"\b\w+\b", clean)
        
        # Word-level features
        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.dimension
            vec[h] += 1.0

        # Bigram features for local semantic phrasing
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]}_{tokens[i+1]}"
            h = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest(), 16) % self.dimension
            vec[h] += 1.5

        # L2 normalization for cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text)


def get_embedding_function() -> Embeddings:
    """Returns the configured embedding instance based on environment settings."""
    if settings.EMBEDDING_PROVIDER == "openai" and settings.LLM_API_KEY:
        try:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                api_key=settings.LLM_API_KEY,
                model=settings.EMBEDDING_MODEL
            )
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAIEmbeddings ({e}). Falling back to local embeddings.")
            return DeterministicLocalEmbeddings()
    return DeterministicLocalEmbeddings()


def build_and_save_index(index_path: Path = FAISS_INDEX_PATH) -> FAISS:
    """Loads markdown policies, chunks them, builds a FAISS vector store, and saves to disk."""
    print("Loading travel policy documents...")
    raw_docs = load_policy_documents()
    chunked_docs = chunk_policy_documents(raw_docs)
    print(f"Created {len(chunked_docs)} policy chunks from {len(raw_docs)} documents.")

    embedder = get_embedding_function()
    vectorstore = FAISS.from_documents(chunked_docs, embedder)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(index_path))
    print(f"FAISS index successfully saved to: {index_path}")
    return vectorstore


def load_vectorstore(index_path: Path = FAISS_INDEX_PATH) -> Optional[FAISS]:
    """Loads an existing FAISS index or builds a new one if missing."""
    embedder = get_embedding_function()
    if (index_path / "index.faiss").exists() or index_path.exists():
        try:
            vectorstore = FAISS.load_local(
                str(index_path),
                embedder,
                allow_dangerous_deserialization=True
            )
            return vectorstore
        except Exception as e:
            print(f"Notice: Could not load index ({e}). Rebuilding...")
            return build_and_save_index(index_path)
    else:
        return build_and_save_index(index_path)
