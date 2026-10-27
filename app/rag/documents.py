"""
Document loader and chunker for the Travel Policy Knowledge Base.
Parses policy markdown files and generates structured LangChain Documents with metadata.
"""

import re
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import POLICIES_DIR


def extract_metadata_from_text(text: str, filename: str) -> dict:
    """Extracts document header attributes (ID, category, title) from markdown."""
    title_match = re.search(r"^#\s+Policy Document:\s*(.+)$", text, re.MULTILINE)
    doc_id_match = re.search(r"^Document ID:\s*(.+)$", text, re.MULTILINE)
    category_match = re.search(r"^Category:\s*(.+)$", text, re.MULTILINE)

    title = title_match.group(1).strip() if title_match else filename.replace(".md", "").replace("_", " ").title()
    doc_id = doc_id_match.group(1).strip() if doc_id_match else filename.replace(".md", "").upper()
    category = category_match.group(1).strip() if category_match else "General Policy"

    return {
        "source": filename,
        "title": title,
        "doc_id": doc_id,
        "category": category,
    }


def load_policy_documents(policies_dir: Path = POLICIES_DIR) -> List[Document]:
    """Reads all markdown files from policies directory into LangChain Documents."""
    docs: List[Document] = []
    if not policies_dir.exists():
        return docs

    for file_path in sorted(policies_dir.glob("*.md")):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        meta = extract_metadata_from_text(content, file_path.name)
        docs.append(Document(page_content=content, metadata=meta))

    return docs


def chunk_policy_documents(
    docs: List[Document],
    chunk_size: int = 450,
    chunk_overlap: int = 60
) -> List[Document]:
    """Splits policy documents into semantically coherent overlapping chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n- ", "\n\n", "\n", " ", ""],
        keep_separator=True
    )

    chunked_docs: List[Document] = []
    for doc in docs:
        splits = text_splitter.split_text(doc.page_content)
        for idx, chunk in enumerate(splits):
            chunk_meta = dict(doc.metadata)
            chunk_meta["chunk_id"] = f"{doc.metadata.get('doc_id', 'DOC')}-C{idx+1:02d}"
            chunked_docs.append(Document(page_content=chunk.strip(), metadata=chunk_meta))

    return chunked_docs
