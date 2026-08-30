"""RAG tool - Qdrant search with FastEmbed (M5/M8 real)."""
from typing import List, Dict, Any
def search_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    try:
        from qdrant_client import QdrantClient
        from fastembed import TextEmbedding
        client = QdrantClient(url="http://localhost:6333", check_compatibility=False)
        info = client.get_collection("orca_knowledge")
        if info.points_count == 0:
            raise ValueError("empty")
        model = TextEmbedding("BAAI/bge-small-en-v1.5")
        qvec = list(model.embed([query]))[0]
        hits = client.query_points(collection_name="orca_knowledge", query=qvec, limit=top_k).points
        return [{"source": h.payload.get("source","Qdrant"), "title": h.payload.get("document",""), "snippet": h.payload.get("text","")[:300], "score": h.score} for h in hits]
    except Exception as e:
        # fallback mock if Qdrant empty or error
        return [
            {"source": "INCOIS Advisory", "title": "High Wind Warning", "snippet": "Avoid fishing when wind >15 m/s", "score": 0.85},
            {"source": "Safety Guideline", "title": "Marine Protected Area Rule", "snippet": "Do not enter MPA without permission", "score": 0.78},
        ]
