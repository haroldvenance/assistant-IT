import os
from dotenv import load_dotenv

load_dotenv()

# Clés et configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY manquante dans le fichier .env")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 jour

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/assistant.db")

# Modèles Groq disponibles
AVAILABLE_MODELS = {
    "llama-3.1-8b-instant": "Llama 3.1 8B (rapide)",
    "llama-3.3-70b-versatile": "Llama 3.3 70B (puissant)",
    "deepseek-r1-distill-llama-70b": "DeepSeek-R1 Distill 70B (raisonnement)"
}