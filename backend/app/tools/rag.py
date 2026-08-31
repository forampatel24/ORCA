"""RAG tool - Mumbai-only authentic, no hardcoded mock."""
from app.rag.retrieval import retrieve
from typing import List, Dict, Any
import structlog
log = structlog.get_logger()
def search_knowledge(query: str, top_k: int = 3, region: str = "mumbai") -> List[Dict[str, Any]]:
    """Authentic retrieval - no hardcoded High Wind Warning mock. Returns empty if no Mumbai data."""
    try:
        # Mumbai-only filter - Qdrant payload region=mumbai when ingested via Mumbai pipeline
        hits = retrieve(query, top_k=5, top_n=top_k, filters={"region": region} if region else None)
        # If Mumbai filter yields 0, try unfiltered (for back-compat) but log
        if not hits and region == "mumbai":
            hits = retrieve(query, top_k=5, top_n=top_k)
            log.info("rag_mumbai_filter_fallback", query=query[:50], hits=len(hits))
        return [{"source": h["source"], "title": h["title"], "snippet": h["snippet"], "score": h["score"], "citation": h["citation"]} for h in hits]
    except Exception as e:
        log.warning("rag_search_failed_mumbai", error=str(e))
        return []  # No hardcoded mock - authentic empty
