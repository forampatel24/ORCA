"""Evidence/RAG Agent - docs 06 AI-017."""
from app.tools.rag import search_knowledge

class RagAgent:
    name = "rag_agent"
    tools = ["search_knowledge"]
    async def run(self, query: str = "") -> dict:
        hits = search_knowledge(query)
        return {"evidence": hits, "count": len(hits)}

rag_agent = RagAgent()
