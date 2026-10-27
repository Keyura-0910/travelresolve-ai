"""
Script to chunk policy markdown files and build the FAISS vector index.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.rag.indexer import build_and_save_index, FAISS_INDEX_PATH


def main():
    print("Building FAISS Vector Index from Travel Policy Documents...")
    build_and_save_index(FAISS_INDEX_PATH)
    print("Knowledge base index successfully created and ready for RAG retrieval.")


if __name__ == "__main__":
    main()
