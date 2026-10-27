"""
Retrieval engine for the Travel Policy RAG pipeline.
Supports FAISS vector search with similarity scores, relevance thresholding,
and a transparent lexical fallback retriever.
"""

import re
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from app.config import settings
from app.rag.indexer import load_vectorstore, FAISS_INDEX_PATH
from app.rag.documents import load_policy_documents, chunk_policy_documents


class LexicalPolicyRetriever:
    """
    Transparent lexical keyword fallback retriever.
    Scores policy chunks based on term frequency and token overlap.
    Clearly labelled so it is never misrepresented as dense vector search.
    """

    def __init__(self):
        raw_docs = load_policy_documents()
        self.chunks: List[Document] = chunk_policy_documents(raw_docs)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = set(re.findall(r"\b\w{3,}\b", query.lower()))
        scored_chunks: List[Tuple[float, Document]] = []

        for doc in self.chunks:
            doc_tokens = re.findall(r"\b\w{3,}\b", doc.page_content.lower())
            if not doc_tokens:
                continue
            # Term overlap count
            overlap = sum(1 for t in doc_tokens if t in query_tokens)
            score = round(overlap / (len(query_tokens) + 1e-5), 3)
            scored_chunks.append((score, doc))

        # Sort descending by lexical score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        results: List[Dict[str, Any]] = []
        for score, doc in scored_chunks[:top_k]:
            results.append({
                "policy_id": doc.metadata.get("doc_id", "POL-UNKNOWN"),
                "title": doc.metadata.get("title", "Policy Document"),
                "category": doc.metadata.get("category", "General"),
                "chunk_id": doc.metadata.get("chunk_id", ""),
                "source": doc.metadata.get("source", ""),
                "content": doc.page_content,
                "relevance_score": float(score),
                "retrieval_mode": "lexical_fallback",
            })
        return results


class PolicyRetriever:
    """
    Primary hybrid/vector policy retriever with automatic fallback to lexical search.
    """

    def __init__(self):
        self.vectorstore = None
        self.lexical_retriever = None
        self._initialize()

    def _initialize(self):
        try:
            self.vectorstore = load_vectorstore(FAISS_INDEX_PATH)
        except Exception as e:
            print(f"Notice: Vectorstore unavailable ({e}). Using lexical fallback.")
            self.vectorstore = None
        self.lexical_retriever = LexicalPolicyRetriever()

    def retrieve_evidence(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves the most relevant policy clauses for a support ticket query.
        
        Returns:
            List of structured evidence records with policy metadata and relevance score.
        """
        clean_query = (query or "").strip()
        if not clean_query:
            return []

        # Attempt vector search via FAISS
        if self.vectorstore is not None:
            try:
                # FAISS similarity_search_with_score returns L2 distance (smaller is better)
                results_with_score = self.vectorstore.similarity_search_with_score(
                    clean_query, k=top_k
                )
                evidence: List[Dict[str, Any]] = []
                for doc, score in results_with_score:
                    # Convert distance to normalized similarity (higher is better, 0.0 to 1.0)
                    sim_score = round(max(0.0, 1.0 / (1.0 + float(score))), 3)
                    evidence.append({
                        "policy_id": doc.metadata.get("doc_id", "POL-UNKNOWN"),
                        "title": doc.metadata.get("title", "Policy Document"),
                        "category": doc.metadata.get("category", "General"),
                        "chunk_id": doc.metadata.get("chunk_id", ""),
                        "source": doc.metadata.get("source", ""),
                        "content": doc.page_content,
                        "relevance_score": sim_score,
                        "retrieval_mode": "faiss_dense_vector",
                    })
                return evidence
            except Exception as e:
                print(f"Vector search failed ({e}). Reverting to lexical fallback.")

        # Fallback to lexical retrieval
        return self.lexical_retriever.retrieve(clean_query, top_k=top_k)


_retriever_instance = None


def get_policy_retriever() -> PolicyRetriever:
    """Singleton getter for the policy retriever."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = PolicyRetriever()
    return _retriever_instance
