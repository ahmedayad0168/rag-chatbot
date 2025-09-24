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


# ------------------------
# Chatbot (no auto-TTS)
# ------------------------
def rag_chat(message: str, history: list):
    """Call your LLM / RAG function to get a textual reply."""
    return ask_gemini(message)

def handle_send(message: str, history_state: list):
    """
    When user sends a message:
    - call rag_chat -> get textual response
    - append to history
    - update the dropdown choices (one per bot reply) for playing audio on demand
    """
    history = history_state or []
    if not message or not message.strip():
        # Nothing to send
        choices = [f"{i} 🔊 {h[1].strip().replace('\\n', ' ')[:80]}" for i, h in enumerate(history)]
        return history, "", history, gr.update(choices=choices, value=(choices[-1] if choices else None))

    # Get the textual response (no TTS here)
    response = rag_chat(message, history)
    history = history + [(message, response)]

    # Build choices for the "play" dropdown (indexed)
    choices = [f"{i} 🔊 {h[1].strip().replace('\\n', ' ')[:80]}" for i, h in enumerate(history)]

    # Outputs: chatbot history, cleared input box, updated history state, updated dropdown choices
    return history, "", history, gr.update(choices=choices, value=choices[-1])

def play_selected(choice: str, history_state: list):
    """
    When user clicks Play:
    - parse selected index from dropdown choice
    - generate TTS for that specific bot reply (on-demand)
    - return audio file path to the Audio component
    """
    if not choice or not history_state:
        return None

    try:
        idx_str = str(choice).split(" ", 1)[0]
        idx = int(idx_str)
    except Exception:
        return None

    history = history_state or []
    if idx < 0 or idx >= len(history):
        return None

    bot_text = history[idx][1]
    if not bot_text:
        return None

    # Generate audio file (on-demand). text_to_speech should return a filepath (wav/mp3)
    audio_path = text_to_speech(bot_text)
    return audio_path


# ============================
# Interface
# ============================
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
        gr.Markdown("### RAG Chatbot ###")

        chatbot = gr.Chatbot(height=420, label="Conversation")
        msg = gr.Textbox(
            label="Your Message",
            placeholder="Type your question here...",
            lines=2
        )

        # Small row: Send + inline mic (emoji-style)
        with gr.Row():
            send_btn = gr.Button("Send", variant="primary")
            mic_btn = gr.Button("🎤")   # small mic button to fill textbox from speech
            # Play controls for listening to any past reply
            play_dropdown = gr.Dropdown(label="Select bot reply to play (🔊)", choices=[], value=None)
            play_btn = gr.Button("🔊 Play")

        # Audio output (shows generated audio file when you click Play)
        audio_output = gr.Audio(label="Audio Player (play when ready)", type="filepath")

        # History state
        history_state = gr.State([])

        # Send typed text -> update history (chatbot), clear msg, update history_state & play_dropdown
        send_btn.click(
            fn=handle_send,
            inputs=[msg, history_state],
            outputs=[chatbot, msg, history_state, play_dropdown]
        )

        # Microphone: fill textbox with recognized speech (does NOT auto-send, does not auto-play)
        mic_btn.click(
            fn=speech_to_text,
            inputs=None,
            outputs=msg
        )

        # Play selected bot reply's audio on demand
        play_btn.click(
            fn=play_selected,
            inputs=[play_dropdown, history_state],
            outputs=audio_output
        )
# ============================
# Launch App
# ============================
if __name__ == "__main__":
    demo.launch()