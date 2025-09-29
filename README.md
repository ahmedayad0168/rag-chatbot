# 🎯 Smart RAG Chatbot

A **Retrieval-Augmented Generation (RAG) chatbot** that combines:
- 📂 **Document ingestion** (PDF, PPTX, DOCX, TXT, CSV, XLSX, images with OCR)
- 🧠 **Embeddings & similarity search** (using `sentence-transformers`)
- 🤖 **LLM responses** (via Google Gemini API)
- 🗄️ **Hybrid database retrieval** (SQLite + SQL Server)
- 🎧 **Speech support** (speech-to-text and text-to-speech with Gradio UI)

---

## 🚀 Features
- Upload multiple document formats (PDF, PPTX, DOCX, TXT, CSV, Excel, images)
- Automatically extract text, chunk, embed, and store in SQLite
- Query knowledge base + SQL Server database simultaneously
- Generate answers using **Google Gemini**
- Gradio UI with:
  - File management (upload/delete/ingest)
  - Chat interface with memory
  - On-demand audio playback of bot responses
  - Voice input and TTS support

---

## 📦 Installation

Clone the repository:
```bash
git clone https://github.com/ahmedayad0168/rag-chatbot.git
cd rag-chatbot
````

Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
DB_PATH=DataBase.db
```

Update `db_sqlserver.py` with your SQL Server connection string if needed.

---

## ▶️ Usage

Run the Gradio interface:

```bash
python rag_ui.py
```

This will open a local Gradio app in your browser where you can:

* Upload files
* Chat with the AI
* Play bot responses as audio
* Use voice input

---

## 📁 Project Structure

```
rag-chatbot/
│── rag_ui.py         # Gradio interface
│── main.py           # Core RAG logic, Gemini, TTS, STT
│── ingest.py         # Document parsing + embeddings + ingestion
│── database.py       # SQLite storage (chunks + embeddings)
│── db_sqlserver.py   # SQL Server queries
│── prompts.py        # System prompt for Gemini
│── config.py         # Config loader (dotenv)
│── .env              # API keys & DB path (user-provided)
│── requirements.txt  # Dependencies
```

---

## 🛠 Dependencies

* `gradio`
* `python-dotenv`
* `sentence-transformers`
* `google-generativeai`
* `pyttsx3`
* `speechrecognition`
* `PyPDF2`
* `python-pptx`
* `python-docx`
* `pandas`
* `pillow`
* `pytesseract`
* `pyodbc`
* `sqlite3` (built-in)

---
