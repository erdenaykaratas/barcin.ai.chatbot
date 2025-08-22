# config.py
"""
Projenin tüm yapılandırma ayarlarını içerir.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Genel Ayarlar ---
APP_NAME = "Barçın AI Asistanı"
LOG_LEVEL = "INFO" # DEBUG, INFO, WARNING, ERROR, CRITICAL

# --- Dizin Ayarları ---
DATA_DIRECTORY = "company_data"
INDEX_PATH = "faiss_index.bin"
CHUNKS_PATH = "chunks.pkl"
USERS_DB_PATH = "users.json"

# --- Model Ayarları ---
EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
GENERATIVE_MODEL_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={os.getenv('GEMINI_API_KEY')}"

# --- API Anahtarları (os.getenv ile güvenli bir şekilde alınır) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_KEY")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

# --- Arama ve Cevap Ayarları ---
SIMILARITY_SEARCH_K = 8 # Benzerlik aramasında getirilecek chunk sayısı
CONTEXT_MAX_LENGTH = 4000 # Modele gönderilecek maksimum bağlam karakter sayısı