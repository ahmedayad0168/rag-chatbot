# modules
from sqlalchemy import engine
import database
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME
from db_sqlserver import fetch_data, get_all_tables
from prompts import system_prompt
import pyttsx3
import speech_recognition as sr

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

    **Input format:**
    Document Context: {context_1}
    Database Query Result: {context_2} 
    User's Question: {question}

    **Output format:**
    [Clear, structured response using both sources]
    """

    try:
        response = gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error with Gemini API: {e}"


# ------------------------
# text to speech
# ------------------------
def text_to_speech(text):
    engine = pyttsx3.init()
    return engine.say(f"{text}") , engine.runAndWait()


# ------------------------
# speech to text
# ------------------------
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as src:
            print("Listening...")
            r.adjust_for_ambient_noise(src, duration=1)
            audio = r.listen(src, timeout=10)
            text = r.recognize_google(audio)
            print(f"You said: {text}")
    return text


