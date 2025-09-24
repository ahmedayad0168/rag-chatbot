# modules
import os
import shutil
from typing import Tuple
import gradio as gr
from ingest import ingest_file
from config import CHUNK_SIZE
from Document_intelligence import text_to_speech, speech_to_text, ask_gemini


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


# ============================
# Helper Functions (audio)
# ============================
def rag_chat_with_audio(message: str, history: list) -> Tuple[str, list]:
    """Chatbot logic with audio icon."""
    # Call your rag_chat function to get response
    response = rag_chat(message, history)

    # Add small speaker icon next to chatbot text
    response_with_icon = f"{response} (click to listen)"
    
    return response_with_icon, history + [(message, response_with_icon)]

def play_audio(text: str):
    """Convert text to speech and return audio file path."""
    audio_path = text_to_speech(text)  # use your existing function
    return audio_path

# ============================
# Interface
# ============================
def rag_chat(message, history):
    return ask_gemini(message)

with gr.Blocks(theme=gr.themes.Soft()) as demo:
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
            outputs=[file_list, out, uploaded_state]
        )

        delete_btn.click(
            fn=delete_file,
            inputs=[file_list, uploaded_state],
            outputs=[file_list, out, uploaded_state]
        )

    with gr.Tab("Chatbot"):
        gr.Markdown("### RAG Chatbot (Type or Talk)")

        chatbot = gr.Chatbot(height=400)
        msg = gr.Textbox(label="Your Message", placeholder="Type or record your question...")
        with gr.Row():
            send_btn = gr.Button("Send")
            voice_btn = gr.Button("Speak")

        audio_output = gr.Audio(label="Chatbot Voice", type="filepath")

        # Text input
        send_btn.click(
            rag_chat_with_audio,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )

        # Voice input
        voice_btn.click(
            speech_to_text,
            inputs=None,
            outputs=msg
        )

        # Play audio when clicking speaker icon
        msg.change(
            fn=play_audio,
            inputs=msg,
            outputs=audio_output
        )

# ============================
# Launch App
# ============================
if __name__ == "__main__":
    demo.launch()
