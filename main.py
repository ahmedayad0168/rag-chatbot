# modules
import os
import numpy as np
import database
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME, CHUNK_SIZE
import gradio as gr
from ingest import ingest_file
import shutil
from db_sqlserver import fetch_data, get_all_tables
from prompts import system_prompt

# configure API
genai.configure(api_key=GEMINI_API_KEY)

# load models once
embedder = SentenceTransformer(MODEL_NAME)
gemini = genai.GenerativeModel("gemini-2.0-flash")

# ------------------------
# Search in DB
# ------------------------
def search_context(query, top_k=3):
    try:
        chunks, vectors = database.get_chunks_and_vectors()
    except Exception as e:
        print(f"[DB Error] {e}")
        return []

    if not chunks:
        return []

    q_vec = embedder.encode(query, convert_to_numpy=True)
    scores = util.cos_sim(q_vec, vectors)[0].cpu().numpy()
    best_idx = scores.argsort()[-top_k:][::-1]
    return [chunks[i] for i in best_idx]


# ------------------------
# Gemini QA
# ------------------------
def ask_gemini(question):
    # read all chunks from documents
    context_chunks = search_context(question, top_k=3)
    if not context_chunks:
        return "Database is empty. Please ingest documents first."

    context_1 = "\n".join(context_chunks)

    # select all from database
    tables = get_all_tables()
    documents = []

    for table in tables:
        try:
            df = fetch_data(f"SELECT * FROM {table}")
            if df.empty:
                continue

            # Convert each row to readable text
            for _, row in df.iterrows():
                row_text = f"{table}: " + ", ".join(
                    [f"{col}={row[col]}" for col in df.columns]
                )
                documents.append(row_text)
        except Exception as e:
            documents.append(f"Could not read table {table}: {e}")

    context_2 = '\n'.join(documents)
    prompt = f"""
    {system_prompt}

    Context:
    {context_1}

    Database content:
    {context_2}

    Question: {question}
    """

    try:
        response = gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error with Gemini API: {e}"


# ------------------------
# Ingest files
# ------------------------
def ingest_and_save(file_paths, uploaded_state):
    uploaded = uploaded_state or []
    if not file_paths:
        return gr.update(choices=uploaded or [""], value=None), "No file uploaded", uploaded

    if isinstance(file_paths, (list, tuple)):
        paths = file_paths
    else:
        paths = [file_paths]

    messages = []
    save_dir = "uploads"
    os.makedirs(save_dir, exist_ok=True)

    for p in paths:
        filename = os.path.basename(p)
        saved_path = os.path.join(save_dir, filename)

        try:
            if os.path.abspath(p) != os.path.abspath(saved_path):
                shutil.copy(p, saved_path)
        except Exception as e:
            messages.append(f"[copy error] {filename}: {e}")
            continue

        if filename not in uploaded:
            uploaded.append(filename)

        try:
            msg = ingest_file(saved_path, chunk_size=CHUNK_SIZE)
            messages.append(msg)
        except Exception as e:
            messages.append(f"[ingest error] {filename}: {e}")

    out_msg = "\n".join(messages) if messages else "Done"
    return gr.update(choices=uploaded or [""], value=None), out_msg, uploaded


# ------------------------
# Delete files
# ------------------------
def delete_file(selected_filename, uploaded_state):
    uploaded = uploaded_state or []
    if not selected_filename:
        return gr.update(choices=uploaded or [""], value=None), "No file selected", uploaded

    if selected_filename not in uploaded:
        return gr.update(choices=uploaded or [""], value=None), f"File not in list: {selected_filename}", uploaded

    file_path = os.path.join("uploads", selected_filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        return gr.update(choices=uploaded or [""], value=None), f"Error deleting file: {e}", uploaded

    uploaded = [f for f in uploaded if f != selected_filename]
    return gr.update(choices=uploaded or [""], value=None), f"Deleted: {selected_filename}", uploaded


# ------------------------
# Gradio UI
# ------------------------
def rag_chat(message, history):
    return ask_gemini(message)


with gr.Blocks() as demo:
    with gr.Tab("File Management"):
        with gr.Row():
            file_input = gr.File(label="Upload file(s)", type="filepath", file_count="multiple")
            ingest_btn = gr.Button("Ingest")
            file_list = gr.Dropdown(choices=[], label="Uploaded Files (select to delete)")
            delete_btn = gr.Button("Delete Selected")
            out = gr.Textbox(label="Output", interactive=False)

        uploaded_state = gr.State([])

        ingest_btn.click(
            fn=ingest_and_save,
            inputs=[file_input, uploaded_state],
            outputs=[file_list, out, uploaded_state],
            queue=True
        )

        delete_btn.click(
            fn=delete_file,
            inputs=[file_list, uploaded_state],
            outputs=[file_list, out, uploaded_state],
            queue=True
        )

    with gr.Tab("Chatbot"):
        gr.ChatInterface(
            fn=rag_chat,
            title="RAG Chatbot with Gemini",
            description="Ask questions about your ingested documents."
        )


if __name__ == "__main__":
    demo.launch()
