"""RAG Ingestion - docs 10_RAG MinIO->PyMuPDF->chunk->FastEmbed->Qdrant + PG metadata."""
import os, uuid, json
from pathlib import Path
from typing import List
import psycopg
from minio import Minio
from app.rag.chunking import chunk_text, clean_text

def extract_text(filepath: Path) -> str:
    if filepath.suffix.lower() == ".pdf":
        import pymupdf
        doc = pymupdf.open(str(filepath))
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    elif filepath.suffix.lower() in [".txt", ".md"]:
        return filepath.read_text(encoding="utf-8", errors="ignore")
    elif filepath.suffix.lower() == ".docx":
        import docx
        d = docx.Document(str(filepath))
        return "\n".join([p.text for p in d.paragraphs])
    else:
        return filepath.read_text(encoding="utf-8", errors="ignore")

def ingest_knowledge(data_dir: str = "D:/Foram_TP/ORCA/data/knowledge"):
    """Full pipeline: MinIO raw -> extract -> chunk -> embed -> Qdrant + PG."""
    from fastembed import TextEmbedding
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct

    minio_client = Minio("localhost:9100", access_key="minioadmin", secret_key="minioadmin", secure=False)
    qdrant = QdrantClient(url="http://localhost:6333", check_compatibility=False)
    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()

    # Clear previous for idempotent re-ingest (keep collection)
    try:
        qdrant.delete_collection("orca_knowledge")
    except: pass
    from qdrant_client.models import VectorParams, Distance
    qdrant.create_collection(collection_name="orca_knowledge", vectors_config=VectorParams(size=384, distance=Distance.COSINE))
    cur.execute("DELETE FROM knowledge_chunks")
    cur.execute("DELETE FROM knowledge_documents")
    conn.commit()

    files = list(Path(data_dir).rglob("*.*"))
    files = [f for f in files if f.suffix.lower() in [".txt",".pdf",".md",".docx"] and f.is_file()]
    # Mumbai-only: prioritize Mumbai/Maharashtra docs, skip non-Mumbai if region filter strict
    total_chunks = 0
    for filepath in files:
        # 1. MinIO raw - tag Mumbai region in payload for Qdrant Mumbai filter
        is_mumbai = "mumbai" in str(filepath).lower() or "maharashtra" in str(filepath).lower() or filepath.parent.name.lower() in ["safety","marine_advisories","fisheries","regulations"]
        key = f"documents/{filepath.parent.name}/{filepath.name}"
        try:
            with open(filepath, "rb") as fh:
                data = fh.read()
                import io
                minio_client.put_object("orca-documents", key, io.BytesIO(data), len(data))
        except Exception as e:
            print(f"MinIO failed {filepath}: {e}")

        # 2. Extract
        raw_text = extract_text(filepath)
        if not raw_text or len(raw_text.strip()) < 20:
            continue
        # 3. Chunk
        chunks = chunk_text(raw_text, chunk_size=700, overlap=100)
        doc_id = str(uuid.uuid4())
        # PG document
        cur.execute("INSERT INTO knowledge_documents (id, title, source, document_type, object_storage_key, language, metadata) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (doc_id, filepath.stem, filepath.parent.name, filepath.suffix[1:], key, "en", json.dumps({"pages": 1, "chunks": len(chunks)})))
        # 4. Embed
        texts = [c["text"] for c in chunks]
        vectors = list(model.embed(texts))
        points = []
        for i, (ch, vec) in enumerate(zip(chunks, vectors)):
            chunk_id = str(uuid.uuid4())
            cur.execute("INSERT INTO knowledge_chunks (id, document_id, chunk_index, text, language, embedding_id, metadata) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (chunk_id, doc_id, ch["chunk_index"], ch["text"], "en", chunk_id, json.dumps({"chars": len(ch["text"])})))
            points.append(PointStruct(
                id=chunk_id,
                vector=vec,
                payload={
                    "document_id": doc_id,
                    "chunk_id": chunk_id,
                    "document": filepath.stem,
                    "title": filepath.stem,
                    "source": filepath.parent.name,
                    "text": ch["text"][:500],
                    "chunk_index": ch["chunk_index"],
                    "language": "en",
                    "object_key": key,
                    "region": "mumbai" if is_mumbai else "global"
                }
            ))
        qdrant.upsert(collection_name="orca_knowledge", points=points)
        total_chunks += len(chunks)
        print(f"Ingested {filepath.name}: {len(chunks)} chunks")
    conn.commit()
    cur.execute("SELECT count(*) FROM knowledge_documents"); docs = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM knowledge_chunks"); chunks = cur.fetchone()[0]
    qcount = qdrant.get_collection("orca_knowledge").points_count
    print(f"DONE docs={docs} chunks={chunks} qdrant={qcount} total_chunks={total_chunks}")
    return {"docs": docs, "chunks": chunks, "qdrant": qcount}

if __name__ == "__main__":
    ingest_knowledge()
