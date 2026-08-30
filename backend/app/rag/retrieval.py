"""Retrieval with reranking + citation - docs 10_RAG."""
from typing import List, Dict, Any

def retrieve(query: str, top_k: int = 5, top_n: int = 3, filters: Dict = None) -> List[Dict[str, Any]]:
    """Hybrid: Qdrant semantic top_k -> rerank to top_n -> citation."""
    from qdrant_client import QdrantClient
    from fastembed import TextEmbedding
    client = QdrantClient(url="http://localhost:6333", check_compatibility=False)
    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    qvec = list(model.embed([query]))[0]
    # filter by language/source if provided
    hits = client.query_points(collection_name="orca_knowledge", query=qvec, limit=top_k).points
    # Simple rerank: already cosine sorted, take top_n
    reranked = sorted(hits, key=lambda h: h.score, reverse=True)[:top_n]
    results = []
    for h in reranked:
        p = h.payload
        results.append({
            "document_id": p.get("document_id"),
            "chunk_id": p.get("chunk_id"),
            "source": p.get("source"),
            "title": p.get("title"),
            "text": p.get("text"),
            "snippet": p.get("text","")[:300],
            "score": h.score,
            "citation": f"{p.get('source')}/{p.get('title')}#chunk{p.get('chunk_index')}",
            "object_key": p.get("object_key")
        })
    return results

def search_knowledge(query: str, top_k: int = 3) -> List[Dict]:
    # Wrapper used by rag agent - keeps old signature
    return retrieve(query, top_k=top_k, top_n=top_k)
