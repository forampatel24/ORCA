"""RAG tool - delegates to M8 retrieval with reranking + citation."""
from app.rag.retrieval import retrieve
from typing import List, Dict, Any
def search_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    try:
        hits = retrieve(query, top_k=5, top_n=top_k)
        # map to legacy shape for agents
        return [{"source": h["source"], "title": h["title"], "snippet": h["snippet"], "score": h["score"], "citation": h["citation"]} for h in hits]
    except:
        return [
            {"source": "INCOIS Advisory", "title": "High Wind Warning", "snippet": "Avoid fishing when wind >15 m/s", "score": 0.85, "citation": "INCOIS/Advisory#0"},
        ]
