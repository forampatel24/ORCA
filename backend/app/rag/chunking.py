"""Chunking - docs 10_RAG 500-1000 tokens ~ 400-800 chars with overlap."""
import re
from typing import List, Dict

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text

def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> List[Dict]:
    """Semantic chunking by sentences, 700 chars target, 100 overlap."""
    text = clean_text(text)
    if len(text) <= chunk_size:
        return [{"text": text, "chunk_index": 0}]
    # split by sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    cur = ""
    idx = 0
    for sent in sentences:
        if len(cur) + len(sent) < chunk_size:
            cur += " " + sent if cur else sent
        else:
            chunks.append({"text": cur.strip(), "chunk_index": idx})
            idx += 1
            # overlap: keep last 100 chars
            cur = cur[-overlap:] + " " + sent if len(cur) > overlap else sent
    if cur:
        chunks.append({"text": cur.strip(), "chunk_index": idx})
    return chunks
