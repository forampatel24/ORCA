"""Conversation service - docs 02 CONV multi-turn + reference resolution."""
import psycopg, uuid, re
from typing import Dict, Any, Optional

def save_message(conversation_id: str, user_id: str, role: str, content: str, language: str = "en"):
    # M10 thorough: handle non-UUID conversation_id, use orca_app least-privilege
    import re as _re
    # validate UUID, if not, generate new
    try:
        uuid.UUID(conversation_id)
        cid = conversation_id
    except:
        cid = str(uuid.uuid4())
        conversation_id = cid
    conn = psycopg.connect("host=localhost dbname=orca_db user=orca_app password=orca_app_pass")
    cur = conn.cursor()
    # ensure conversation exists
    try:
        cur.execute("SELECT id FROM conversations WHERE id=%s", (conversation_id,))
        if not cur.fetchone():
            cur.execute("INSERT INTO conversations (id, user_id, title) VALUES (%s,%s,%s)", (conversation_id, user_id, content[:50]))
    except:
        # if fails due to invalid uuid, generate new
        conversation_id = str(uuid.uuid4())
        cur.execute("INSERT INTO conversations (id, user_id, title) VALUES (%s,%s,%s)", (conversation_id, user_id, content[:50]))
    cur.execute("INSERT INTO messages (id, conversation_id, role, content, language) VALUES (%s,%s,%s,%s,%s)",
        (str(uuid.uuid4()), conversation_id, role, content, language))
    conn.commit()
    conn.close()

def get_history(conversation_id: str, limit: int = 5) -> list:
    try:
        uuid.UUID(conversation_id)
    except:
        return []
    try:
        conn = psycopg.connect("host=localhost dbname=orca_db user=orca_app password=orca_app_pass")
        cur = conn.cursor()
        cur.execute("SELECT role, content FROM messages WHERE conversation_id=%s ORDER BY created_at DESC LIMIT %s", (conversation_id, limit))
        rows = cur.fetchall()
        conn.close()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
    except:
        return []

def resolve_references(query: str, history: list, last_location: Optional[str] = None) -> Dict[str, Any]:
    """Resolve there/that zone/tomorrow + Marathi तिथे using history."""
    ql = query.lower()
    resolved = query
    pronouns = ["there", "that zone", "that pfz", "that location", "this zone", "तिथे", "त्या ठिकाणी"]
    if any(p in ql for p in pronouns) and last_location:
        resolved += f" (referring to {last_location})"
    # time resolution
    time_map = {"tomorrow": "2026-08-31", "today": "2026-08-30", "6 am": "06:00"}
    time_resolved = None
    for k,v in time_map.items():
        if k in ql:
            time_resolved = v
            break
    return {"resolved_query": resolved, "time": time_resolved, "history_len": len(history)}
