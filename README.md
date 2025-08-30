# 📚 RAG Chatbot with Gemini & BAAI Embeddings

This project is a **Retrieval-Augmented Generation (RAG) chatbot**.
It uses **BAAI/bge-m3** embeddings for semantic search and **Google Gemini** for generating answers.
Documents (PDF & PPTX) are ingested into a **SQLite database**, then retrieved to answer user questions.

---

## ⚡ Features

* 📂 Ingest PDF and PPTX documents.
* ✂️ Automatically chunks text into smaller pieces for embedding.
* 🔎 Semantic search using **BAAI/bge-m3** embeddings.
* 🤖 Context-aware answers powered by **Gemini API**.
* 💾 Stores everything in a lightweight **SQLite database**.

---

## 🛠️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # on Linux/Mac
venv\Scripts\activate      # on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

*(Make sure you have PyTorch installed for `sentence-transformers`)*

### 4. Environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_api_key
DB_PATH=E:/my projects/test/test/DataBase.db
```

⚠️ **Do not commit `.env` to GitHub**. Add it to `.gitignore`.

---

## 🚀 Usage

### Ingest documents

Run the ingestion script to add documents (PDF/PPTX) to the database:

```bash
python ingest.py
```

Edit the file path inside `ingest.py`:

```python
file_path = r"E:/my projects/documents/Data Science Methodology.pptx"
```

After ingestion, chunks and embeddings are saved into the database.

---

### Run the chatbot

```bash
python chatbot.py
```

Example:

```
Chatbot ready! Type 'exit' to quit.

You: what is data science
Bot: Data science is the field that combines ...
```

---

## 📂 Project Structure

```
project/
│── chatbot.py      # Chatbot logic (retrieval + Gemini)
│── ingest.py       # Ingest PDF/PPTX into database
│── database.py     # SQLite database functions
│── config.py       # Configuration (loads .env)
│── requirements.txt
│── .env            # Environment variables (not in repo)
│── DataBase.db     # SQLite database (created automatically)
```

---

## 📦 Requirements

* Python 3.9+
* [sentence-transformers](https://www.sbert.net/)
* [PyPDF2](https://pypi.org/project/pypdf2/)
* [python-pptx](https://python-pptx.readthedocs.io/)
* [google-generativeai](https://pypi.org/project/google-generativeai/)
* [numpy](https://numpy.org/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## 🔮 Future Improvements

* [ ] Add ingestion for `.docx` and `.txt` files.
* [ ] Support folder ingestion (all documents in a directory).
* [ ] Replace SQLite with **FAISS** or **pgvector** for scalability.
* [ ] Add a simple **Streamlit/Gradio UI** for chatbot interaction.

