"""
Tests for Travel Policy RAG Pipeline.
Verifies document loading, chunking, FAISS vector indexing, and lexical fallback.
"""

from app.rag.documents import load_policy_documents, chunk_policy_documents
from app.rag.retriever import get_policy_retriever, LexicalPolicyRetriever
from app.rag.indexer import build_and_save_index, FAISS_INDEX_PATH


def test_document_loading_and_chunking():
    raw_docs = load_policy_documents()
    assert len(raw_docs) >= 6
    
    chunks = chunk_policy_documents(raw_docs)
    assert len(chunks) >= len(raw_docs)
    
    sample_chunk = chunks[0]
    assert "doc_id" in sample_chunk.metadata
    assert "category" in sample_chunk.metadata
    assert "chunk_id" in sample_chunk.metadata


def test_lexical_fallback_retriever():
    lex_retriever = LexicalPolicyRetriever()
    results = lex_retriever.retrieve("cancellation fee and non-refundable", top_k=2)
    assert len(results) == 2
    assert results[0]["retrieval_mode"] == "lexical_fallback"
    assert "policy_id" in results[0]


def test_policy_retriever_evidence():
    retriever = get_policy_retriever()
    evidence = retriever.retrieve_evidence("How many days does a refund take to appear in my account?", top_k=2)
    assert len(evidence) >= 1
    top_doc = evidence[0]
    assert "POL" in top_doc["policy_id"]
    assert top_doc["relevance_score"] >= 0.0
    assert len(top_doc["content"]) > 10
