"""Evidence/RAG Agent - docs 06 AI-017 - Mumbai-only authentic, no hardcoded."""
from app.tools.rag import search_knowledge

class RagAgent:
    name = "rag_agent"
    tools = ["search_knowledge"]
    async def run(self, query: str = "", region: str = "mumbai") -> dict:
        hits = search_knowledge(query, region=region)
        return {"evidence": hits, "count": len(hits), "region": region, "source": "qdrant_orca_knowledge_mumbai" if hits else "no_authentic_mumbai_evidence"}

rag_agent = RagAgent()
