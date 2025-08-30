import os
import numpy as np
import database
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME
import gradio as gr 

genai.configure(api_key=GEMINI_API_KEY)
model = SentenceTransformer(MODEL_NAME)

def search_context(query, top_k=3):
    try:
        chunks, vectors = database.get_chunks_and_vectors()
    except Exception as e:
        return []

    if not chunks:
        return []

    q_vec = model.encode([query])[0]
    scores = util.cos_sim(q_vec, vectors)[0].cpu().numpy()
    best_idx = scores.argsort()[-top_k:][::-1]
    return [chunks[i] for i in best_idx]

def ask_gemini(question):
    context_chunks = search_context(question, top_k=3)
    if not context_chunks:
        return "Database is empty. Please ingest documents first."

    context = "\n".join(context_chunks)
    prompt = f"""
    You are a helpful assistant. Answer the following question ONLY using the provided context.
    
    Context:
    {context}

    Question: {question}
    """

    try:
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error with Gemini API: {e}"

def rag_chat(message, history):
    return ask_gemini(message)

demo = gr.ChatInterface(
    fn=rag_chat,
    title=" RAG Chatbot with Gemini",
    description="Ask questions about your ingested documents."
)

if __name__ == "__main__":
    print("Chatbot ready! Type 'exit' to quit.\n")
    while True:
        q = input("You: ")
        if q.lower() == "exit":
            print("Bye!")
            break
        ans = ask_gemini(q)
        print("\nBot:", ans, "\n")
        demo.launch(share=True)
