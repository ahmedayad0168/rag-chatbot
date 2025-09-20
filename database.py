# modules
import sqlite3
from config import DB_PATH
import numpy as np
import json
# connection helper
def get_connection():
    return sqlite3.connect(DB_PATH)

# initialize database
def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            chunk_text TEXT,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id INTEGER,
            vector BLOB,
            FOREIGN KEY(chunk_id) REFERENCES chunks(id)
        )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(document_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_chunk ON embeddings(chunk_id)")

# save chunks + embeddings in bulk
def save_chunks(document_id, chunks, vectors):
    with get_connection() as conn:
        cur = conn.cursor()
        for chunk, vector in zip(chunks, vectors):
            cur.execute("INSERT INTO chunks (document_id, chunk_text) VALUES (?, ?)", (document_id, chunk))
            chunk_id = cur.lastrowid
            cur.execute(
                "INSERT INTO embeddings (chunk_id, vector) VALUES (?, ?)",
                (chunk_id, vector.astype(np.float32).tobytes())
            )

# get all chunks and vectors
def get_chunks_and_vectors():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.chunk_text, e.vector
            FROM chunks c
            JOIN embeddings e ON c.id = e.chunk_id
        """)
        rows = cur.fetchall()

    chunks = [text for text, _ in rows]
    vectors = [np.frombuffer(vec, dtype=np.float32) for _, vec in rows]
    return chunks, np.vstack(vectors) if vectors else np.array([])

# export database to JSON
def export_to_json(json_path="database.json"):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT d.file_path, c.chunk_text, e.vector
            FROM documents d
            JOIN chunks c ON d.id = c.document_id
            JOIN embeddings e ON c.id = e.chunk_id
        """)
        rows = cur.fetchall()

    data = [
        {
            "file_path": file_path,
            "chunk_text": chunk_text,
            "vector": np.frombuffer(vec, dtype=np.float32).tolist()
        }
        for file_path, chunk_text, vec in rows
    ]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"documents": data}, f, indent=2, ensure_ascii=False)

