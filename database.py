import sqlite3
import numpy as np
from config import DB_PATH

# connect database
def get_connection():
    return sqlite3.connect(DB_PATH)

# initialize database
def init_db():
    conn = get_connection()
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

    conn.commit()
    conn.close()

# save chunks in bulk
def save_chunks(document_id, chunks, vectors):
    conn = get_connection()
    cur = conn.cursor()

    for chunk, vector in zip(chunks, vectors):
        cur.execute("INSERT INTO chunks (document_id, chunk_text) VALUES (?, ?)", (document_id, chunk))
        chunk_id = cur.lastrowid
        cur.execute("INSERT INTO embeddings (chunk_id, vector) VALUES (?, ?)",
                    (chunk_id, vector.astype(np.float32).tobytes()))

    conn.commit()
    conn.close()

def get_chunks_and_vectors():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT c.chunk_text, e.vector FROM chunks c JOIN embeddings e ON c.id = e.chunk_id")
    rows = cur.fetchall()
    conn.close()

    chunks, vectors = [], []
    for text, vec in rows:
        chunks.append(text)
        vectors.append(np.frombuffer(vec, dtype=np.float32))

    return chunks, np.array(vectors)
