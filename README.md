# 📚 RAG Chatbot with Gemini & BAAI Embeddings

A **Retrieval-Augmented Generation (RAG)** chatbot that uses:
- **BAAI/bge-m3** for embeddings  
- **Google Gemini API** for answer generation  
- **SQLite** for document storage and semantic search  

This project allows you to turn your **PDFs** and **PPTXs** into a context-aware assistant!  

---

## 🚀 Features

- 📂 Ingest `.pdf` and `.pptx` documents  
- ✂️ Automatic text chunking for embeddings  
- 🔎 Semantic search with **BAAI/bge-m3**  
- 🤖 Context-aware responses powered by **Gemini API**  
- 💾 Storage in lightweight **SQLite** database  
- 📤 Optional export of data to `.json`  

---

## ⚙️ Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ahmedayad0168/rag-chatbot.git
cd rag-chatbot
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Make sure you also have PyTorch installed for `sentence-transformers`.)*

### 4. Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DB_PATH=E:/my_projects/rag-chatbot/DataBase.db
```

⚠️ Add `.env` to `.gitignore` to keep your API key safe.

---

## 📖 Usage

### Step 1 — Ingest Documents
Edit `file_path` in **`ingest.py`**:
```python
file_path = r"E:/my projects/documents/MyDoc.pptx"
```
Run:
```bash
python ingest.py
```
This creates the database and saves embeddings.

---

### Step 2 — Start the Chatbot
**Option A — Terminal**
```bash
python chatbot.py
```
Example:
```
Chatbot ready! Type 'exit' to quit.

You: What is data science?
Bot: Data science is the field that combines ...
```

**Option B — Web UI (Gradio)**
If you add Gradio to `chatbot.py`, run:
```bash
python chatbot.py
```
Open the provided link in your browser to chat interactively.

---

### Step 3 — Export Database to JSON (Optional)
```python
import database
database.export_to_json("database.json")
```

This creates a `.json` file containing all chunks and embeddings.

---

## 📂 Project Structure

```
rag-chatbot/
│── chatbot.py         # Chatbot interface (CLI/Gradio UI)
│── ingest.py          # Document ingestion pipeline
│── database.py        # SQLite + JSON export
│── config.py          # Loads environment variables
│── requirements.txt   # Dependencies
│── README.md          # Project description
│── .env               # API key & DB path (ignored in git)
│── DataBase.db        # SQLite database (auto-created)
│── database.json      # Optional JSON export
```

---

## 🔮 Future Improvements

- Ingest all files in a folder automatically  
- Add support for `.docx` and `.txt`  
- Replace SQLite with **FAISS** or **pgvector** for large-scale search  
- Smarter chunking (by sentences/sections)  
- Full Gradio UI with **file upload + chat**  

---

## ⚠️ Notes

- Don’t upload `.env` (contains API key)  
- Large PDFs/PPTXs may take time to ingest  
- Make sure you use a valid Gemini model (`gemini-1.5-flash` recommended)  

---

## 👨‍💻 Author

Built with by **Ahmed Ayad**  
👉 [GitHub Profile](https://github.com/ahmedayad0168)
