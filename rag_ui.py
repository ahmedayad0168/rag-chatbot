# modules
import os
import shutil
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
        choices = [f"{i+1} 🔊 {h[1].strip().replace('\\n', ' ')[:80]}" for i, h in enumerate(history)]
        return history, "", history, gr.update(choices=choices, value=(choices[-1] if choices else None))

    # Get the textual response (no TTS here)
    response = rag_chat(message, history)
    history = history + [(message, response)]

    # Build choices for the "play" dropdown (indexed)
    choices = [f"{i+1} 🔊 {h[1].strip().replace('\\n', ' ')[:80]}" for i, h in enumerate(history)]

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
        idx = int(idx_str) - 1  # Adjust for 1-based indexing
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

def stop_audio():
    """Stop audio playback"""
    return None

def clear_chat(history_state):
    """Clear chat history"""
    return [], [], gr.update(choices=[], value=None)

# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.header {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 20px;
}
.chatbot {
    min-height: 400px;
    border-radius: 10px;
    border: 1px solid #ddd;
}
.textbox {
    border-radius: 8px;
}
.button {
    border-radius: 6px;
    font-weight: 500;
}
.tab {
    border-radius: 10px;
}
.control-panel {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e9ecef;
}
.file-manager {
    background: #f0f8ff;
    padding: 15px;
    border-radius: 10px;
}
"""

# ============================
# Improved Interface
# ============================
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    
    # Header
    gr.Markdown("""
    <div class="header">
        <h1>🎯 Smart RAG Chatbot</h1>
        <p>Upload documents, chat with AI, and listen to responses</p>
    </div>
    """)
    
    with gr.Tab("📁 File Management", elem_classes="tab"):
        gr.Markdown("### 📂 Upload and Manage Documents")
        
        with gr.Row():
            with gr.Column(scale=3):
                file_input = gr.File(
                    label="📤 Upload File(s)", 
                    type="filepath", 
                    file_count="multiple",
                    height=100
                )
                
                with gr.Row():
                    ingest_btn = gr.Button("🚀 Ingest Files", variant="primary", size="lg")
                    clear_files_btn = gr.Button("🗑️ Clear All", variant="secondary")
                
            with gr.Column(scale=2, elem_classes="file-manager"):
                gr.Markdown("**📋 Uploaded Files**")
                file_list = gr.Dropdown(
                    choices=[], 
                    label="Select file to delete",
                    interactive=True
                )
                
                with gr.Row():
                    delete_btn = gr.Button("❌ Delete Selected", variant="stop")
                    refresh_btn = gr.Button("🔄 Refresh List")
        
        output_status = gr.Textbox(
            label="📊 Status", 
            interactive=False,
            lines=2,
            max_lines=4
        )
        
        uploaded_state = gr.State([])

    with gr.Tab("💬 Chatbot", elem_classes="tab"):
        gr.Markdown("### 🤖 Chat with Your Documents")
        
        with gr.Row():
            with gr.Column(scale=3):
                # Chat interface
                chatbot = gr.Chatbot(
                    height=450, 
                    label="💭 Conversation",
                    show_copy_button=True,
                    bubble_full_width=False,
                    placeholder="Start chatting with the AI..."
                )
                
                # Message input with better layout
                with gr.Row():
                    msg = gr.Textbox(
                        label="💬 Your Message",
                        placeholder="Type your question here or use voice input...",
                        lines=2,
                        scale=4
                    )
                    send_btn = gr.Button("📤 Send", variant="primary", scale=1)
                
                # Control buttons row
                with gr.Row():
                    mic_btn = gr.Button("🎤 Voice Input", variant="secondary")
                    clear_chat_btn = gr.Button("🧹 Clear Chat", variant="secondary")
                    stop_audio_btn = gr.Button("⏹️ Stop Audio", variant="stop")
            
            with gr.Column(scale=1, elem_classes="control-panel"):
                gr.Markdown("### 🔊 Audio Controls")
                
                play_dropdown = gr.Dropdown(
                    label="🎵 Select Response to Play",
                    choices=[], 
                    value=None,
                    info="Choose a previous response to listen to"
                )
                
                with gr.Row():
                    play_btn = gr.Button("▶️ Play Selected", variant="primary")
                    refresh_audio_btn = gr.Button("🔄 Refresh List")
                
                audio_output = gr.Audio(
                    label="🎧 Audio Player",
                    type="filepath",
                    interactive=False,
                    show_download_button=True
                )
                
                gr.Markdown("---")
                gr.Markdown("### ℹ️ Session Info")
                session_info = gr.Textbox(
                    label="Status",
                    value="✅ Ready to chat",
                    interactive=False,
                    lines=2
                )

        # History state
        history_state = gr.State([])

    # ============================
    # Event Handlers
    # ============================

    # File Management Tab
    ingest_btn.click(
        fn=ingest_and_save,
        inputs=[file_input, uploaded_state],
        outputs=[file_list, output_status, uploaded_state]
    )

    delete_btn.click(
        fn=delete_file,
        inputs=[file_list, uploaded_state],
        outputs=[file_list, output_status, uploaded_state]
    )

    refresh_btn.click(
        fn=lambda x: gr.update(choices=x or [""]),
        inputs=[uploaded_state],
        outputs=[file_list]
    )

    clear_files_btn.click(
        fn=lambda: ([], gr.update(choices=[], value=None), "All files cleared"),
        outputs=[uploaded_state, file_list, output_status]
    )

    # Chatbot Tab
    send_btn.click(
        fn=handle_send,
        inputs=[msg, history_state],
        outputs=[chatbot, msg, history_state, play_dropdown]
    )

    msg.submit(
        fn=handle_send,
        inputs=[msg, history_state],
        outputs=[chatbot, msg, history_state, play_dropdown]
    )

    mic_btn.click(
        fn=speech_to_text,
        inputs=None,
        outputs=msg
    )

    play_btn.click(
        fn=play_selected,
        inputs=[play_dropdown, history_state],
        outputs=audio_output
    )

    stop_audio_btn.click(
        fn=stop_audio,
        outputs=audio_output
    )

    clear_chat_btn.click(
        fn=clear_chat,
        inputs=[history_state],
        outputs=[chatbot, history_state, play_dropdown]
    )

    refresh_audio_btn.click(
        fn=lambda hist: gr.update(choices=[f"{i+1} 🔊 {h[1].strip().replace('\\n', ' ')[:80]}" for i, h in enumerate(hist)] if hist else []),
        inputs=[history_state],
        outputs=[play_dropdown]
    )

# ============================
# Launch App
# ============================
if __name__ == "__main__":
    demo.launch()
