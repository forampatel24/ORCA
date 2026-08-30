"""RAG tool - Qdrant search (mock until M8)."""
from typing import List, Dict, Any
def search_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Try Qdrant, fallback mock."""
    try:
        from qdrant_client import QdrantClient
        from fastembed import TextEmbedding
        client = QdrantClient(url="http://localhost:6333")
        # For M5 mock without embeddings, return mock
        info = client.get_collection("orca_knowledge")
        if info.points_count == 0:
            raise ValueError("empty")
        # real search would embed query
    except:
        pass
    return [
        {"source": "INCOIS Advisory", "title": "High Wind Warning", "snippet": "Avoid fishing when wind >15 m/s", "score": 0.85},
        {"source": "Safety Guideline", "title": "Marine Protected Area Rule", "snippet": "Do not enter MPA without permission", "score": 0.78},
    ]
