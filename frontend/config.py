"""Configuration du frontend Streamlit."""

API_BASE_URL = "http://localhost:8000"

# Modèles disponibles (affichage -> identifiant API)
MODEL_CHOICES = {
    "Llama 3.1 8B (fast)": "llama-3.1-8b-instant",
    "Llama 3.3 70B (powerful)": "llama-3.3-70b-versatile",
    "DeepSeek-R1 Distill 70B (reasoning)": "deepseek-r1-distill-llama-70b"
}

# Formats d'export supportés
EXPORT_FORMATS = ["markdown", "html", "pdf"]