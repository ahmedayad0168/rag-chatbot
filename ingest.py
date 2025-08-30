import os
from PyPDF2 import PdfReader
from pptx import Presentation
from sentence_transformers import SentenceTransformer
import database
from config import MODEL_NAME, CHUNK_SIZE

database.init_db()

model = SentenceTransformer(MODEL_NAME)

# read .pdf
def read_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

# read .pptx
def read_pptx(file_path):
    prs = Presentation(file_path)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "has_text_frame") and shape.has_text_frame:
                text += shape.text + "\n"
    return text

# chunks
def chunk_text(text, chunk_size=200):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# ingest file
def ingest_file(file_path, chunk_size=200):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = read_pdf(file_path)
    elif ext == ".pptx":
        text = read_pptx(file_path)
    else:
        raise ValueError("Unsupported file type!")

    chunks = chunk_text(text, chunk_size)
    if not chunks:
        print(f"No text found in {file_path}")
        return

    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO documents (file_path) VALUES (?)", (file_path,))
    conn.commit()
    cur.execute("SELECT id FROM documents WHERE file_path=?", (file_path,))
    document_id = cur.fetchone()[0]
    conn.close()

    vectors = model.encode(chunks, batch_size=32, show_progress_bar=True)
    database.save_chunks(document_id, chunks, vectors)

    print(f"{file_path} ingested with {len(chunks)} chunks.")

#    i = 1
#    for chunk in chunks:
#        print(f"chunk {i}: ")
#        print(chunk)
#        i += 1

if __name__ == "__main__":
    file_path = r"E:/my projects/documents/Data Science Methodology.pptx"
    ingest_file(file_path, chunk_size=150)
