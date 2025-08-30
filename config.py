import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Database
DB_PATH = os.getenv("DB_PATH", "DataBase.db")

# Embedding model
MODEL_NAME = "BAAI/bge-m3"

# Chunk size default
CHUNK_SIZE = 200

